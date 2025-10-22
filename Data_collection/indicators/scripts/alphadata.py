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

# Track API usage per key (5 calls per ticker, 400 calls per day per key = 80 tickers per key per day)
api_call_counts = {key: 0 for key in API_KEYS}
current_api_key_index = 0
CALLS_PER_KEY_LIMIT = 550  # Premium tier daily limit
CALLS_PER_TICKER = 5  # Income Statement + Earnings + Balance Sheet + Cash Flow + Historical Prices

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
            print("⚠️  ALL API KEYS HAVE REACHED DAILY LIMIT (400 calls each)")
            print("="*60)
            print(f"Total API calls made: {sum(api_call_counts.values())}")
            print(f"Tickers completed: {sum(api_call_counts.values()) // CALLS_PER_TICKER}")
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

def fetch_company_overview(ticker):
    """Fetch company overview for market cap"""
    print(f"  Fetching company overview...")
    api_key = get_current_api_key()
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    increment_api_call()
    
    # Check for API errors or limitations
    if "Note" in data:
        print(f"  ⚠️  API message: {data['Note']}")
        return None
    if "Error Message" in data:
        print(f"  ⚠️  API error: {data['Error Message']}")
        return None
    if "Information" in data:
        print(f"  ⚠️  API info: {data['Information']}")
        return None
    
    # Extract market cap from overview data
    market_cap = data.get('MarketCapitalization')
    if market_cap and market_cap != 'None':
        try:
            market_cap_value = float(market_cap)
            print(f"  ✅ Market cap: ${market_cap_value:,.0f}")
            return market_cap_value
        except (ValueError, TypeError):
            print(f"  ⚠️  Invalid market cap value: {market_cap}")
            return None
    else:
        print(f"  ⚠️  No market cap data available")
        return None

def fetch_historical_prices(ticker):
    """Fetch historical daily stock prices"""
    print(f"  Fetching historical prices...")
    api_key = get_current_api_key()
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    increment_api_call()
    
    # Check for API errors or limitations
    if "Note" in data:
        print(f"  ⚠️  API message: {data['Note']}")
        return None
    if "Error Message" in data:
        print(f"  ⚠️  API error: {data['Error Message']}")
        return None
    if "Information" in data:
        print(f"  ⚠️  API info: {data['Information']}")
        return None
    
    if "Time Series (Daily)" in data:
        time_series = data["Time Series (Daily)"]
        if not time_series:
            print(f"  ⚠️  No historical price data available for {ticker}")
            return None
        
        # Convert to DataFrame
        prices_df = pd.DataFrame.from_dict(time_series, orient='index')
        prices_df.index = pd.to_datetime(prices_df.index)
        prices_df.columns = ['open', 'high', 'low', 'close', 'volume']
        
        # Convert to numeric
        for col in prices_df.columns:
            prices_df[col] = pd.to_numeric(prices_df[col], errors='coerce')
        
        # Filter by year range
        prices_df = prices_df[(prices_df.index.year >= START_YEAR) & (prices_df.index.year <= END_YEAR)]
        
        if len(prices_df) > 0:
            print(f"  ✅ Loaded {len(prices_df)} days of price data ({prices_df.index.min().date()} to {prices_df.index.max().date()})")
            return prices_df
        else:
            print(f"  ⚠️  No price data in year range {START_YEAR}-{END_YEAR}")
            return None
    else:
        print(f"  ⚠️  No 'Time Series (Daily)' field in response")
        return None

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

