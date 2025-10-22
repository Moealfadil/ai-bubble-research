import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ==== CONFIG ====
# Get script directory for absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# Directories
COMPLETE_NEWS_DIR = os.path.join(BASE_DIR, "news_data", "complete")
ANALYSIS_DIR = os.path.join(BASE_DIR, "news_data", "analysis")
COMPANY_LIST_PATH = os.path.join(BASE_DIR, "..", "Tickers", "merged_tickers.csv")

# ==== CREATE OUTPUT DIRECTORY ====
os.makedirs(ANALYSIS_DIR, exist_ok=True)

# ==== UTILITY FUNCTIONS ====
def load_company_list():
    """Load company tickers from CSV"""
    df = pd.read_csv(COMPANY_LIST_PATH)
    df = df[df['Ticker'].notna()]
    return df['Ticker'].tolist()

def clean_ticker_for_filename(ticker):
    """Clean ticker for filename usage"""
    return ticker.replace(' ', '_').replace('/', '_')

def load_all_news_data():
    """Load all news data from complete directory"""
    all_data = []
    tickers = load_company_list()
    
    for ticker in tickers:
        clean_ticker = clean_ticker_for_filename(ticker)
        file_path = os.path.join(COMPLETE_NEWS_DIR, f"{clean_ticker}_complete_news.csv")
        
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                df['published_date'] = pd.to_datetime(df['published_date'])
                all_data.append(df)
            except Exception as e:
                print(f"⚠️  Error loading {ticker}: {str(e)}")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"✅ Loaded news data for {len(all_data)} companies")
        print(f"   Total articles: {len(combined_df)}")
        return combined_df
    else:
        print("❌ No news data found")
        return pd.DataFrame()

def calculate_time_series_metrics(df):
    """Calculate time-series metrics for trend analysis"""
    if df.empty:
        return pd.DataFrame()
    
    # Create time-based aggregations
    df['year'] = df['published_date'].dt.year
    df['month'] = df['published_date'].dt.month
    df['quarter'] = df['published_date'].dt.quarter
    df['year_quarter'] = df['year'].astype(str) + 'Q' + df['quarter'].astype(str)
    
    # Monthly aggregations
    monthly_stats = df.groupby(['ticker', 'year', 'month']).agg({
        'title': 'count',  # Article count
        'sentiment_score': 'mean',  # Average sentiment
        'relevance_score': 'mean',  # Average relevance
        'category': lambda x: (x == 'focused').sum()  # Focused AI articles count
    }).reset_index()
    
    monthly_stats.columns = ['ticker', 'year', 'month', 'article_count', 'avg_sentiment', 'avg_relevance', 'focused_count']
    
    # Quarterly aggregations
    quarterly_stats = df.groupby(['ticker', 'year', 'quarter']).agg({
        'title': 'count',
        'sentiment_score': 'mean',
        'relevance_score': 'mean',
        'category': lambda x: (x == 'focused').sum(),
        'source_type': lambda x: (x == 'news_article').sum()  # News vs SEC breakdown
    }).reset_index()
    
    quarterly_stats.columns = ['ticker', 'year', 'quarter', 'article_count', 'avg_sentiment', 'avg_relevance', 'focused_count', 'news_count']
    quarterly_stats['sec_count'] = quarterly_stats['article_count'] - quarterly_stats['news_count']
    
    return monthly_stats, quarterly_stats

def calculate_sentiment_trends(df):
    """Calculate sentiment trends and patterns"""
    if df.empty:
        return pd.DataFrame()
    
    # Overall sentiment trends by time
    df['published_date'] = pd.to_datetime(df['published_date'])
    df['year_month'] = df['published_date'].dt.to_period('M')
    
    sentiment_trends = df.groupby('year_month').agg({
        'sentiment_score': ['mean', 'std', 'count'],
        'category': lambda x: (x == 'focused').sum()
    }).reset_index()
    
    # Flatten column names
    sentiment_trends.columns = ['year_month', 'avg_sentiment', 'sentiment_std', 'article_count', 'focused_count']
    sentiment_trends['focused_ratio'] = sentiment_trends['focused_count'] / sentiment_trends['article_count']
    
    # Calculate rolling averages
    sentiment_trends['rolling_sentiment_3m'] = sentiment_trends['avg_sentiment'].rolling(window=3, min_periods=1).mean()
    sentiment_trends['rolling_volume_3m'] = sentiment_trends['article_count'].rolling(window=3, min_periods=1).mean()
    
    return sentiment_trends

