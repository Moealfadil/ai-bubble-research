"""
IMPROVED VERSION - Properly merges stock and financial data
Fixes: 
1. Stock metrics and financials now in same rows
2. Better user metrics extraction
3. Forward-fills quarterly data to monthly records
"""

import pandas as pd
import yfinance as yf
import requests
import re
import time
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

os.makedirs('../complete_data_improved', exist_ok=True)

SEC_HEADERS = {
    'User-Agent': 'AI Bubble Research 23701295@emu.edu.tr',
    'Accept-Encoding': 'gzip, deflate',
}

print(f"{'='*80}")
print(f"COMPLETE COLLECTION - All Companies")
print(f"{'='*80}")
print(f"Processing ALL companies from merged_tickers.csv")
print(f"Collecting: Stock data, Financials, User metrics, Ratios (2015-2025)")
print(f"{'='*80}\n")

df = pd.read_csv('../../Tickers/merged_tickers.csv')
# Filter out empty tickers
df = df[df['Ticker'].notna() & (df['Ticker'] != '')]
print(f"Total companies to process: {len(df)}\n")

def extract_user_numbers_improved(text, date_str=None):
    """Improved user extraction with better patterns"""
    user_metrics = {}
    
    # More comprehensive patterns
    patterns = {
        'mau': [
            r'(\d[\d,]*\.?\d*)\s*(?:million|M|billion|B)?\s+(?:monthly\s+active\s+users|MAU)',
            r'MAU[s]?.*?(\d[\d,]*\.?\d*)\s*(?:million|M|billion|B)',
            r'Monthly\s+Active\s+Users.*?(\d[\d,]*\.?\d*)\s*(?:million|M|billion|B)',
        ],
        'dau': [
            r'(\d[\d,]*\.?\d*)\s*(?:million|M|billion|B)?\s+(?:daily\s+active\s+users|DAU)',
            r'DAU[s]?.*?(\d[\d,]*\.?\d*)\s*(?:million|M|billion|B)',
            r'Daily\s+Active\s+Users.*?(\d[\d,]*\.?\d*)\s*(?:million|M|billion|B)',
        ],
        'subscribers': [
            r'(\d[\d,]*\.?\d*)\s*(?:million|M)?\s+(?:paid\s+)?(?:streaming\s+)?(?:subscribers?|memberships?)',
            r'(?:paid\s+)?(?:subscribers?|memberships?).*?(\d[\d,]*\.?\d*)\s*(?:million|M)',
            r'subscriber\s+base.*?(\d[\d,]*\.?\d*)\s*(?:million|M)',
        ],
        'active_riders': [
            r'(\d[\d,]*\.?\d*)\s*(?:million|M)?\s+active\s+(?:riders|drivers)',
        ],
        'merchants': [
            r'(\d[\d,]*\.?\d*)\s*(?:million|M|thousand|K)?\s+merchants',
        ],
    }
    
    for metric_type, pattern_list in patterns.items():
        for pattern in pattern_list:
            try:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    num_str = match.group(1).replace(',', '').strip()
                    if not num_str:
                        continue
                    
                    num_value = float(num_str)
                    
                    # Get context
                    context = text[max(0, match.start()-100):min(len(text), match.end()+100)]
                    
                    # Adjust for units
                    if 'billion' in context.lower() or ' B ' in context:
                        num_value *= 1000
                    elif 'thousand' in context.lower() or ' K ' in context:
                        num_value /= 1000
                    elif 'million' not in context.lower() and 'M ' not in context and num_value > 100:
                        # If no unit specified and number is large, assume millions
                        continue
                    
                    # Only store reasonable values
                    if 0.01 < num_value < 10000:  # Between 10k and 10 billion users
                        if metric_type not in user_metrics or num_value > user_metrics[metric_type]['value']:
                            user_metrics[metric_type] = {
                                'value': num_value,
                                'date': date_str,
                                'text': match.group(0)[:100]
                            }
            except Exception as e:
                continue
    
    return user_metrics

