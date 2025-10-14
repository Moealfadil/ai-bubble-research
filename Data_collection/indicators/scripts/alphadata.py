import requests
import pandas as pd
import time
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# ==== CONFIG ====
# Load environment variables
load_dotenv()

# Get script directory for absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# Load API keys from environment variables
api_keys_str = os.getenv('ALPHA_VANTAGE_API_KEYS')
if not api_keys_str:
    print("❌ Error: ALPHA_VANTAGE_API_KEYS not found in environment variables")
    print("Please create a .env file with your API keys. See .env.example for format.")
    exit(1)

# Parse API keys from comma-separated string
API_KEYS = [key.strip() for key in api_keys_str.split(',') if key.strip()]
if not API_KEYS:
    print("❌ Error: No valid API keys found in ALPHA_VANTAGE_API_KEYS")
    exit(1)

print(f"✅ Loaded {len(API_KEYS)} API keys from environment variables")

# Load configuration from environment variables with defaults
START_YEAR = int(os.getenv('START_YEAR', '2015'))
END_YEAR = int(os.getenv('END_YEAR', '2025'))
RATE_LIMIT_DELAY = int(os.getenv('RATE_LIMIT_DELAY', '15'))  # seconds between API calls

OUTPUT_DIR = os.path.join(BASE_DIR, "alpha")
COMPANY_LIST_PATH = os.path.join(BASE_DIR, "..", "Tickers", "merged_tickers.csv")
# For international companies, use your existing complete_data_improved/ files
COMPLETE_DATA_DIR = os.path.join(BASE_DIR, "complete_data_improved")  # For market cap data

# Track API usage per key (4 calls per ticker, 25 calls per day per key = 6 tickers per key per day)
api_call_counts = {key: 0 for key in API_KEYS}
current_api_key_index = 0
CALLS_PER_KEY_LIMIT = 400  # Free tier daily limit
CALLS_PER_TICKER = 4  # Income Statement + Earnings + Balance Sheet + Cash Flow

# ==== CREATE OUTPUT DIRECTORY ====
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==== API KEY ROTATION ====
def get_current_api_key():
    """Get the current API key"""
    global current_api_key_index
    return API_KEYS[current_api_key_index]

def rotate_api_key():
    """Rotate to the next API key when limit is reached"""
    global current_api_key_index, api_call_counts
    
    current_key = API_KEYS[current_api_key_index]
    
    # If current key has reached limit, rotate to next
    if api_call_counts[current_key] >= CALLS_PER_KEY_LIMIT:
        current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)
        next_key = API_KEYS[current_api_key_index]
        
        # If next key is also at limit, we've exhausted all keys
        if api_call_counts[next_key] >= CALLS_PER_KEY_LIMIT:
            print("\n" + "="*60)
            print("⚠️  ALL API KEYS HAVE REACHED DAILY LIMIT (25 calls each)")
            print("="*60)
            print(f"Total API calls made: {sum(api_call_counts.values())}")
            print(f"Tickers completed: {sum(api_call_counts.values()) // 5}")
            print("\nOptions:")
            print("1. Wait 24 hours for limits to reset")
            print("2. Get more API keys")
            print("3. Upgrade to premium tier")
            print("\nProgress has been saved. Re-run the script tomorrow to continue.")
            print("="*60)
            return False
        
        print(f"\n🔄 Rotating API key: {current_key[:8]}... → {next_key[:8]}...")
        print(f"   Previous key used: {api_call_counts[current_key]} calls")
        print(f"   New key available: {CALLS_PER_KEY_LIMIT - api_call_counts[next_key]} calls remaining")
    
    return True

def increment_api_call():
    """Increment the call count for current key"""
    current_key = get_current_api_key()
    api_call_counts[current_key] += 1

def get_api_stats():
    """Get current API usage statistics"""
    stats = []
    for idx, key in enumerate(API_KEYS):
        is_current = (idx == current_api_key_index)
        marker = "→ " if is_current else "  "
        stats.append(f"{marker}Key {idx+1} ({key[:8]}...): {api_call_counts[key]}/{CALLS_PER_KEY_LIMIT} calls")
    return "\n".join(stats)

