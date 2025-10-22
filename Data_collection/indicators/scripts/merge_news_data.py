import pandas as pd
import os
import re
from datetime import datetime
import numpy as np

# ==== CONFIG ====
# Get script directory for absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# Directories
AV_NEWS_DIR = os.path.join(BASE_DIR, "news_data", "av_news")
SEC_FILINGS_DIR = os.path.join(BASE_DIR, "news_data", "sec_filings")
OUTPUT_DIR = os.path.join(BASE_DIR, "news_data", "complete")
COMPANY_LIST_PATH = os.path.join(BASE_DIR, "..", "Tickers", "merged_tickers.csv")

# ==== CREATE OUTPUT DIRECTORY ====
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==== UTILITY FUNCTIONS ====
def load_company_list():
    """Load company tickers from CSV"""
    df = pd.read_csv(COMPANY_LIST_PATH)
    df = df[df['Ticker'].notna()]
    return df['Ticker'].tolist()

def clean_ticker_for_filename(ticker):
    """Clean ticker for filename usage"""
    return ticker.replace(' ', '_').replace('/', '_')

def parse_av_date(date_str):
    """Parse Alpha Vantage date format"""
    try:
        # AV format: 20240101T120000
        return datetime.strptime(date_str, '%Y%m%dT%H%M%S')
    except:
        return None

def parse_sec_date(date_str):
    """Parse SEC date format"""
    try:
        # SEC format: 2024-01-01
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        return None

def extract_url_domain(url):
    """Extract domain from URL for deduplication"""
    try:
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc
    except:
        return url

def calculate_similarity(text1, text2):
    """Calculate simple text similarity for deduplication"""
    if not text1 or not text2:
        return 0.0
    
    # Simple word overlap similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

def deduplicate_articles(articles_df):
    """Remove duplicate articles based on title similarity and source"""
    if articles_df.empty:
        return articles_df
    
    # Sort by date to keep newer articles when duplicates found
    articles_df = articles_df.sort_values('published_date', ascending=False)
    
    # Group by source domain for more efficient deduplication
    articles_df['source_domain'] = articles_df['url'].apply(extract_url_domain)
    
    deduplicated = []
    processed_titles = set()
    
    for _, article in articles_df.iterrows():
        title = article['title'].lower().strip()
        
        # Check for exact title matches
        if title in processed_titles:
            continue
        
        # Check for similar titles (threshold: 0.8 similarity)
        is_duplicate = False
        for processed_title in processed_titles:
            if calculate_similarity(title, processed_title) > 0.8:
                is_duplicate = True
                break
        
        if not is_duplicate:
            deduplicated.append(article)
            processed_titles.add(title)
    
    result_df = pd.DataFrame(deduplicated)
    result_df = result_df.drop('source_domain', axis=1, errors='ignore')
    
    return result_df