def collect_improved_data(ticker, name):
    """Collect and properly merge all data"""
    print(f"\n{'='*80}")
    print(f"Processing: {name} ({ticker})")
    print(f"{'='*80}")
    
    # Check if file already exists
    filename = f"../complete_data_improved/{ticker}_complete.csv"
    if os.path.exists(filename):
        print(f"  ⏭ Skipping {ticker} - data already exists")
        return None
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 1. Get monthly stock data
        print(f"  → Collecting monthly stock data (2015-present)...")
        hist = stock.history(start='2015-01-01', interval='1mo')
        
        if hist.empty:
            print(f"  ✗ No historical data")
            return None
        
        # Create base dataframe from monthly data
        df_monthly = pd.DataFrame({
            'date': hist.index,
            'close_price': hist['Close'].values,
            'open_price': hist['Open'].values,
            'high_price': hist['High'].values,
            'low_price': hist['Low'].values,
            'volume': hist['Volume'].values,
        })
        
        df_monthly['date'] = pd.to_datetime(df_monthly['date'])
        df_monthly['year'] = df_monthly['date'].dt.year
        df_monthly['quarter'] = df_monthly['date'].dt.quarter
        df_monthly['month'] = df_monthly['date'].dt.month
        df_monthly['year_quarter'] = df_monthly['year'].astype(str) + '-Q' + df_monthly['quarter'].astype(str)
        
        # Add shares and market cap
        shares = info.get('sharesOutstanding', None)
        df_monthly['shares_outstanding'] = shares
        if shares:
            df_monthly['market_cap'] = df_monthly['close_price'] * shares
            df_monthly['market_cap_billions'] = df_monthly['market_cap'] / 1e9
        
        print(f"    ✓ {len(df_monthly)} monthly records")
        
        # 2. Get quarterly financials
        print(f"  → Collecting quarterly financials...")
        quarterly = stock.quarterly_financials
        
        df_quarterly = pd.DataFrame()
        if quarterly is not None and not quarterly.empty:
            quarterly_data = []
            for date_col in quarterly.columns:
                if date_col.year < 2015:
                    continue
                
                qdata = {
                    'date': date_col,
                    'year': date_col.year,
                    'quarter': (date_col.month - 1) // 3 + 1,
                    'year_quarter': f"{date_col.year}-Q{(date_col.month-1)//3 + 1}",
                }
                
                if 'Total Revenue' in quarterly.index:
                    qdata['revenue'] = float(quarterly.loc['Total Revenue', date_col])
                if 'Gross Profit' in quarterly.index:
                    qdata['gross_profit'] = float(quarterly.loc['Gross Profit', date_col])
                if 'Net Income' in quarterly.index:
                    qdata['net_income'] = float(quarterly.loc['Net Income', date_col])
                if 'Operating Income' in quarterly.index:
                    qdata['operating_income'] = float(quarterly.loc['Operating Income', date_col])
                if 'EBITDA' in quarterly.index:
                    qdata['ebitda'] = float(quarterly.loc['EBITDA', date_col])
                
                quarterly_data.append(qdata)
            
            if quarterly_data:
                df_quarterly = pd.DataFrame(quarterly_data)
                print(f"    ✓ {len(df_quarterly)} quarterly reports")
        
        # 3. Merge quarterly data into monthly (forward fill within quarters)
        if not df_quarterly.empty:
            # Merge on year_quarter
            df_combined = df_monthly.merge(
                df_quarterly.drop(['date', 'year', 'quarter'], axis=1),
                on='year_quarter',
                how='left'
            )
        else:
            df_combined = df_monthly.copy()
            print(f"    ℹ No quarterly financials available")
        
        # Add current valuation ratios
        df_combined['current_pe'] = info.get('trailingPE')
        df_combined['forward_pe'] = info.get('forwardPE')
        df_combined['current_ps'] = info.get('priceToSalesTrailing12Months')
        df_combined['current_pb'] = info.get('priceToBook')
        df_combined['peg_ratio'] = info.get('pegRatio')
        
        # Calculate P/S ratio historically
        if 'revenue' in df_combined.columns and 'market_cap' in df_combined.columns:
            df_combined['ps_ratio'] = df_combined['market_cap'] / (df_combined['revenue'] * 4)
        
        # Calculate growth rates
        if 'revenue' in df_combined.columns:
            df_combined['revenue_millions'] = df_combined['revenue'] / 1e6
            df_combined['revenue_qoq_pct'] = df_combined['revenue'].pct_change() * 100
            df_combined['revenue_yoy_pct'] = df_combined['revenue'].pct_change(periods=4) * 100
        
        if 'market_cap' in df_combined.columns:
            df_combined['market_cap_yoy_pct'] = df_combined['market_cap'].pct_change(periods=12) * 100
        
        # 4. Search SEC for user metrics (for all US companies)
        print(f"  → Searching for user metrics...")
        user_metrics_found = {}
        
        try:
            # Check if it's a US ticker (no international exchange suffix)
            is_us = not any(x in ticker for x in ['HK', 'KS', 'GR', 'LN', 'JP', 'IM', 'SS', 'SW', 'NA', 'FH', 'FP', 'TT', 'CN', 'AU'])
            
            if is_us:  # Search SEC for all US companies
                search_url = f"https://www.sec.gov/cgi-bin/browse-edgar"
                params = {'action': 'getcompany', 'company': name, 'type': '10-K', 'count': '3'}
                response = requests.get(search_url, params=params, headers=SEC_HEADERS, timeout=10)
                time.sleep(0.3)
                
                cik_match = re.search(r'CIK=(\d+)', response.text)
                if cik_match:
                    cik = cik_match.group(1).zfill(10)
                    print(f"    Found CIK: {cik}")
                    
                    # Get recent filings
                    filings_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
                    filings_resp = requests.get(filings_url, headers=SEC_HEADERS, timeout=10)
                    time.sleep(0.3)
                    
                    if filings_resp.status_code == 200:
                        filings = filings_resp.json().get('filings', {}).get('recent', {})
                        forms = filings.get('form', [])
                        dates = filings.get('filingDate', [])
                        accessions = filings.get('accessionNumber', [])
                        
                        # Check 2 recent 10-Ks
                        checked = 0
                        for i in range(len(forms)):
                            if forms[i] == '10-K' and dates[i] >= '2022-01-01':
                                if checked >= 2:
                                    break
                                checked += 1
                                
                                print(f"      Checking 10-K from {dates[i]}...")
                                acc_clean = accessions[i].replace('-', '')
                                doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_clean}/{accessions[i]}.txt"
                                
                                try:
                                    doc_resp = requests.get(doc_url, headers=SEC_HEADERS, timeout=20)
                                    time.sleep(0.5)
                                    
                                    if doc_resp.status_code == 200:
                                        # Search in the document
                                        metrics = extract_user_numbers_improved(doc_resp.text[:1000000], dates[i])
                                        if metrics:
                                            print(f"        ✓ Found: {list(metrics.keys())}")
                                            user_metrics_found[dates[i]] = metrics
                                        else:
                                            print(f"        No user metrics in this filing")
                                except Exception as e:
                                    print(f"        Error: {e}")
            else:
                print(f"    ℹ Non-US company - skipping SEC search")
        except Exception as e:
            print(f"    SEC search error: {e}")
        
        # Add user metrics to dataframe
        if user_metrics_found:
            for filing_date, metrics in user_metrics_found.items():
                # Find the closest month to add the metrics
                filing_dt = pd.to_datetime(filing_date)
                
                for metric_type, metric_data in metrics.items():
                    col_name = f'user_{metric_type}_millions'
                    if col_name not in df_combined.columns:
                        df_combined[col_name] = None
                    
                    # Find rows in same year-quarter
                    mask = (df_combined['year'] == filing_dt.year) & (df_combined['quarter'] == (filing_dt.month-1)//3 + 1)
                    df_combined.loc[mask, col_name] = metric_data['value']
        
        # Add company metadata
        df_combined['company_name'] = name
        df_combined['ticker'] = ticker
        df_combined['sector'] = info.get('sector', 'N/A')
        df_combined['industry'] = info.get('industry', 'N/A')
        df_combined['country'] = info.get('country', 'N/A')
        df_combined['employees'] = info.get('fullTimeEmployees')
        
        # Reorder columns logically
        base_cols = ['ticker', 'company_name', 'date', 'year', 'quarter', 'month']
        stock_cols = ['close_price', 'open_price', 'high_price', 'low_price', 'volume', 'shares_outstanding', 'market_cap', 'market_cap_billions']
        financial_cols = ['revenue', 'revenue_millions', 'gross_profit', 'net_income', 'operating_income', 'ebitda']
        ratio_cols = ['ps_ratio', 'current_pe', 'forward_pe', 'current_ps', 'current_pb', 'peg_ratio']
        growth_cols = ['revenue_qoq_pct', 'revenue_yoy_pct', 'market_cap_yoy_pct']
        user_cols = [col for col in df_combined.columns if 'user_' in col]
        meta_cols = ['sector', 'industry', 'country', 'employees']
        
        col_order = []
        for col_list in [base_cols, stock_cols, financial_cols, ratio_cols, growth_cols, user_cols, meta_cols]:
            col_order.extend([c for c in col_list if c in df_combined.columns])
        
        # Add any remaining columns
        remaining = [c for c in df_combined.columns if c not in col_order]
        col_order.extend(remaining)
        
        df_combined = df_combined[col_order]
        
        # Save
        filename = f"../complete_data_improved/{ticker}_complete.csv"
        df_combined.to_csv(filename, index=False)
        
        print(f"  ✓ Saved: {filename}")
        print(f"    Records: {len(df_combined)}")
        print(f"    Date range: {df_combined['date'].min().strftime('%Y-%m-%d')} to {df_combined['date'].max().strftime('%Y-%m-%d')}")
        print(f"    Revenue records: {df_combined['revenue'].notna().sum()}")
        
        user_cols_found = [col for col in df_combined.columns if 'user_' in col]
        if user_cols_found:
            print(f"    ✓ USER METRICS:")
            for col in user_cols_found:
                vals = df_combined[col].dropna()
                if len(vals) > 0:
                    print(f"      {col}: {vals.iloc[-1]:.1f}M (in {len(vals)} records)")
        
        return {'ticker': ticker, 'name': name, 'records': len(df_combined), 'has_users': len(user_cols_found) > 0}
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Run on ALL companies
results = []
success_count = 0
failed_count = 0
companies_with_users = 0

for idx, row in df.iterrows():
    result = collect_improved_data(row['Ticker'], row['Name'])
    if result:
        results.append(result)
        success_count += 1
        if result['has_users']:
            companies_with_users += 1
    else:
        failed_count += 1
    
    # Rate limiting
    time.sleep(0.5)
    
    # Progress update every 10 companies
    if (idx + 1) % 10 == 0:
        print(f"\n{'='*80}")
        print(f"PROGRESS: {idx + 1}/{len(df)} companies processed")
        print(f"✓ Success: {success_count} | ✗ Failed: {failed_count} | 👥 With user metrics: {companies_with_users}")
        print(f"{'='*80}")

print(f"\n{'='*80}")
print(f"COMPLETE COLLECTION FINISHED!")
print(f"{'='*80}")

if results:
    summary = pd.DataFrame(results)
    summary_file = f"../complete_data_improved/FULL_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    summary.to_csv(summary_file, index=False)
    
    print(f"\n📊 Final Statistics:")
    print(f"  Total processed: {len(results)}")
    print(f"  ✓ Successful: {success_count}")
    print(f"  ✗ Failed: {failed_count}")
    print(f"  👥 Companies with user metrics: {companies_with_users}")
    print(f"\n📁 Output:")
    print(f"  Individual files: ../complete_data_improved/[TICKER]_complete.csv")
    print(f"  Summary: {summary_file}")
    
    # Create consolidated file
    print(f"\n📦 Creating consolidated dataset...")
    all_files = [f"../complete_data_improved/{f}" for f in os.listdir('../complete_data_improved') if f.endswith('_complete.csv')]
    
    if all_files:
        all_data = []
        for file in all_files:
            try:
                df_temp = pd.read_csv(file)
                all_data.append(df_temp)
            except Exception as e:
                print(f"  Error reading {file}: {e}")
        
        if all_data:
            consolidated = pd.concat(all_data, ignore_index=True)
            consolidated = consolidated.sort_values(['ticker', 'date'])
            consolidated_file = f"../complete_data_improved/ALL_COMPANIES_consolidated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            consolidated.to_csv(consolidated_file, index=False)
            
            print(f"  ✓ Consolidated file created: {consolidated_file}")
            print(f"    Total records: {len(consolidated):,}")
            print(f"    Companies: {consolidated['ticker'].nunique()}")
            print(f"    Date range: {consolidated['date'].min()} to {consolidated['date'].max()}")
            
            # Check for user metrics
            user_cols = [col for col in consolidated.columns if 'user_' in col]
            if user_cols:
                print(f"\n  👥 USER METRICS SUMMARY:")
                for col in user_cols:
                    companies_with_metric = consolidated[col].notna().sum()
                    unique_companies = consolidated[consolidated[col].notna()]['ticker'].nunique()
                    if companies_with_metric > 0:
                        print(f"    {col}: {companies_with_metric} data points across {unique_companies} companies")
    
print("\n✅ Done! All data collected with properly merged rows.")
print(f"⏱️  Collection completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