# ==== LOAD COMPANY LIST ====
def load_company_list():
    """Load company tickers from CSV"""
    df = pd.read_csv(COMPANY_LIST_PATH)
    # Filter out empty rows
    df = df[df['Ticker'].notna()]
    return df['Ticker'].tolist()

def load_market_cap_by_quarter(ticker):
    """Load market cap data grouped by year and quarter from existing complete_data_improved CSV files"""
    try:
        # Convert ticker format for filename (e.g., "000660 KS" -> "000660_KS")
        clean_ticker = ticker.replace(' ', '_').replace('/', '_')
        file_path = os.path.join(COMPLETE_DATA_DIR, f"{clean_ticker}_complete.csv")
        
        if not os.path.exists(file_path):
            print(f"  ⚠️  Market cap file not found: {file_path}")
            return None
        
        # Load the CSV
        df = pd.read_csv(file_path)
        
        if 'year' not in df.columns or 'quarter' not in df.columns or 'market_cap' not in df.columns:
            print(f"  ⚠️  Missing year, quarter, or market_cap columns")
            return None
        
        # Group by year and quarter, take the median market cap for each quarter
        # (median is more robust to outliers than mean)
        quarterly_market_cap = df.groupby(['year', 'quarter'])['market_cap'].median().reset_index()
        quarterly_market_cap = quarterly_market_cap[quarterly_market_cap['market_cap'].notna()]
        
        if len(quarterly_market_cap) > 0:
            quarters = len(quarterly_market_cap)
            year_range = f"{quarterly_market_cap['year'].min()}-{quarterly_market_cap['year'].max()}"
            print(f"  ✅ Loaded {quarters} quarters of market cap data ({year_range})")
            return quarterly_market_cap
        
        print(f"  ⚠️  No valid market cap data")
        return None
        
    except Exception as e:
        print(f"  ⚠️  Error loading market cap: {str(e)}")
        return None

# ==== API FETCH FUNCTIONS ====
def fetch_income_statement(ticker):
    """Fetch quarterly income statement data"""
    print(f"  Fetching income statement...")
    api_key = get_current_api_key()
    url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    increment_api_call()
    
    # Check for API errors or limitations
    if "Note" in data:
        print(f"  ⚠️  API message: {data['Note']}")
        return []
    if "Error Message" in data:
        print(f"  ⚠️  API error: {data['Error Message']}")
        return []
    if "Information" in data:
        print(f"  ⚠️  API info: {data['Information']}")
        return []
    
    if "quarterlyReports" in data:
        reports = data["quarterlyReports"]
        if not reports:
            print(f"  ⚠️  No quarterly reports available for {ticker}")
            return []
        # Filter by year range
        filtered = [
            r for r in reports
            if START_YEAR <= int(r.get("fiscalDateEnding", "0000").split("-")[0]) <= END_YEAR
        ]
        if not filtered:
            print(f"  ⚠️  No data in year range {START_YEAR}-{END_YEAR}")
        return filtered
    else:
        print(f"  ⚠️  No 'quarterlyReports' field in response")
    return []

def fetch_earnings(ticker):
    """Fetch quarterly earnings data"""
    print(f"  Fetching earnings...")
    api_key = get_current_api_key()
    url = f"https://www.alphavantage.co/query?function=EARNINGS&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    increment_api_call()
    
    if "quarterlyEarnings" in data:
        reports = data["quarterlyEarnings"]
        # Filter by year range
        filtered = [
            r for r in reports
            if START_YEAR <= int(r.get("fiscalDateEnding", "0000").split("-")[0]) <= END_YEAR
        ]
        return filtered
    return []

def fetch_balance_sheet(ticker):
    """Fetch quarterly balance sheet data"""
    print(f"  Fetching balance sheet...")
    api_key = get_current_api_key()
    url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    increment_api_call()
    
    if "quarterlyReports" in data:
        reports = data["quarterlyReports"]
        # Filter by year range
        filtered = [
            r for r in reports
            if START_YEAR <= int(r.get("fiscalDateEnding", "0000").split("-")[0]) <= END_YEAR
        ]
        return filtered
    return []

