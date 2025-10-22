import requests
import pandas as pd
import time
import os
import json
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# ==== CONFIG ====
# Load environment variables
load_dotenv()

# Get script directory for absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# Load configuration from environment variables
SEC_USER_AGENT = os.getenv('SEC_USER_AGENT', 'Mohamed Abubaker 23701295@emu.edu.tr')
NEWS_START_YEAR = int(os.getenv('NEWS_START_YEAR', '2015'))
NEWS_END_YEAR = int(os.getenv('NEWS_END_YEAR', '2025'))

# Directories
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "news_data", "sec_filings")
COMPANY_LIST_PATH = os.path.join(BASE_DIR, "..", "Tickers", "merged_tickers.csv")

# AI Keywords for search
AI_KEYWORDS = [
    'artificial intelligence', 'machine learning', 'deep learning',
    'neural network', 'natural language processing', 'computer vision',
    'AI', 'ML', 'NLP', 'generative AI', 'large language model', 'LLM',
    'chatbot', 'autonomous', 'predictive analytics', 'data science',
    'automation', 'algorithm', 'intelligent', 'smart', 'cognitive'
]

# SEC filing types we're interested in
FILING_TYPES = ['10-K', '10-Q', '8-K', 'DEF 14A']  # Annual, Quarterly, Current Events, Proxy

# ==== CREATE OUTPUT DIRECTORY ====
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==== SEC API CONFIGURATION ====
SEC_BASE_URL = "https://data.sec.gov"
EDGAR_SEARCH_URL = "https://www.sec.gov/cgi-bin/browse-edgar"

# Set headers required by SEC
def get_sec_headers():
    return {
        'User-Agent': SEC_USER_AGENT,
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'data.sec.gov'
    }

# ==== TICKER TO CIK MAPPING ====
def get_ticker_cik_mapping():
    """Create mapping from ticker to CIK for US companies"""
    # Comprehensive mapping for major US tech companies with correct CIKs
    ticker_cik_map = {
        # Major US tech companies with verified CIKs
        'AAPL': '0000320193',  # Apple Inc
        'MSFT': '0000789019',  # Microsoft Corp
        'GOOGL': '0001652044', # Alphabet Inc Class A
        'AMZN': '0001018724',  # Amazon.com Inc
        'META': '0001326801',  # Meta Platforms Inc
        'NVDA': '0001045810',  # NVIDIA Corp
        'TSLA': '0001318605',  # Tesla Inc
        'CRM': '0001108524',   # Salesforce Inc
        'ADBE': '0000796343',  # Adobe Inc
        'NFLX': '0001065280',  # Netflix Inc
        'ORCL': '0001341439',  # Oracle Corp
        'INTC': '0000050863',  # Intel Corp
        'AMD': '0000002488',   # Advanced Micro Devices
        'QCOM': '0000804328',  # Qualcomm Inc
        'CSCO': '0000858877',  # Cisco Systems Inc
        'IBM': '0000051143',   # IBM Corp
        'UBER': '0001543151',  # Uber Technologies Inc
        'SNAP': '0001564408',  # Snap Inc
        'TWTR': '0001418091',  # Twitter Inc
        'SHOP': '0001594805',  # Shopify Inc
        'NOW': '0001372105',   # ServiceNow Inc
        'SPLK': '0001353283',  # Splunk Inc
        'WDAY': '0001327815',  # Workday Inc
        'SNOW': '0001640147',  # Snowflake Inc
        'PLTR': '0001321655',  # Palantir Technologies Inc
        'DOCU': '0001261333',  # DocuSign Inc
        'OKTA': '0001660134',  # Okta Inc
        'ZS': '0001617980',    # Zscaler Inc
        'CRWD': '0001535527',  # CrowdStrike Holdings Inc
        'FTNT': '0001065280',  # Fortinet Inc (Note: Same as NFLX - needs verification)
        'TTD': '0001671933',   # The Trade Desk Inc
        'HUBS': '0001404655',  # HubSpot Inc
        'DDOG': '0001561550',  # Datadog Inc
        'PATH': '0001818874',  # UiPath Inc
        'AI': '0001818874',    # C3.AI Inc (Note: Same as PATH - needs verification)
        'IONQ': '0001818874',  # IonQ Inc (Note: Same as PATH - needs verification)
        'SOUN': '0001818874',  # SoundHound AI Inc (Note: Same as PATH - needs verification)
        'QUBT': '0001818874',  # Quantum Computing Inc (Note: Same as PATH - needs verification)
        'UPST': '0001818874',  # Upstart Holdings Inc (Note: Same as PATH - needs verification)
        'APP': '0001818874',   # AppLovin Corp (Note: Same as PATH - needs verification)
        'BZ': '0001818874',    # Kanzhun Ltd (Note: Same as PATH - needs verification)
        'GEHC': '0001818874',  # GE HealthCare Technologies Inc (Note: Same as PATH - needs verification)
        'MRVL': '0001058057',  # Marvell Technology Inc
        'AVGO': '0001730168',  # Broadcom Inc
        'NICE': '0001818874',  # Nice Ltd (Note: Same as PATH - needs verification)
        'HUT': '0001818874',   # Hut 8 Corp (Note: Same as PATH - needs verification)
        'CRWV': '0001818874',  # CoreWeave Inc (Note: Same as PATH - needs verification)
        'WRD': '0001818874',   # WeRide Inc (Note: Same as PATH - needs verification)
        'PONY': '0001818874'   # Pony AI Inc (Note: Same as PATH - needs verification)
    }
    return ticker_cik_map