def calculate_company_rankings(df):
    """Calculate various company rankings and metrics"""
    if df.empty:
        return pd.DataFrame()
    
    company_stats = df.groupby('ticker').agg({
        'title': 'count',  # Total articles
        'sentiment_score': ['mean', 'std'],  # Sentiment metrics
        'relevance_score': 'mean',  # Average relevance
        'category': lambda x: (x == 'focused').sum(),  # Focused AI articles
        'source_type': lambda x: (x == 'news_article').sum(),  # News articles
        'published_date': ['min', 'max']  # Date range
    }).reset_index()
    
    # Flatten column names
    company_stats.columns = [
        'ticker', 'total_articles', 'avg_sentiment', 'sentiment_std',
        'avg_relevance', 'focused_articles', 'news_articles', 'earliest_date', 'latest_date'
    ]
    
    company_stats['sec_articles'] = company_stats['total_articles'] - company_stats['news_articles']
    company_stats['focused_ratio'] = company_stats['focused_articles'] / company_stats['total_articles']
    company_stats['sentiment_consistency'] = 1 / (1 + company_stats['sentiment_std'].fillna(0))
    
    # Calculate rankings
    company_stats['volume_rank'] = company_stats['total_articles'].rank(ascending=False, method='dense')
    company_stats['sentiment_rank'] = company_stats['avg_sentiment'].rank(ascending=False, method='dense')
    company_stats['focus_rank'] = company_stats['focused_ratio'].rank(ascending=False, method='dense')
    company_stats['consistency_rank'] = company_stats['sentiment_consistency'].rank(ascending=False, method='dense')
    
    # Calculate composite score
    company_stats['composite_score'] = (
        company_stats['volume_rank'].rank(pct=True) * 0.3 +
        company_stats['sentiment_rank'].rank(pct=True) * 0.3 +
        company_stats['focus_rank'].rank(pct=True) * 0.2 +
        company_stats['consistency_rank'].rank(pct=True) * 0.2
    )
    
    company_stats['overall_rank'] = company_stats['composite_score'].rank(ascending=False, method='dense')
    
    return company_stats.sort_values('overall_rank')

def analyze_ai_keyword_trends(df):
    """Analyze AI keyword usage trends over time"""
    if df.empty or 'ai_keywords_found' not in df.columns:
        return pd.DataFrame()
    
    # Extract individual keywords
    all_keywords = []
    for keywords_str in df['ai_keywords_found'].dropna():
        if pd.notna(keywords_str) and keywords_str.strip():
            keywords = [k.strip() for k in keywords_str.split(',')]
            all_keywords.extend(keywords)
    
    # Count keyword frequency
    from collections import Counter
    keyword_counts = Counter(all_keywords)
    
    # Create keyword trend analysis
    keyword_trends = []
    df['year'] = df['published_date'].dt.year
    
    for keyword, count in keyword_counts.most_common(20):  # Top 20 keywords
        yearly_counts = df[df['ai_keywords_found'].str.contains(keyword, na=False)].groupby('year').size()
        
        for year, year_count in yearly_counts.items():
            keyword_trends.append({
                'keyword': keyword,
                'year': year,
                'count': year_count,
                'total_count': count
            })
    
    keyword_df = pd.DataFrame(keyword_trends)
    return keyword_df

