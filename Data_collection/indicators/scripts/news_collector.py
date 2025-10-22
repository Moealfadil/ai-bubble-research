import requests
import pandas as pd
import time
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import re

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
NEWS_START_YEAR = int(os.getenv('NEWS_START_YEAR', '2015'))
NEWS_END_YEAR = int(os.getenv('NEWS_END_YEAR', '2025'))
NEWS_RATE_LIMIT_DELAY = int(os.getenv('NEWS_RATE_LIMIT_DELAY', '1'))  # Premium tier: 75 calls/min

# Directories
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "news_data", "av_news")
COMPANY_LIST_PATH = os.path.join(BASE_DIR, "..", "Tickers", "merged_tickers.csv")

# AI Keywords for focused categorization
AI_KEYWORDS = [
    'artificial intelligence', 'machine learning', 'deep learning',
    'neural network', 'natural language processing', 'computer vision',
    'AI', 'ML', 'NLP', 'generative AI', 'large language model', 'LLM',
    'chatbot', 'autonomous', 'predictive analytics', 'data science',
    'automation', 'algorithm', 'intelligent', 'smart', 'cognitive'
]

# Ticker mapping for Alpha Vantage API compatibility
TICKER_MAPPING = {
    'GOOGL': 'GOOG',    # Alphabet Inc Class A
    'FB': 'META',       # Facebook -> Meta Platforms
    'TWTR': 'X',        # Twitter -> X (if supported)
    # Add more mappings as Alpha Vantage supports different ticker formats
    # Note: Some companies may not be available in Alpha Vantage news database
}

def get_av_ticker(original_ticker):
    """Get the correct ticker for Alpha Vantage API"""
    return TICKER_MAPPING.get(original_ticker, original_ticker)

# ==== CREATE OUTPUT DIRECTORY ====
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==== API KEY MANAGEMENT ====
current_api_key_index = 0
api_call_counts = {key: 0 for key in API_KEYS}

def get_current_api_key():
    """Get the current API key"""
    global current_api_key_index
    return API_KEYS[current_api_key_index]

def rotate_api_key():
    """Rotate to the next API key when limit is reached"""
    global current_api_key_index
    
    current_key = API_KEYS[current_api_key_index]
    
    # Premium tier has much higher limits, but we'll still rotate for safety
    if api_call_counts[current_key] >= 1000:  # Conservative limit for premium
        current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)
        next_key = API_KEYS[current_api_key_index]
        
        if api_call_counts[next_key] >= 1000:
            print("\n" + "="*60)
            print("⚠️  ALL API KEYS HAVE REACHED LIMIT")
            print("="*60)
            return False
        
        print(f"\n🔄 Rotating API key: {current_key[:8]}... → {next_key[:8]}...")
    
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
        stats.append(f"{marker}Key {idx+1} ({key[:8]}...): {api_call_counts[key]} calls")
    return "\n".join(stats)

# ==== LOAD COMPANY LIST ====
def load_company_list():
    """Load company tickers from CSV"""
    df = pd.read_csv(COMPANY_LIST_PATH)
    # Filter out empty rows
    df = df[df['Ticker'].notna()]
    return df['Ticker'].tolist()

# ==== AI KEYWORD DETECTION ====
def detect_ai_keywords(text):
    """Detect AI-related keywords in text and return found keywords"""
    if not text:
        return []
    
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in AI_KEYWORDS:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords

def categorize_news_article(title, summary):
    """Categorize news article as broad or focused AI news"""
    full_text = f"{title} {summary}".lower()
    
    # Check for AI-specific keywords
    ai_keywords_found = detect_ai_keywords(f"{title} {summary}")
    
    if ai_keywords_found:
        return "focused", ai_keywords_found
    else:
        return "broad", []

# ==== NEWS FETCHING ====
def fetch_news_for_ticker(ticker, start_date, end_date):
    """Fetch news articles for a specific ticker and date range"""
    # Use ticker mapping for Alpha Vantage API compatibility
    av_ticker = get_av_ticker(ticker)
    if av_ticker != ticker:
        print(f"  Using ticker mapping: {ticker} -> {av_ticker}")
    
    print(f"  Fetching news for {ticker} ({start_date} to {end_date})...")
    
    api_key = get_current_api_key()
    
    # Alpha Vantage NEWS_SENTIMENT API parameters
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': av_ticker,  # Use mapped ticker
        'topics': 'technology',  # Focus on technology news
        'time_from': start_date,
        'time_to': end_date,
        'sort': 'EARLIEST',
        'limit': 1000,  # Premium tier allows larger limits
        'apikey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        increment_api_call()
        
        # Check for API errors
        if "Note" in data:
            print(f"  ⚠️  API message: {data['Note']}")
            return []
        if "Error Message" in data:
            print(f"  ⚠️  API error: {data['Error Message']}")
            return []
        if "Information" in data:
            print(f"  ⚠️  API info: {data['Information']}")
            return []
        
        # Extract news articles
        if "feed" in data:
            articles = data["feed"]
            print(f"  ✅ Found {len(articles)} articles")
            return articles
        else:
            print(f"  ⚠️  No 'feed' field in response")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Request error: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON decode error: {str(e)}")
        return []
    except Exception as e:
        print(f"  ❌ Unexpected error: {str(e)}")
        return []

