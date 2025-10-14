#!/usr/bin/env python3
"""
International Ticker Symbol Testing Script for Alpha Vantage

This script tests different symbol formats for international tickers to find
the correct format that works with Alpha Vantage API.

Usage:
    python test_international_symbols.py

Requirements:
    - Alpha Vantage API key in .env file
    - merged_tickers.csv file in parent directory
"""

import requests
import time
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEYS', '').split(',')[0].strip()
if not API_KEY:
    print("❌ Error: ALPHA_VANTAGE_API_KEYS not found in environment variables")
    print("Please create a .env file with your API key")
    exit(1)

# Rate limiting
RATE_LIMIT_DELAY = 15  # seconds between API calls

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
TICKER_FILE = os.path.join(BASE_DIR, "..", "Tickers", "merged_tickers.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "international_symbol_test_results.csv")

def get_format_variations(original_ticker):
    """Generate different symbol format variations to test"""
    
    format_variations = []
    
    # Extract symbol and exchange from your format
    if ' ' in original_ticker:
        symbol, exchange = original_ticker.split(' ', 1)
    else:
        symbol = original_ticker
        exchange = None
    
    # Generate test formats based on exchange
    if exchange == 'KS':  # Korean
        format_variations = [
            f"{symbol}.KRX",
            f"{symbol}.KQ",
            symbol,
            f"{symbol}.KS"
        ]
    elif exchange == 'TT':  # Taiwan
        format_variations = [
            f"{symbol}.TPE",
            symbol,
            f"{symbol}.TT"
        ]
    elif exchange == 'JP':  # Japan
        format_variations = [
            f"{symbol}.TYO",
            symbol,
            f"{symbol}.JP"
        ]
    elif exchange == 'GR':  # Germany
        format_variations = [
            f"{symbol}.FRA",
            symbol,
            f"{symbol}.GR"
        ]
    elif exchange == 'HK':  # Hong Kong
        format_variations = [
            f"{symbol}.HKG",
            symbol,
            f"{symbol}.HK"
        ]
    elif exchange == 'LN':  # London
        format_variations = [
            f"{symbol}.LON",
            symbol,
            f"{symbol}.LN"
        ]
    elif exchange == 'AU':  # Australia
        format_variations = [
            f"{symbol}.ASX",
            symbol,
            f"{symbol}.AU"
        ]
    elif exchange == 'SS':  # Swedish
        format_variations = [
            f"{symbol}.STO",
            symbol,
            f"{symbol}.SS"
        ]
    elif exchange == 'IM':  # Italian
        format_variations = [
            f"{symbol}.MIL",
            symbol,
            f"{symbol}.IM"
        ]
    elif exchange == 'CN':  # Canadian
        format_variations = [
            f"{symbol}.TSX",
            symbol,
            f"{symbol}.CN"
        ]
    elif exchange == 'FP':  # French
        format_variations = [
            f"{symbol}.PAR",
            symbol,
            f"{symbol}.FP"
        ]
    elif exchange == 'FH':  # Finnish
        format_variations = [
            f"{symbol}.HEL",
            symbol,
            f"{symbol}.FH"
        ]
    elif exchange == 'SW':  # Swiss
        format_variations = [
            f"{symbol}.SWX",
            symbol,
            f"{symbol}.SW"
        ]
    else:
        # For unknown formats, try the original
        format_variations = [original_ticker]
    
    return format_variations

def test_symbol_with_overview(ticker_format):
    """Test if a symbol format works using the OVERVIEW API"""
    
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker_format}&apikey={API_KEY}"
    
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
        
        # Check if symbol is valid
        if "Symbol" in data and data["Symbol"] != "None" and data["Symbol"] != "":
            return {
                'valid': True,
                'symbol': data.get("Symbol", ""),
                'name': data.get("Name", ""),
                'exchange': data.get("Exchange", ""),
                'sector': data.get("Sector", ""),
                'industry': data.get("Industry", ""),
                'market_cap': data.get("MarketCapitalization", ""),
                'error': None
            }
        else:
            return {
                'valid': False,
                'symbol': "",
                'name': "",
                'exchange': "",
                'sector': "",
                'industry': "",
                'market_cap': "",
                'error': data.get("Note", data.get("Error Message", "Unknown error"))
            }
            
    except Exception as e:
        return {
            'valid': False,
            'symbol': "",
            'name': "",
            'exchange': "",
            'sector': "",
            'industry': "",
            'market_cap': "",
            'error': str(e)
        }

def test_symbol_formats(original_ticker):
    """Test different symbol formats for a given ticker"""
    
    print(f"\n{'='*60}")
    print(f"Testing: {original_ticker}")
    print(f"{'='*60}")
    
    format_variations = get_format_variations(original_ticker)
    results = []
    
    for i, format_ticker in enumerate(format_variations, 1):
        print(f"  [{i}/{len(format_variations)}] Testing: {format_ticker}")
        
        # Test the symbol format
        result = test_symbol_with_overview(format_ticker)
        
        result['original_ticker'] = original_ticker
        result['tested_format'] = format_ticker
        result['test_order'] = i
        
        results.append(result)
        
        if result['valid']:
            print(f"    ✅ VALID: {result['name']}")
            print(f"    📊 Symbol: {result['symbol']}")
            print(f"    🏢 Exchange: {result['exchange']}")
            print(f"    💼 Sector: {result['sector']}")
            if result['market_cap']:
                print(f"    💰 Market Cap: ${result['market_cap']}")
            break
        else:
            print(f"    ❌ Invalid: {result['error']}")
        
        # Rate limiting
        if i < len(format_variations):
            time.sleep(RATE_LIMIT_DELAY)
    
    return results