def create_visualizations(monthly_stats, quarterly_stats, sentiment_trends, company_rankings, keyword_trends):
    """Create visualization plots for trend analysis"""
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # 1. Overall sentiment trend over time
    if not sentiment_trends.empty:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Sentiment trend
        ax1.plot(sentiment_trends['year_month'].astype(str), sentiment_trends['rolling_sentiment_3m'], 
                marker='o', linewidth=2, markersize=4)
        ax1.set_title('AI News Sentiment Trend (3-Month Rolling Average)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Average Sentiment Score')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Volume trend
        ax2.bar(sentiment_trends['year_month'].astype(str), sentiment_trends['rolling_volume_3m'], 
               alpha=0.7, color='skyblue')
        ax2.set_title('AI News Volume Trend (3-Month Rolling Average)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Average Article Count')
        ax2.set_xlabel('Time Period')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(ANALYSIS_DIR, 'sentiment_and_volume_trends.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 2. Top companies by various metrics
    if not company_rankings.empty:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Top 15 companies by volume
        top_volume = company_rankings.head(15)
        ax1.barh(top_volume['ticker'], top_volume['total_articles'])
        ax1.set_title('Top 15 Companies by News Volume', fontweight='bold')
        ax1.set_xlabel('Total Articles')
        
        # Top 15 companies by sentiment
        top_sentiment = company_rankings.nlargest(15, 'avg_sentiment')
        ax2.barh(top_sentiment['ticker'], top_sentiment['avg_sentiment'])
        ax2.set_title('Top 15 Companies by Average Sentiment', fontweight='bold')
        ax2.set_xlabel('Average Sentiment Score')
        
        # Top 15 companies by AI focus
        top_focus = company_rankings.nlargest(15, 'focused_ratio')
        ax3.barh(top_focus['ticker'], top_focus['focused_ratio'])
        ax3.set_title('Top 15 Companies by AI Focus Ratio', fontweight='bold')
        ax3.set_xlabel('Focused AI Articles / Total Articles')
        
        # Composite ranking
        top_composite = company_rankings.head(15)
        ax4.barh(top_composite['ticker'], top_composite['composite_score'])
        ax4.set_title('Top 15 Companies by Composite Score', fontweight='bold')
        ax4.set_xlabel('Composite Score')
        
        plt.tight_layout()
        plt.savefig(os.path.join(ANALYSIS_DIR, 'company_rankings.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 3. AI keyword trends
    if not keyword_trends.empty:
        # Get top keywords for trend analysis
        top_keywords = keyword_trends.groupby('keyword')['total_count'].max().nlargest(10).index
        
        fig, ax = plt.subplots(figsize=(15, 8))
        
        for keyword in top_keywords:
            keyword_data = keyword_trends[keyword_trends['keyword'] == keyword]
            ax.plot(keyword_data['year'], keyword_data['count'], marker='o', label=keyword, linewidth=2)
        
        ax.set_title('AI Keyword Usage Trends Over Time', fontsize=14, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Usage Count')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(ANALYSIS_DIR, 'ai_keyword_trends.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"✅ Created visualizations in {ANALYSIS_DIR}")

def generate_insights_report(company_rankings, sentiment_trends, keyword_trends):
    """Generate insights and recommendations"""
    insights = []
    
    # Company insights
    if not company_rankings.empty:
        top_volume = company_rankings.head(5)
        top_sentiment = company_rankings.nlargest(5, 'avg_sentiment')
        most_focused = company_rankings.nlargest(5, 'focused_ratio')
        
        insights.append("=== TOP COMPANIES BY METRICS ===")
        insights.append(f"Most News Volume: {', '.join(top_volume['ticker'].tolist())}")
        insights.append(f"Highest Sentiment: {', '.join(top_sentiment['ticker'].tolist())}")
        insights.append(f"Most AI-Focused: {', '.join(most_focused['ticker'].tolist())}")
        insights.append("")
    
    # Sentiment insights
    if not sentiment_trends.empty:
        latest_sentiment = sentiment_trends['avg_sentiment'].iloc[-1]
        sentiment_trend = sentiment_trends['rolling_sentiment_3m'].iloc[-3:].mean() - sentiment_trends['rolling_sentiment_3m'].iloc[-6:-3].mean()
        
        insights.append("=== SENTIMENT ANALYSIS ===")
        insights.append(f"Latest Average Sentiment: {latest_sentiment:.3f}")
        if sentiment_trend > 0.05:
            insights.append("Trend: Sentiment is improving")
        elif sentiment_trend < -0.05:
            insights.append("Trend: Sentiment is declining")
        else:
            insights.append("Trend: Sentiment is stable")
        insights.append("")
    
    # Keyword insights
    if not keyword_trends.empty:
        top_keywords = keyword_trends.groupby('keyword')['total_count'].max().nlargest(5)
        
        insights.append("=== TOP AI KEYWORDS ===")
        for keyword, count in top_keywords.items():
            insights.append(f"{keyword}: {count} mentions")
        insights.append("")
    
    # Data quality insights
    total_companies = len(company_rankings) if not company_rankings.empty else 0
    complete_data = len(company_rankings[(company_rankings['news_articles'] > 0) & (company_rankings['sec_articles'] > 0)]) if not company_rankings.empty else 0
    
    insights.append("=== DATA QUALITY ===")
    insights.append(f"Total Companies Analyzed: {total_companies}")
    insights.append(f"Companies with Complete Data (News + SEC): {complete_data}")
    insights.append(f"Data Completeness: {(complete_data/total_companies*100):.1f}%" if total_companies > 0 else "Data Completeness: 0%")
    
    # Save insights report
    insights_text = "\n".join(insights)
    insights_file = os.path.join(ANALYSIS_DIR, 'insights_report.txt')
    
    with open(insights_file, 'w') as f:
        f.write(insights_text)
    
    print(f"✅ Generated insights report: {insights_file}")
    
    # Print insights to console
    print("\n" + "="*60)
    print("KEY INSIGHTS")
    print("="*60)
    print(insights_text)
    print("="*60)

# ==== MAIN EXECUTION ====
def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("AI NEWS TREND ANALYSIS")
    print("="*60)
    print(f"Complete News Directory: {COMPLETE_NEWS_DIR}")
    print(f"Analysis Output Directory: {ANALYSIS_DIR}")
    print("="*60)
    
    # Load all news data
    print("\n📊 Loading all news data...")
    df = load_all_news_data()
    
    if df.empty:
        print("❌ No news data found. Please run news collection scripts first.")
        return
    
    # Calculate various metrics
    print("\n📈 Calculating time-series metrics...")
    monthly_stats, quarterly_stats = calculate_time_series_metrics(df)
    
    print("📊 Calculating sentiment trends...")
    sentiment_trends = calculate_sentiment_trends(df)
    
    print("🏆 Calculating company rankings...")
    company_rankings = calculate_company_rankings(df)
    
    print("🤖 Analyzing AI keyword trends...")
    keyword_trends = analyze_ai_keyword_trends(df)
    
    # Save analysis results
    print("\n💾 Saving analysis results...")
    
    if not monthly_stats.empty:
        monthly_stats.to_csv(os.path.join(ANALYSIS_DIR, 'monthly_news_stats.csv'), index=False)
    
    if not quarterly_stats.empty:
        quarterly_stats.to_csv(os.path.join(ANALYSIS_DIR, 'quarterly_news_stats.csv'), index=False)
    
    if not sentiment_trends.empty:
        sentiment_trends.to_csv(os.path.join(ANALYSIS_DIR, 'sentiment_trends.csv'), index=False)
    
    if not company_rankings.empty:
        company_rankings.to_csv(os.path.join(ANALYSIS_DIR, 'company_rankings.csv'), index=False)
    
    if not keyword_trends.empty:
        keyword_trends.to_csv(os.path.join(ANALYSIS_DIR, 'keyword_trends.csv'), index=False)
    
    # Create visualizations
    print("📊 Creating visualizations...")
    create_visualizations(monthly_stats, quarterly_stats, sentiment_trends, company_rankings, keyword_trends)
    
    # Generate insights report
    print("📝 Generating insights report...")
    generate_insights_report(company_rankings, sentiment_trends, keyword_trends)
    
    # Final summary
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"📁 Analysis files saved to: {ANALYSIS_DIR}")
    print(f"📊 Total articles analyzed: {len(df)}")
    print(f"🏢 Companies analyzed: {df['ticker'].nunique()}")
    print(f"📅 Date range: {df['published_date'].min()} to {df['published_date'].max()}")
    print(f"🤖 AI-focused articles: {len(df[df['category'] == 'focused'])}")
    print(f"📰 News articles: {len(df[df['source_type'] == 'news_article'])}")
    print(f"📋 SEC filings: {len(df[df['source_type'] == 'sec_filing'])}")
    print("="*60)

if __name__ == "__main__":
    main()