# ==== HISTORICAL MARKET CAP CALCULATION ====
def calculate_historical_market_cap(financial_df, prices_df):
    """Calculate historical market cap using stock prices and shares outstanding
    
    Args:
        financial_df: DataFrame with financial data including fiscalDateEnding and commonStockSharesOutstanding
        prices_df: DataFrame with historical daily prices (index=date, columns=close, etc.)
    
    Returns:
        DataFrame with historical market cap data
    """
    if financial_df.empty or prices_df is None or prices_df.empty:
        return None
    
    # Create a copy to work with
    df = financial_df.copy()
    
    # Convert fiscalDateEnding to datetime
    df['fiscalDate'] = pd.to_datetime(df['fiscalDateEnding'])
    
    # Extract shares outstanding (in millions from Alpha Vantage)
    if 'commonStockSharesOutstanding' not in df.columns:
        print("  ⚠️  No shares outstanding data available")
        return None
    
    # Convert shares outstanding to numeric
    df['sharesOutstanding'] = pd.to_numeric(df['commonStockSharesOutstanding'], errors='coerce')
    
    # Remove rows where shares outstanding is missing
    df = df.dropna(subset=['sharesOutstanding'])
    
    if df.empty:
        print("  ⚠️  No valid shares outstanding data")
        return None
    
    # For each fiscal quarter, find the closest trading day and calculate market cap
    historical_market_caps = []
    
    for _, row in df.iterrows():
        fiscal_date = row['fiscalDate']
        shares_outstanding = row['sharesOutstanding']  # Already in millions
        
        # Find the closest trading day to the fiscal date
        # Look for trading days within 30 days after the fiscal date
        days_after_fiscal = prices_df.index - fiscal_date
        valid_days = days_after_fiscal[(days_after_fiscal >= pd.Timedelta(0)) & (days_after_fiscal <= pd.Timedelta(days=30))]
        
        if len(valid_days) > 0:
            # Get the first trading day after the fiscal date
            closest_date = fiscal_date + valid_days.min()
            closest_price = prices_df.loc[closest_date, 'close']
            
            # Calculate market cap (shares in millions, price per share)
            market_cap = shares_outstanding * closest_price  # Already in millions
            
            historical_market_caps.append({
                'fiscalDateEnding': row['fiscalDateEnding'],
                'marketCap': market_cap,
                'stockPrice': closest_price,
                'sharesOutstanding': shares_outstanding,
                'priceDate': closest_date.strftime('%Y-%m-%d')
            })
        else:
            # If no trading day found within 30 days, try to find the closest day before
            days_before_fiscal = fiscal_date - prices_df.index
            valid_days_before = days_before_fiscal[(days_before_fiscal >= pd.Timedelta(0)) & (days_before_fiscal <= pd.Timedelta(days=30))]
            
            if len(valid_days_before) > 0:
                closest_date = fiscal_date - valid_days_before.min()
                closest_price = prices_df.loc[closest_date, 'close']
                market_cap = shares_outstanding * closest_price
                
                historical_market_caps.append({
                    'fiscalDateEnding': row['fiscalDateEnding'],
                    'marketCap': market_cap,
                    'stockPrice': closest_price,
                    'sharesOutstanding': shares_outstanding,
                    'priceDate': closest_date.strftime('%Y-%m-%d')
                })
    
    if not historical_market_caps:
        print("  ⚠️  Could not calculate any historical market caps")
        return None
    
    # Convert to DataFrame
    market_cap_df = pd.DataFrame(historical_market_caps)
    
    print(f"  ✅ Calculated {len(market_cap_df)} quarters of historical market cap")
    return market_cap_df


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
        # Fetch income statement first to check if ticker exists in Alpha Vantage
        income_reports = fetch_income_statement(ticker)
        time.sleep(RATE_LIMIT_DELAY)
        
        # Check if income statement has data - if not, skip remaining API calls
        if not income_reports:
            print(f"⚠️  No income statement data available for {ticker}, skipping remaining API calls...")
            return False
        
        # Check and rotate key if needed
        if not rotate_api_key():
            return False
        
        # Continue with remaining API calls since we have data
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
        
        if not rotate_api_key():
            return False
        
        # Fetch historical prices for market cap calculation
        prices_df = fetch_historical_prices(ticker)
        time.sleep(RATE_LIMIT_DELAY)
        
        # No need to check rotation here - we're done with API calls (5 total)
        
        # Check if we have ANY data from any source (should be true since we have income_reports)
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
        
        # Calculate historical market cap using prices and shares outstanding
        print(f"  Calculating historical market cap...")
        historical_market_cap_df = calculate_historical_market_cap(merged_df, prices_df)
        
        # Merge historical market cap data directly into merged_df
        if historical_market_cap_df is not None and not historical_market_cap_df.empty:
            final_df = merged_df.merge(
                historical_market_cap_df[['fiscalDateEnding', 'marketCap', 'stockPrice', 'sharesOutstanding']],
                on='fiscalDateEnding',
                how='left'
            )
        else:
            final_df = merged_df
        
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
    print(f"📊 API Calls per ticker: {CALLS_PER_TICKER} (Income + Earnings + Balance + Cash Flow + Historical Prices)")
    print(f"📊 Daily Capacity: {len(API_KEYS) * (CALLS_PER_KEY_LIMIT // CALLS_PER_TICKER)} tickers per day")
    print(f"📊 Estimated Days: {160 // (len(API_KEYS) * (CALLS_PER_KEY_LIMIT // CALLS_PER_TICKER)) + 1} days for all 160 companies")
    print(f"💡 Optimization: International tickers with no data skip remaining 4 API calls")
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