def fetch_cash_flow(ticker):
    """Fetch quarterly cash flow data"""
    print(f"  Fetching cash flow...")
    api_key = get_current_api_key()
    url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    increment_api_call()
    
    if "quarterlyReports" in data:
        reports = data["quarterlyReports"]
        # Filter by year range
        filtered = [
            r for r in reports
            if START_YEAR <= int(r.get("fiscalDateEnding", "0000").split("-")[0]) <= END_YEAR
        ]
        return filtered
    return []

# def fetch_company_overview(ticker):
#     """Fetch company overview for market cap"""
#     print(f"  Fetching company overview...")
#     api_key = get_current_api_key()
#     url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
#     response = requests.get(url)
#     data = response.json()
#     increment_api_call()
#     return data

# ==== DATA PROCESSING ====
def extract_income_statement_data(reports):
    """Extract relevant fields from income statement"""
    extracted = []
    for r in reports:
        extracted.append({
            'fiscalDateEnding': r.get('fiscalDateEnding'),
            'totalRevenue': r.get('totalRevenue'),
            'grossProfit': r.get('grossProfit'),
            'operatingIncome': r.get('operatingIncome'),
            'researchAndDevelopment': r.get('researchAndDevelopment'),
            'operatingExpenses': r.get('operatingExpenses'),
            'netIncome': r.get('netIncome'),
            'ebit': r.get('ebit'),
            'ebitda': r.get('ebitda'),
            'depreciationAndAmortization': r.get('depreciationAndAmortization')
        })
    return pd.DataFrame(extracted)

def extract_earnings_data(reports):
    """Extract relevant fields from earnings"""
    extracted = []
    for r in reports:
        extracted.append({
            'fiscalDateEnding': r.get('fiscalDateEnding'),
            'reportedEPS': r.get('reportedEPS'),
            'estimatedEPS': r.get('estimatedEPS'),
            'surprise': r.get('surprise'),
            'surprisePercentage': r.get('surprisePercentage')
        })
    return pd.DataFrame(extracted)

def extract_balance_sheet_data(reports):
    """Extract relevant fields from balance sheet"""
    extracted = []
    for r in reports:
        extracted.append({
            'fiscalDateEnding': r.get('fiscalDateEnding'),
            'totalAssets': r.get('totalAssets'),
            'totalLiabilities': r.get('totalLiabilities'),
            'cashAndCashEquivalentsAtCarryingValue': r.get('cashAndCashEquivalentsAtCarryingValue'),
            'shortTermDebt': r.get('shortTermDebt'),
            'longTermDebt': r.get('longTermDebt'),
            'totalShareholderEquity': r.get('totalShareholderEquity'),
            'retainedEarnings': r.get('retainedEarnings'),
            'commonStockSharesOutstanding': r.get('commonStockSharesOutstanding'),
            'currentNetReceivables': r.get('currentNetReceivables'),
            'inventory': r.get('inventory'),
            'currentAccountsPayable': r.get('currentAccountsPayable')
        })
    return pd.DataFrame(extracted)

def extract_cash_flow_data(reports):
    """Extract relevant fields from cash flow"""
    extracted = []
    for r in reports:
        extracted.append({
            'fiscalDateEnding': r.get('fiscalDateEnding'),
            'operatingCashflow': r.get('operatingCashflow'),
            'capitalExpenditures': r.get('capitalExpenditures'),
            'dividendPayout': r.get('dividendPayout'),
            'proceedsFromRepurchaseOfEquity': r.get('proceedsFromRepurchaseOfEquity'),
            'cashflowNetIncome': r.get('netIncome')  # Rename to avoid collision
        })
    return pd.DataFrame(extracted)

# ==== MERGE DATA ====
def merge_all_data(income_df, earnings_df, balance_df, cashflow_df):
    """Merge all dataframes on fiscalDateEnding - handles partial data"""
    
    # Find the first non-empty dataframe to use as base
    base_df = None
    for df in [income_df, earnings_df, balance_df, cashflow_df]:
        if not df.empty:
            base_df = df.copy()
            break
    
    # If all dataframes are empty, return empty dataframe
    if base_df is None:
        return pd.DataFrame()
    
    # Start with the base (first non-empty dataframe)
    merged = base_df
    
    # Merge remaining dataframes using outer join to keep all dates
    # (outer join ensures we don't lose data if dates don't perfectly match)
    for df, name in [(income_df, 'income'), (earnings_df, 'earnings'), 
                     (balance_df, 'balance'), (cashflow_df, 'cashflow')]:
        if not df.empty and not df.equals(base_df):
            # Use outer join to preserve all fiscal dates from both dataframes
            merged = merged.merge(df, on='fiscalDateEnding', how='outer')
    
    # Sort by date (newest first)
    if 'fiscalDateEnding' in merged.columns:
        merged = merged.sort_values('fiscalDateEnding', ascending=False)
    
    return merged