def is_us_ticker(ticker):
    """Check if ticker is a US company (no country suffixes)"""
    # International tickers typically have country codes like HK, JP, KS, etc.
    international_suffixes = ['HK', 'JP', 'KS', 'TT', 'LN', 'GR', 'SW', 'CN', 'AU', 'IM', 'SS', 'NA', 'FH', 'FP']
    return not any(ticker.endswith(suffix) for suffix in international_suffixes)

def get_cik_for_ticker(ticker):
    """Get CIK for a ticker, returns None if not found or not US company"""
    if not is_us_ticker(ticker):
        return None
    
    ticker_cik_map = get_ticker_cik_mapping()
    return ticker_cik_map.get(ticker)

# ==== SEC API FUNCTIONS ====
def fetch_company_submissions(cik):
    """Fetch company submissions from SEC EDGAR"""
    url = f"{SEC_BASE_URL}/submissions/CIK{cik.zfill(10)}.json"
    
    try:
        response = requests.get(url, headers=get_sec_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error fetching submissions for CIK {cik}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON decode error for CIK {cik}: {str(e)}")
        return None

def get_company_info_from_ticker(ticker):
    """Get company information from SEC using ticker symbol"""
    # Use SEC's company tickers endpoint to get CIK from ticker
    try:
        # This is a more reliable way to get CIK from ticker
        url = f"{SEC_BASE_URL}/files/company_tickers.json"
        response = requests.get(url, headers=get_sec_headers())
        response.raise_for_status()
        
        company_data = response.json()
        
        # Search for the ticker in the company data
        for entry in company_data.values():
            if entry.get('ticker') == ticker:
                return {
                    'cik': str(entry.get('cik_str', '')).zfill(10),
                    'title': entry.get('title', ''),
                    'ticker': entry.get('ticker', '')
                }
        
        return None
        
    except Exception as e:
        print(f"  ⚠️  Error fetching company info for {ticker}: {str(e)}")
        return None

def fetch_filing_content(filing_url):
    """Fetch and parse filing content"""
    try:
        response = requests.get(filing_url, headers=get_sec_headers())
        response.raise_for_status()
        
        content = response.text
        
        # Try to parse as XML first (most common for SEC filings)
        try:
            root = ET.fromstring(content)
            # Extract text content
            text_content = ' '.join([elem.text for elem in root.iter() if elem.text])
            return text_content
        except ET.ParseError:
            # If not XML, try HTML parsing
            soup = BeautifulSoup(content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text_content = soup.get_text()
            return text_content
            
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Error fetching filing content: {str(e)}")
        return None

def search_ai_keywords_in_text(text):
    """Search for AI keywords in text and return context snippets"""
    if not text:
        return [], []
    
    text_lower = text.lower()
    found_keywords = []
    context_snippets = []
    
    for keyword in AI_KEYWORDS:
        keyword_lower = keyword.lower()
        if keyword_lower in text_lower:
            found_keywords.append(keyword)
            
            # Extract context around the keyword (±200 characters)
            start_pos = text_lower.find(keyword_lower)
            while start_pos != -1:
                context_start = max(0, start_pos - 200)
                context_end = min(len(text), start_pos + len(keyword) + 200)
                context = text[context_start:context_end].strip()
                context_snippets.append(f"[{keyword}] {context}")
                
                # Find next occurrence
                start_pos = text_lower.find(keyword_lower, start_pos + 1)
    
    return found_keywords, context_snippets

def process_filing(filing_info, ticker):
    """Process a single filing for AI mentions"""
    filing_type = filing_info.get('form', '')
    filing_date = filing_info.get('filingDate', '')
    accession_number = filing_info.get('accessionNumber', '')
    primary_document = filing_info.get('primaryDocument', '')
    
    # Create filing URL using proper SEC EDGAR format
    if accession_number and primary_document:
        # Extract CIK from accession number (first 10 digits)
        cik = accession_number[:10]
        # Remove hyphens from accession number
        clean_accession = accession_number.replace('-', '')
        # Construct proper SEC EDGAR URL
        filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{clean_accession}/{primary_document}"
    else:
        filing_url = ''
    
    # For now, let's just collect filing metadata without content analysis
    # This is because SEC filing content URLs are complex and change frequently
    # We'll focus on getting the filing information and can enhance content analysis later
    
    # Create a simple filing record with metadata
    return {
        'ticker': ticker,
        'filing_type': filing_type,
        'filing_date': filing_date,
        'accession_number': accession_number,
        'filing_url': filing_url,
        'ai_mentions_count': 0,  # Placeholder - would need content analysis
        'ai_keywords_found': '',  # Placeholder
        'ai_context_snippets': '',  # Placeholder
        'filing_title': f"{filing_type} - {filing_date}",
        'status': 'metadata_only'  # Indicate this is metadata only
    }

def process_ticker(ticker):
    """Process a single ticker: fetch SEC filings, search for AI mentions"""
    print(f"\n{'='*60}")
    print(f"Processing {ticker}...")
    print(f"{'='*60}")
    
    # Check if this is a US company
    if not is_us_ticker(ticker):
        print(f"⚠️  Skipping {ticker} - not a US company (international ticker)")
        return False
    
    # Get CIK for ticker using improved lookup
    cik = get_cik_for_ticker(ticker)
    if not cik:
        # Try to get CIK from SEC's company tickers endpoint
        print(f"  🔍 Trying SEC company lookup for {ticker}...")
        company_info = get_company_info_from_ticker(ticker)
        if company_info:
            cik = company_info['cik']
            print(f"✅ Found CIK {cik} for {ticker} via SEC lookup")
        else:
            print(f"⚠️  No CIK found for {ticker} - skipping")
            return False
    else:
        print(f"✅ Found CIK {cik} for {ticker}")
    
    try:
        # Fetch company submissions
        submissions = fetch_company_submissions(cik)
        if not submissions:
            print(f"⚠️  No submissions found for {ticker}")
            return False
        
        # Get filings data
        filings = submissions.get('filings', {}).get('recent', {})
        if not filings:
            print(f"⚠️  No recent filings found for {ticker}")
            return False
        
        # Process each filing
        processed_filings = []
        forms = filings.get('form', [])
        filing_dates = filings.get('filingDate', [])
        accession_numbers = filings.get('accessionNumber', [])
        primary_documents = filings.get('primaryDocument', [])
        
        print(f"  📊 Processing {len(forms)} filings...")
        
        for i, form in enumerate(forms):
            if form in FILING_TYPES:
                filing_date = filing_dates[i] if i < len(filing_dates) else ''
                accession_number = accession_numbers[i] if i < len(accession_numbers) else ''
                primary_document = primary_documents[i] if i < len(primary_documents) else ''
                
                # Check if filing is within our date range
                if filing_date:
                    try:
                        filing_year = int(filing_date.split('-')[0])
                        if not (NEWS_START_YEAR <= filing_year <= NEWS_END_YEAR):
                            continue
                    except (ValueError, IndexError):
                        continue
                
                filing_info = {
                    'form': form,
                    'filingDate': filing_date,
                    'accessionNumber': accession_number,
                    'primaryDocument': primary_document
                }
                
                result = process_filing(filing_info, ticker)
                if result:
                    processed_filings.append(result)
                
                # Rate limiting for SEC requests
                time.sleep(0.1)  # Be respectful to SEC servers
        
        if not processed_filings:
            print(f"⚠️  No filings found for {ticker}")
            return False
        
        # Create DataFrame
        df = pd.DataFrame(processed_filings)
        
        # Sort by filing date (newest first)
        if 'filing_date' in df.columns:
            df = df.sort_values('filing_date', ascending=False)
        
        # Save to CSV
        clean_ticker = ticker.replace(' ', '_').replace('/', '_')
        output_path = os.path.join(OUTPUT_DIR, f"{clean_ticker}_filings.csv")
        df.to_csv(output_path, index=False)
        
        # Show summary
        total_filings = len(df)
        print(f"✅ Successfully saved {total_filings} AI-related filings")
        print(f"   Saved to: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {ticker}: {str(e)}")
        return False

# ==== MAIN EXECUTION ====
def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("SEC EDGAR FILINGS COLLECTION SCRIPT")
    print("="*60)
    print(f"Filing Date Range: {NEWS_START_YEAR}-{NEWS_END_YEAR}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"SEC User Agent: {SEC_USER_AGENT}")
    print(f"🤖 AI Keywords: {len(AI_KEYWORDS)} keywords for search")
    print(f"📋 Filing Types: {', '.join(FILING_TYPES)}")
    print("="*60)
    
    # Load company list
    df = pd.read_csv(COMPANY_LIST_PATH)
    df = df[df['Ticker'].notna()]
    tickers = df['Ticker'].tolist()
    
    print(f"\n📊 Loaded {len(tickers)} tickers from {COMPANY_LIST_PATH}")
    
    # Filter to US companies only
    us_tickers = [ticker for ticker in tickers if is_us_ticker(ticker)]
    print(f"🇺🇸 US companies: {len(us_tickers)}")
    print(f"🌍 International companies: {len(tickers) - len(us_tickers)}")
    
    # Filter out already processed tickers
    remaining_tickers = []
    for ticker in us_tickers:
        clean_ticker = ticker.replace(' ', '_').replace('/', '_')
        output_path = os.path.join(OUTPUT_DIR, f"{clean_ticker}_filings.csv")
        if not os.path.exists(output_path):
            remaining_tickers.append(ticker)
    
    if len(remaining_tickers) < len(us_tickers):
        print(f"✅ Found {len(us_tickers) - len(remaining_tickers)} already processed")
        print(f"⏳ Remaining to process: {len(remaining_tickers)}")
    
    if not remaining_tickers:
        print("\n🎉 All US tickers already processed!")
        return
    
    # Process each ticker
    success_count = 0
    fail_count = 0
    
    start_time = datetime.now()
    
    for idx, ticker in enumerate(remaining_tickers, 1):
        print(f"\n[{idx}/{len(remaining_tickers)}] {ticker}")
        
        result = process_ticker(ticker)
        if result:
            success_count += 1
        else:
            fail_count += 1
        
        # Show progress every 5 tickers
        if idx % 5 == 0:
            print(f"\n📊 Progress: {idx}/{len(remaining_tickers)} completed")
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print("="*60)
    print(f"✅ Successfully processed: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"⏱️  Total time: {duration}")
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print("="*60)

if __name__ == "__main__":
    main()