def process_news_articles(articles, ticker):
    """Process and categorize news articles"""
    processed_articles = []
    
    for article in articles:
        try:
            # Extract basic article information
            title = article.get('title', '')
            url = article.get('url', '')
            time_published = article.get('time_published', '')
            source = article.get('source', '')
            summary = article.get('summary', '')
            
            # Extract sentiment information
            sentiment_info = article.get('overall_sentiment_score', 0)
            sentiment_label = article.get('overall_sentiment_label', '')
            
            # Extract ticker-specific sentiment
            ticker_sentiment = None
            ticker_sentiment_score = None
            ticker_sentiment_label = None
            
            if 'ticker_sentiment' in article:
                for ticker_data in article['ticker_sentiment']:
                    if ticker_data.get('ticker') == ticker:
                        ticker_sentiment_score = ticker_data.get('relevance_score', 0)
                        ticker_sentiment_label = ticker_data.get('ticker_sentiment_label', '')
                        break
            
            # Get relevance score
            relevance_score = article.get('relevance_score', 0)
            
            # Categorize as broad or focused AI news
            category, ai_keywords_found = categorize_news_article(title, summary)
            
            processed_article = {
                'ticker': ticker,
                'title': title,
                'url': url,
                'time_published': time_published,
                'source': source,
                'summary': summary,
                'sentiment_score': sentiment_info,
                'sentiment_label': sentiment_label,
                'ticker_sentiment_score': ticker_sentiment_score,
                'ticker_sentiment_label': ticker_sentiment_label,
                'relevance_score': relevance_score,
                'category': category,
                'ai_keywords_found': ', '.join(ai_keywords_found) if ai_keywords_found else ''
            }
            
            processed_articles.append(processed_article)
            
        except Exception as e:
            print(f"  ⚠️  Error processing article: {str(e)}")
            continue
    
    return processed_articles

def process_ticker(ticker):
    """Process a single ticker: fetch news, categorize, save"""
    print(f"\n{'='*60}")
    print(f"Processing {ticker}...")
    print(f"{'='*60}")
    
    # Check if we can continue with API calls
    if not rotate_api_key():
        return False  # All keys exhausted
    
    try:
        # Create date range for news collection
        start_date = f"{NEWS_START_YEAR}0101T0000"  # YYYYMMDDTHHMM format
        end_date = f"{NEWS_END_YEAR}1231T2359"
        
        # Fetch news articles
        articles = fetch_news_for_ticker(ticker, start_date, end_date)
        
        if not articles:
            print(f"⚠️  No news articles found for {ticker}")
            return False
        
        # Process and categorize articles
        processed_articles = process_news_articles(articles, ticker)
        
        if not processed_articles:
            print(f"⚠️  No valid articles processed for {ticker}")
            return False
        
        # Create DataFrame
        df = pd.DataFrame(processed_articles)
        
        # Sort by publication time (newest first)
        if 'time_published' in df.columns:
            df = df.sort_values('time_published', ascending=False)
        
        # Save to CSV
        clean_ticker = ticker.replace(' ', '_').replace('/', '_')
        output_path = os.path.join(OUTPUT_DIR, f"{clean_ticker}_news.csv")
        df.to_csv(output_path, index=False)
        
        # Show summary
        total_articles = len(df)
        focused_count = len(df[df['category'] == 'focused'])
        broad_count = len(df[df['category'] == 'broad'])
        
        print(f"✅ Successfully saved {total_articles} articles")
        print(f"   - Focused AI news: {focused_count}")
        print(f"   - Broad tech news: {broad_count}")
        print(f"   Saved to: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {ticker}: {str(e)}")
        return False

# ==== MAIN EXECUTION ====
def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("ALPHA VANTAGE NEWS COLLECTION SCRIPT")
    print("="*60)
    print(f"News Date Range: {NEWS_START_YEAR}-{NEWS_END_YEAR}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Rate Limit Delay: {NEWS_RATE_LIMIT_DELAY}s between calls")
    print(f"\n🔑 API Keys: {len(API_KEYS)} keys loaded")
    print(f"📊 Premium Tier: 75 calls/minute")
    print(f"🤖 AI Keywords: {len(AI_KEYWORDS)} keywords for focused categorization")
    print("="*60)
    
    # Load company list
    tickers = load_company_list()
    print(f"\n📊 Loaded {len(tickers)} tickers from {COMPANY_LIST_PATH}")
    
    # Filter out already processed tickers
    remaining_tickers = []
    for ticker in tickers:
        clean_ticker = ticker.replace(' ', '_').replace('/', '_')
        output_path = os.path.join(OUTPUT_DIR, f"{clean_ticker}_news.csv")
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
        elif result is False and sum(api_call_counts.values()) >= len(API_KEYS) * 1000:
            # All keys exhausted
            stopped_early = True
            break
        else:
            fail_count += 1
        
        # Rate limiting
        time.sleep(NEWS_RATE_LIMIT_DELAY)
        
        # Show API usage stats every 10 tickers
        if idx % 10 == 0:
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
        print(f"\n💡 To continue: Re-run the script")
        print(f"   Completed files are automatically skipped")
    
    print("="*60)

if __name__ == "__main__":
    main()