# ==== CALCULATE METRICS ====
def calculate_metrics(df, market_cap=None):
    """Calculate all required financial metrics with quarter-matched market cap
    
    Args:
        df: DataFrame with financial data and fiscalDateEnding column
        market_cap: DataFrame with 'year', 'quarter', and 'market_cap' columns for quarter matching,
                   or None if market cap data is unavailable
    """
    df = df.copy()
    
    # Save ticker if it exists
    ticker_value = None
    if 'ticker' in df.columns:
        ticker_value = df['ticker'].iloc[0] if len(df) > 0 else None
    
    # Convert all numeric columns
    numeric_cols = [col for col in df.columns if col not in ['fiscalDateEnding', 'ticker']]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Sort by date to calculate growth metrics
    df = df.sort_values('fiscalDateEnding', ascending=True)
    
    # 1. Revenue Growth (%)
    df['revenueGrowthPct'] = df['totalRevenue'].pct_change() * 100
    
    # 2. Net Income Margin (%)
    df['netIncomeMarginPct'] = (df['netIncome'] / df['totalRevenue']) * 100
    
    # 3. EPS Surprise (%) - only if earnings data available
    if 'reportedEPS' in df.columns and 'estimatedEPS' in df.columns:
        df['epsSurprisePct'] = ((df['reportedEPS'] - df['estimatedEPS']) / df['estimatedEPS'].abs()) * 100
    else:
        df['epsSurprisePct'] = None
    
    # 4. Free Cash Flow (FCF) - only if cash flow data available
    if 'operatingCashflow' in df.columns and 'capitalExpenditures' in df.columns:
        df['freeCashFlow'] = df['operatingCashflow'] + df['capitalExpenditures']  # capEx is usually negative
    else:
        df['freeCashFlow'] = None
    
    # 5. Debt-to-Equity Ratio - only if balance sheet data available
    if 'totalLiabilities' in df.columns and 'totalShareholderEquity' in df.columns:
        df['debtToEquityRatio'] = df['totalLiabilities'] / df['totalShareholderEquity']
    else:
        df['debtToEquityRatio'] = None
    
    # 6. Cash Ratio - only if balance sheet data available
    # Note: Current liabilities not directly available, using total liabilities as proxy
    if 'shortTermDebt' in df.columns and 'longTermDebt' in df.columns:
        df['totalDebt'] = df['shortTermDebt'].fillna(0) + df['longTermDebt'].fillna(0)
    else:
        df['totalDebt'] = None
    
    if 'cashAndCashEquivalentsAtCarryingValue' in df.columns and 'shortTermDebt' in df.columns:
        df['cashRatio'] = df['cashAndCashEquivalentsAtCarryingValue'] / df['shortTermDebt']
    else:
        df['cashRatio'] = None
    
    # 7. R&D Intensity - only if income statement data available
    if 'researchAndDevelopment' in df.columns and 'totalRevenue' in df.columns:
        df['rdIntensityPct'] = (df['researchAndDevelopment'] / df['totalRevenue']) * 100
    else:
        df['rdIntensityPct'] = None
    
    # 8. Buyback Ratio - only if cash flow and income statement data available
    if 'proceedsFromRepurchaseOfEquity' in df.columns and 'netIncome' in df.columns:
        df['buybackRatio'] = -df['proceedsFromRepurchaseOfEquity'] / df['netIncome']
    else:
        df['buybackRatio'] = None
    
    # 9. P/E and P/S Ratios (requires market cap matched by quarter)
    if market_cap is not None and isinstance(market_cap, pd.DataFrame) and not market_cap.empty:
        # Extract year and quarter from fiscalDateEnding
        df['fiscalDate'] = pd.to_datetime(df['fiscalDateEnding'])
        df['fiscal_year'] = df['fiscalDate'].dt.year
        df['fiscal_quarter'] = df['fiscalDate'].dt.quarter
        
        # Merge market cap data by year and quarter
        df = df.merge(
            market_cap[['year', 'quarter', 'market_cap']],
            left_on=['fiscal_year', 'fiscal_quarter'],
            right_on=['year', 'quarter'],
            how='left'
        )
        
        # Rename and clean up
        df.rename(columns={'market_cap': 'marketCap'}, inplace=True)
        df.drop(['fiscalDate', 'fiscal_year', 'fiscal_quarter', 'year', 'quarter'], axis=1, inplace=True, errors='ignore')
        
        # Calculate ratios using quarter-matched market cap
        df['peRatio'] = df['marketCap'] / df['netIncome']
        df['psRatio'] = df['marketCap'] / df['totalRevenue']
    else:
        df['marketCap'] = None
        df['peRatio'] = None
        df['psRatio'] = None
        
    # Sort back to newest first
    df = df.sort_values('fiscalDateEnding', ascending=False)
    
    # Restore ticker column if it existed
    if ticker_value is not None:
        if 'ticker' not in df.columns:
            df.insert(0, 'ticker', ticker_value)
        else:
            df['ticker'] = ticker_value
    
    return df