def load_international_tickers():
    """Load and filter international tickers from CSV"""
    
    try:
        df = pd.read_csv(TICKER_FILE)
        
        # Filter international tickers (those with spaces or non-US exchange codes)
        international_pattern = ' |JP|KS|TT|GR|HK|AU|LN|SS|IM|CN|FP|FH|SW'
        international_tickers = df[df['Ticker'].str.contains(international_pattern, na=False)]
        
        print(f"📊 Loaded {len(df)} total tickers")
        print(f"🌍 Found {len(international_tickers)} international tickers")
        
        return international_tickers
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find {TICKER_FILE}")
        print("Please ensure the file exists in the correct location")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error loading ticker file: {e}")
        return pd.DataFrame()

def main():
    """Main execution function"""
    
    print("\n" + "="*60)
    print("INTERNATIONAL TICKER SYMBOL TESTING")
    print("="*60)
    print(f"API Key: {API_KEY[:8]}...")
    print(f"Rate Limit: {RATE_LIMIT_DELAY}s between calls")
    print(f"Output File: {OUTPUT_FILE}")
    print("="*60)
    
    # Load international tickers
    international_tickers = load_international_tickers()
    
    if international_tickers.empty:
        print("❌ No international tickers found. Exiting.")
        return
    
    # Ask user how many to test
    total_count = len(international_tickers)
    print(f"\n📊 Found {total_count} international tickers")
    print("\nOptions:")
    print("1. Test all tickers (will use many API calls)")
    print("2. Test sample tickers (recommended for first run)")
    print("3. Test specific tickers")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        tickers_to_test = international_tickers['Ticker'].tolist()
        print(f"🧪 Testing ALL {len(tickers_to_test)} international tickers")
    elif choice == "2":
        # Test a sample from each region
        sample_tickers = [
            "005930 KS",  # Samsung (Korea)
            "2395 TT",    # Advantech (Taiwan)
            "6701 JP",    # NEC (Japan)
            "SIE GR",     # Siemens (Germany)
            "700 HK",     # Tencent (Hong Kong)
            "AVV LN",     # AVEVA (London)
            "XRO AU",     # Xero (Australia)
        ]
        # Filter to only include tickers that exist in our list
        tickers_to_test = [t for t in sample_tickers if t in international_tickers['Ticker'].values]
        print(f"🧪 Testing SAMPLE of {len(tickers_to_test)} international tickers")
    elif choice == "3":
        # Let user specify tickers
        ticker_input = input("Enter tickers separated by commas: ").strip()
        tickers_to_test = [t.strip() for t in ticker_input.split(',') if t.strip()]
        print(f"🧪 Testing SPECIFIED {len(tickers_to_test)} tickers")
    else:
        print("❌ Invalid choice. Exiting.")
        return
    
    # Estimate API usage
    estimated_calls = len(tickers_to_test) * 3  # Average 3 formats tested per ticker
    estimated_time = estimated_calls * RATE_LIMIT_DELAY / 60  # minutes
    
    print(f"\n⏱️  Estimated API calls: {estimated_calls}")
    print(f"⏱️  Estimated time: {estimated_time:.1f} minutes")
    
    confirm = input(f"\nProceed with testing? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Testing cancelled.")
        return
    
    # Test each ticker
    all_results = []
    start_time = datetime.now()
    
    for i, ticker in enumerate(tickers_to_test, 1):
        print(f"\n[{i}/{len(tickers_to_test)}] Processing...")
        
        results = test_symbol_formats(ticker)
        all_results.extend(results)
        
        # Save intermediate results every 5 tickers
        if i % 5 == 0:
            temp_df = pd.DataFrame(all_results)
            temp_file = OUTPUT_FILE.replace('.csv', f'_temp_{i}.csv')
            temp_df.to_csv(temp_file, index=False)
            print(f"💾 Intermediate results saved to {temp_file}")
    
    # Save final results
    if all_results:
        results_df = pd.DataFrame(all_results)
        results_df.to_csv(OUTPUT_FILE, index=False)
        
        # Generate summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        valid_tickers = results_df[results_df['valid'] == True]
        invalid_tickers = results_df[results_df['valid'] == False]
        
        print("\n" + "="*60)
        print("TESTING COMPLETE")
        print("="*60)
        print(f"⏱️  Total time: {duration}")
        print(f"📊 Total tests: {len(results_df)}")
        print(f"✅ Valid symbols found: {len(valid_tickers)}")
        print(f"❌ Invalid symbols: {len(invalid_tickers)}")
        
        if not valid_tickers.empty:
            print(f"\n✅ WORKING SYMBOLS:")
            for _, row in valid_tickers.iterrows():
                print(f"  {row['original_ticker']} → {row['tested_format']} ({row['name']})")
        
        print(f"\n💾 Results saved to: {OUTPUT_FILE}")
        
        # Show recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if len(valid_tickers) > len(tickers_to_test) * 0.5:
            print("  ✅ Good coverage! You can proceed with alphadata.py")
        elif len(valid_tickers) > len(tickers_to_test) * 0.2:
            print("  ⚠️  Partial coverage. Consider testing more formats or using existing data")
        else:
            print("  ❌ Low coverage. Consider using existing complete_data_improved/ files")
        
        print(f"\n📋 Next steps:")
        print(f"  1. Review {OUTPUT_FILE}")
        print(f"  2. Update your ticker list with working symbols")
        print(f"  3. Run alphadata.py with corrected symbols")
        
    else:
        print("❌ No results to save. Check your API key and internet connection.")
    
    print("="*60)

if __name__ == "__main__":
    main()