def merge_news_data(ticker):
    """Merge Alpha Vantage news and SEC filings for a single ticker"""
    clean_ticker = clean_ticker_for_filename(ticker)
    
    # Load Alpha Vantage news
    av_file = os.path.join(AV_NEWS_DIR, f"{clean_ticker}_news.csv")
    av_news_df = pd.DataFrame()
    
    if os.path.exists(av_file):
        try:
            av_news_df = pd.read_csv(av_file)
            if not av_news_df.empty:
                # Standardize AV news format
                av_news_df['source_type'] = 'news_article'
                av_news_df['published_date'] = av_news_df['time_published'].apply(parse_av_date)
                av_news_df['sentiment_score'] = pd.to_numeric(av_news_df['sentiment_score'], errors='coerce')
                av_news_df['relevance_score'] = pd.to_numeric(av_news_df['relevance_score'], errors='coerce')
                
                # Rename columns for consistency
                av_news_df = av_news_df.rename(columns={
                    'ticker_sentiment_score': 'ticker_sentiment',
                    'ticker_sentiment_label': 'ticker_sentiment_label'
                })
                
                print(f"  ✅ Loaded {len(av_news_df)} AV news articles")
        except Exception as e:
            print(f"  ⚠️  Error loading AV news: {str(e)}")
    
    # Load SEC filings
    sec_file = os.path.join(SEC_FILINGS_DIR, f"{clean_ticker}_filings.csv")
    sec_filings_df = pd.DataFrame()
    
    if os.path.exists(sec_file):
        try:
            sec_filings_df = pd.read_csv(sec_file)
            if not sec_filings_df.empty:
                # Standardize SEC filings format
                sec_filings_df['source_type'] = 'sec_filing'
                sec_filings_df['published_date'] = sec_filings_df['filing_date'].apply(parse_sec_date)
                sec_filings_df['title'] = sec_filings_df['filing_title']
                sec_filings_df['source'] = 'SEC EDGAR'
                sec_filings_df['category'] = 'focused'  # SEC filings are always focused AI content
                
                # Add sentiment placeholder (SEC filings don't have sentiment)
                sec_filings_df['sentiment_score'] = np.nan
                sec_filings_df['sentiment_label'] = 'neutral'
                sec_filings_df['ticker_sentiment'] = np.nan
                sec_filings_df['ticker_sentiment_label'] = 'neutral'
                sec_filings_df['relevance_score'] = 1.0  # SEC filings are always relevant
                
                print(f"  ✅ Loaded {len(sec_filings_df)} SEC filings")
        except Exception as e:
            print(f"  ⚠️  Error loading SEC filings: {str(e)}")
    
    # Check if we have any data
    if av_news_df.empty and sec_filings_df.empty:
        print(f"  ⚠️  No news data found for {ticker}")
        return False
    
    # Merge dataframes
    merged_df = pd.DataFrame()
    
    if not av_news_df.empty and not sec_filings_df.empty:
        # Both sources available - merge them
        merged_df = pd.concat([av_news_df, sec_filings_df], ignore_index=True)
    elif not av_news_df.empty:
        # Only AV news available
        merged_df = av_news_df
    else:
        # Only SEC filings available
        merged_df = sec_filings_df
    
    # Standardize column order
    standard_columns = [
        'ticker', 'title', 'url', 'published_date', 'source', 'source_type',
        'summary', 'sentiment_score', 'sentiment_label', 'ticker_sentiment',
        'ticker_sentiment_label', 'relevance_score', 'category', 'ai_keywords_found'
    ]
    
    # Add any additional columns from either source
    all_columns = list(merged_df.columns)
    for col in all_columns:
        if col not in standard_columns:
            standard_columns.append(col)
    
    # Reorder columns
    available_columns = [col for col in standard_columns if col in merged_df.columns]
    merged_df = merged_df[available_columns]
    
    # Sort by publication date (newest first)
    merged_df = merged_df.sort_values('published_date', ascending=False)
    
    # Deduplicate articles
    merged_df = deduplicate_articles(merged_df)
    
    # Calculate aggregate metrics
    merged_df = calculate_aggregate_metrics(merged_df)
    
    # Save merged data
    output_file = os.path.join(OUTPUT_DIR, f"{clean_ticker}_complete_news.csv")
    merged_df.to_csv(output_file, index=False)
    
    # Show summary
    total_articles = len(merged_df)
    news_articles = len(merged_df[merged_df['source_type'] == 'news_article'])
    sec_filings = len(merged_df[merged_df['source_type'] == 'sec_filing'])
    focused_articles = len(merged_df[merged_df['category'] == 'focused'])
    
    print(f"  ✅ Merged {total_articles} total items ({news_articles} news, {sec_filings} filings)")
    print(f"     - Focused AI content: {focused_articles}")
    print(f"     - Saved to: {output_file}")
    
    return True

def calculate_aggregate_metrics(df):
    """Calculate aggregate metrics for the merged dataset"""
    if df.empty:
        return df
    
    # Add year and quarter for time-based analysis
    df['year'] = df['published_date'].dt.year
    df['quarter'] = df['published_date'].dt.quarter
    
    # Calculate rolling metrics (if enough data)
    if len(df) > 1:
        # Rolling average sentiment (30-day window)
        df = df.sort_values('published_date')
        df['rolling_sentiment'] = df['sentiment_score'].rolling(window=30, min_periods=1).mean()
        
        # News volume trend (30-day window)
        df['rolling_volume'] = df.groupby(df['published_date'].dt.date).size().rolling(window=30, min_periods=1).sum()
    
    # Add AI intensity score (number of AI keywords found)
    df['ai_intensity'] = df['ai_keywords_found'].apply(
        lambda x: len(x.split(',')) if pd.notna(x) and x.strip() else 0
    )
    
    # Add content quality score (combination of relevance and sentiment)
    df['content_quality'] = (
        df['relevance_score'].fillna(0.5) * 0.6 +
        (df['sentiment_score'].fillna(0) + 1) / 2 * 0.4  # Normalize sentiment to 0-1
    )
    
    return df