# ==== MAIN PROCESSING FUNCTION ====
def process_ticker(ticker):
    """Process a single ticker: fetch data, merge, calculate metrics, save"""
    print(f"\n{'='*60}")
    print(f"Processing {ticker}...")
    print(f"{'='*60}")
    
    # Check if we can continue with API calls
    if not rotate_api_key():
        return False  # All keys exhausted
    
    try:
        # Fetch all data with rate limiting
        income_reports = fetch_income_statement(ticker)
        time.sleep(RATE_LIMIT_DELAY)
        
        # Check and rotate key if needed
        if not rotate_api_key():
            return False
        
        earnings_reports = fetch_earnings(ticker)
        time.sleep(RATE_LIMIT_DELAY)
        
        if not rotate_api_key():
            return False
        
        balance_reports = fetch_balance_sheet(ticker)
        time.sleep(RATE_LIMIT_DELAY)
        
        if not rotate_api_key():
            return False
        
        cashflow_reports = fetch_cash_flow(ticker)
        time.sleep(RATE_LIMIT_DELAY)
        
        # No need to check rotation here - we're done with API calls (4 total)
        
        # Check if we have ANY data from any source
        has_data = bool(income_reports or earnings_reports or balance_reports or cashflow_reports)
        
        if not has_data:
            print(f"⚠️  No data available from any API endpoint for {ticker}, skipping...")
            return False
        
        # Extract data into dataframes (even if some are empty)
        income_df = extract_income_statement_data(income_reports) if income_reports else pd.DataFrame()
        earnings_df = extract_earnings_data(earnings_reports) if earnings_reports else pd.DataFrame()
        balance_df = extract_balance_sheet_data(balance_reports) if balance_reports else pd.DataFrame()
        cashflow_df = extract_cash_flow_data(cashflow_reports) if cashflow_reports else pd.DataFrame()
        
        # Check what data we have
        data_status = {
            'Income Statement': len(income_df) > 0,
            'Earnings': len(earnings_df) > 0,
            'Balance Sheet': len(balance_df) > 0,
            'Cash Flow': len(cashflow_df) > 0
        }
        available = [k for k, v in data_status.items() if v]
        missing = [k for k, v in data_status.items() if not v]
        
        if available:
            print(f"  📊 Available: {', '.join(available)}")
        if missing:
            print(f"  ⚠️  Missing: {', '.join(missing)} (will save partial data)")
        
        # Merge all data - handle case where we might only have some data sources
        merged_df = merge_all_data(income_df, earnings_df, balance_df, cashflow_df)
        
        # Check if we have any merged data
        if merged_df.empty:
            print(f"⚠️  No data could be merged for {ticker}, skipping...")
            return False
        
        # Add ticker column
        merged_df.insert(0, 'ticker', ticker)
        
        # Get market cap by quarter from existing data instead of API
        print(f"  Loading market cap by quarter from existing data...")
        market_cap_df = load_market_cap_by_quarter(ticker)
        
        # Calculate metrics (with quarter-matched market cap)
        try:
            final_df = calculate_metrics(merged_df, market_cap_df)
        except Exception as e:
            print(f"❌ Error calculating metrics for {ticker}: {e}")
            return False
        
        # Check that we have at least some data to save
        if len(final_df) == 0:
            print(f"⚠️  No valid quarters after processing {ticker}, skipping...")
            return False
        
        # Save to CSV
        # Clean ticker name for filename (replace special characters)
        clean_ticker = ticker.replace(' ', '_').replace('/', '_')
        output_path = os.path.join(OUTPUT_DIR, f"{clean_ticker}_alpha_data.csv")
        final_df.to_csv(output_path, index=False)
        
        # Show summary
        quarters_saved = len(final_df)
        date_range = f"{final_df['fiscalDateEnding'].min()} to {final_df['fiscalDateEnding'].max()}" if 'fiscalDateEnding' in final_df.columns else "N/A"
        print(f"✅ Successfully saved {quarters_saved} quarters ({date_range})")
        print(f"   Saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {ticker}: {str(e)}")
        return False

# ==== MAIN EXECUTION ====
def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("ALPHA VANTAGE DATA COLLECTION SCRIPT")
    print("="*60)
    print(f"Start Year: {START_YEAR}")
    print(f"End Year: {END_YEAR}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Rate Limit Delay: {RATE_LIMIT_DELAY}s between calls")
    print(f"\n🔑 API Keys: {len(API_KEYS)} keys loaded")
    print(f"📊 API Calls per ticker: {CALLS_PER_TICKER} (no market cap call - using existing data)")
    print(f"📊 Daily Capacity: {len(API_KEYS) * (CALLS_PER_KEY_LIMIT // CALLS_PER_TICKER)} tickers per day")
    print(f"📊 Estimated Days: {160 // (len(API_KEYS) * (CALLS_PER_KEY_LIMIT // CALLS_PER_TICKER)) + 1} days for all 160 companies")
    print("="*60)
    
    # Load company list
    tickers = load_company_list()
    print(f"\n📊 Loaded {len(tickers)} tickers from {COMPANY_LIST_PATH}")
    
    # Filter out already processed tickers
    remaining_tickers = []
    for ticker in tickers:
        clean_ticker = ticker.replace(' ', '_').replace('/', '_')
        output_path = os.path.join(OUTPUT_DIR, f"{clean_ticker}_alpha_data.csv")
        if not os.path.exists(output_path):
            remaining_tickers.append(ticker)
    
    if len(remaining_tickers) < len(tickers):
        print(f"✅ Found {len(tickers) - len(remaining_tickers)} already processed")
        print(f"⏳ Remaining to process: {len(remaining_tickers)}")
    
    if not remaining_tickers:
        print("\n🎉 All tickers already processed!")
        return
    
    # Process each ticker
    success_count = 0
    fail_count = 0
    stopped_early = False
    
    start_time = datetime.now()
    
    for idx, ticker in enumerate(remaining_tickers, 1):
        print(f"\n[{idx}/{len(remaining_tickers)}] {ticker}")
        
        result = process_ticker(ticker)
        if result:
            success_count += 1
        elif result is False and sum(api_call_counts.values()) >= len(API_KEYS) * CALLS_PER_KEY_LIMIT:
            # All keys exhausted
            stopped_early = True
            break
        else:
            fail_count += 1
        
        # Show API usage stats every 5 tickers
        if idx % 5 == 0:
            print(f"\n📊 API Usage Status:")
            print(get_api_stats())
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    if stopped_early:
        print("COLLECTION PAUSED (API LIMITS REACHED)")
    else:
        print("COLLECTION COMPLETE")
    print("="*60)
    print(f"✅ Successfully processed: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"⏱️  Total time: {duration}")
    print(f"\n📊 Final API Usage:")
    print(get_api_stats())
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    
    if stopped_early:
        print(f"\n💡 To continue: Wait 24 hours and re-run the script")
        print(f"   Completed files are automatically skipped")
    
    print("="*60)

if __name__ == "__main__":
    main()