def create_summary_statistics():
    """Create summary statistics across all companies"""
    print("\n" + "="*60)
    print("CREATING SUMMARY STATISTICS")
    print("="*60)
    
    summary_data = []
    tickers = load_company_list()
    
    for ticker in tickers:
        clean_ticker = clean_ticker_for_filename(ticker)
        file_path = os.path.join(OUTPUT_DIR, f"{clean_ticker}_complete_news.csv")
        
        if not os.path.exists(file_path):
            continue
        
        try:
            df = pd.read_csv(file_path)
            df['published_date'] = pd.to_datetime(df['published_date'])
            
            # Calculate summary metrics
            total_articles = len(df)
            if total_articles == 0:
                continue
            
            # Source breakdown
            news_articles = len(df[df['source_type'] == 'news_article'])
            sec_filings = len(df[df['source_type'] == 'sec_filing'])
            
            # Category breakdown
            focused_articles = len(df[df['category'] == 'focused'])
            broad_articles = len(df[df['category'] == 'broad'])
            
            # Sentiment metrics
            avg_sentiment = df['sentiment_score'].mean() if 'sentiment_score' in df.columns else np.nan
            positive_articles = len(df[df['sentiment_score'] > 0.1]) if 'sentiment_score' in df.columns else 0
            negative_articles = len(df[df['sentiment_score'] < -0.1]) if 'sentiment_score' in df.columns else 0
            
            # Time metrics
            date_range = f"{df['published_date'].min().strftime('%Y-%m-%d')} to {df['published_date'].max().strftime('%Y-%m-%d')}"
            
            summary_data.append({
                'ticker': ticker,
                'total_articles': total_articles,
                'news_articles': news_articles,
                'sec_filings': sec_filings,
                'focused_ai_articles': focused_articles,
                'broad_tech_articles': broad_articles,
                'avg_sentiment_score': avg_sentiment,
                'positive_articles': positive_articles,
                'negative_articles': negative_articles,
                'date_range': date_range,
                'data_completeness': 'complete' if news_articles > 0 and sec_filings > 0 else 'partial'
            })
            
        except Exception as e:
            print(f"  ⚠️  Error processing {ticker}: {str(e)}")
            continue
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(summary_data)
    
    if not summary_df.empty:
        # Sort by total articles (most active companies first)
        summary_df = summary_df.sort_values('total_articles', ascending=False)
        
        # Save summary
        summary_file = os.path.join(BASE_DIR, "news_data", "analysis", "news_summary.csv")
        os.makedirs(os.path.dirname(summary_file), exist_ok=True)
        summary_df.to_csv(summary_file, index=False)
        
        print(f"✅ Created summary for {len(summary_df)} companies")
        print(f"   Saved to: {summary_file}")
        
        # Show top companies by news volume
        print(f"\n📊 Top 10 companies by news volume:")
        for _, row in summary_df.head(10).iterrows():
            print(f"   {row['ticker']}: {row['total_articles']} articles ({row['data_completeness']})")
    
    return summary_df

# ==== MAIN EXECUTION ====
def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("NEWS DATA MERGING SCRIPT")
    print("="*60)
    print(f"AV News Directory: {AV_NEWS_DIR}")
    print(f"SEC Filings Directory: {SEC_FILINGS_DIR}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("="*60)
    
    # Load company list
    tickers = load_company_list()
    print(f"\n📊 Processing {len(tickers)} companies...")
    
    # Process each ticker
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    start_time = datetime.now()
    
    for idx, ticker in enumerate(tickers, 1):
        print(f"\n[{idx}/{len(tickers)}] {ticker}")
        
        # Check if we have any source data
        clean_ticker = clean_ticker_for_filename(ticker)
        av_file = os.path.join(AV_NEWS_DIR, f"{clean_ticker}_news.csv")
        sec_file = os.path.join(SEC_FILINGS_DIR, f"{clean_ticker}_filings.csv")
        
        if not os.path.exists(av_file) and not os.path.exists(sec_file):
            print(f"  ⚠️  No source data found - skipping")
            skipped_count += 1
            continue
        
        # Check if already processed
        output_file = os.path.join(OUTPUT_DIR, f"{clean_ticker}_complete_news.csv")
        if os.path.exists(output_file):
            print(f"  ✅ Already processed - skipping")
            skipped_count += 1
            continue
        
        result = merge_news_data(ticker)
        if result:
            success_count += 1
        else:
            fail_count += 1
        
        # Show progress every 10 tickers
        if idx % 10 == 0:
            print(f"\n📊 Progress: {idx}/{len(tickers)} completed")
    
    # Create summary statistics
    summary_df = create_summary_statistics()
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("MERGING COMPLETE")
    print("="*60)
    print(f"✅ Successfully merged: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"⏱️  Total time: {duration}")
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    
    if not summary_df.empty:
        print(f"\n📊 Summary Statistics:")
        print(f"   Total companies with news data: {len(summary_df)}")
        print(f"   Total articles collected: {summary_df['total_articles'].sum()}")
        print(f"   Average articles per company: {summary_df['total_articles'].mean():.1f}")
        print(f"   Companies with both news and SEC data: {len(summary_df[summary_df['data_completeness'] == 'complete'])}")
    
    print("="*60)

if __name__ == "__main__":
    main()
