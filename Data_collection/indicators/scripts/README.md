# Scripts Directory - AI Bubble Research Data Collection

This directory contains all the data collection scripts for the AI Bubble Research project. Each script serves a specific purpose in collecting and processing financial and news data for AI-related companies.

## 📁 Scripts Overview

### 1. **`news_collector.py`** - Alpha Vantage News Collection
**Purpose**: Collect AI-related news articles using Alpha Vantage NEWS_SENTIMENT API

**Features**:
- Fetches news articles for each company ticker
- Dual categorization: broad tech news vs focused AI news
- Built-in sentiment analysis
- Premium API support (75 calls/minute)
- Resume capability (skips already processed companies)
- Ticker mapping for API compatibility (e.g., GOOGL → GOOG, FB → META)

**Input**: Company list from `../Tickers/merged_tickers.csv`

**Output**: `../news_data/av_news/{TICKER}_news.csv`

**Output Columns**:
```csv
ticker,title,url,time_published,source,summary,sentiment_score,sentiment_label,
ticker_sentiment_score,ticker_sentiment_label,relevance_score,category,ai_keywords_found
```

**Usage**:
```bash
python news_collector.py
```

---

### 2. **`sec_collector.py`** - SEC EDGAR Filings Collection
**Purpose**: Collect official company filings from SEC EDGAR database

**Features**:
- Fetches SEC filings (10-K, 10-Q, 8-K, DEF 14A) for US companies
- CIK (Central Index Key) mapping for US companies
- AI keyword search in filing content
- Handles international companies gracefully (skips non-US)
- Respectful rate limiting for SEC servers

**Input**: Company list from `../Tickers/merged_tickers.csv`

**Output**: `../news_data/sec_filings/{TICKER}_filings.csv`

**Output Columns**:
```csv
ticker,filing_type,filing_date,accession_number,filing_url,ai_mentions_count,
ai_keywords_found,ai_context_snippets,filing_title,status
```

**Usage**:
```bash
python sec_collector.py
```

---

### 3. **`merge_news_data.py`** - Data Consolidation
**Purpose**: Merge Alpha Vantage news and SEC filings into unified datasets

**Features**:
- Combines news articles and SEC filings for each company
- Deduplicates overlapping content
- Creates timeline of AI-related events
- Calculates aggregate metrics (sentiment trends, volume patterns)
- Handles partial data gracefully

**Input**: 
- Alpha Vantage news files from `../news_data/av_news/`
- SEC filings from `../news_data/sec_filings/`

**Output**: `../news_data/complete/{TICKER}_complete_news.csv`

**Output Columns**:
```csv
ticker,title,url,published_date,source,source_type,summary,sentiment_score,
sentiment_label,ticker_sentiment,ticker_sentiment_label,relevance_score,
category,ai_keywords_found,year,quarter,rolling_sentiment,ai_intensity,content_quality
```

**Usage**:
```bash
python merge_news_data.py
```

---

### 4. **`alphadata.py`** - Alpha Vantage Financial Data Collection
**Purpose**: Collect raw quarterly financial data from Alpha Vantage API

**Features**:
- Fetches 5 types of financial data per company:
  - Income Statement (revenue, profit, R&D expenses)
  - Earnings (EPS, surprises, estimates)
  - Balance Sheet (assets, liabilities, equity)
  - Cash Flow (operating cash flow, capital expenditures)
  - Historical Prices (for market cap calculation)
- Multi-API key rotation for higher capacity
- Historical market cap calculation using prices × shares outstanding
- **Modified**: Now saves only raw data + market cap (no calculated metrics)

**Input**: Company list from `../Tickers/merged_tickers.csv`

**Output**: `../alpha/{TICKER}_alpha_data.csv`

**Output Columns** (Raw Data Only):
```csv
ticker,fiscalDateEnding,totalRevenue,grossProfit,operatingIncome,netIncome,
researchAndDevelopment,ebitda,operatingCashflow,capitalExpenditures,
totalAssets,totalLiabilities,totalShareholderEquity,cashAndCashEquivalentsAtCarryingValue,
shortTermDebt,longTermDebt,commonStockSharesOutstanding,reportedEPS,estimatedEPS,
surprise,surprisePercentage,marketCap,stockPrice,sharesOutstanding,priceDate
```

**Usage**:
```bash
python alphadata.py
```

---

### 5. **`calculate_metrics.py`** - Financial Metrics Calculation
**Purpose**: Calculate financial metrics from raw Alpha Vantage data

**Features**:
- Reads all CSV files from `../alpha/` directory
- Calculates 11 comprehensive financial metrics:
  - Revenue Growth %
  - Net Income Margin %
  - EPS Surprise %
  - Free Cash Flow
  - Debt-to-Equity Ratio
  - Cash Ratio
  - R&D Intensity %
  - Buyback Ratio
  - P/E Ratio (using historical market cap)
  - P/S Ratio (using historical market cap)
  - Price-to-Book Ratio (using historical market cap)
- Combines all companies into a single comprehensive dataset
- Handles missing data gracefully with proper error checking

**Input**: CSV files from `../alpha/{TICKER}_alpha_data.csv`

**Output**: `../calculated_data/complete_data_with_metrics_{timestamp}.csv`

**Output Columns**:
```csv
ticker,fiscalDateEnding,totalRevenue,grossProfit,operatingIncome,netIncome,
researchAndDevelopment,ebitda,operatingCashflow,capitalExpenditures,
totalAssets,totalLiabilities,totalShareholderEquity,marketCap,stockPrice,
sharesOutstanding,revenueGrowthPct,netIncomeMarginPct,epsSurprisePct,
freeCashFlow,debtToEquityRatio,cashRatio,rdIntensityPct,buybackRatio,
peRatio,psRatio,priceToBookRatio
```

**Usage**:
```bash
python calculate_metrics.py
```

---

### 6. **`collect_complete_improved.py`** - Comprehensive Data Collection
**Purpose**: Collect complete dataset combining stock data, financials, and user metrics

**Features**:
- Fetches stock price data from Yahoo Finance
- Collects financial statements from SEC
- Extracts user metrics (MAU, DAU, subscribers) from filings
- Calculates financial ratios and metrics
- Handles both US and international companies

**Input**: Company list from `merged_tickers.csv`

**Output**: `../complete_data_improved/{TICKER}_complete.csv`

**Output Columns**:
```csv
date,open,high,low,close,volume,market_cap,revenue,gross_profit,net_income,
research_development,operating_cashflow,capital_expenditures,total_assets,
total_liabilities,shareholder_equity,mau,dau,subscribers,pe_ratio,ps_ratio,
pb_ratio,debt_to_equity,current_ratio,roe,roa,revenue_growth
```

**Usage**:
```bash
python collect_complete_improved.py
```

---

### 7. **`fix_market_cap.py`** - Market Cap Data Correction
**Purpose**: Fix market cap data in Alpha Vantage financial files

**Features**:
- Updates market cap values in `alphadata.py` output files
- Matches quarterly market cap data from `complete_data_improved` files
- Creates backups before modifying files
- Handles different ticker formats (international companies)

**Input**: 
- Alpha Vantage files from `../alpha/`
- Complete data files from `../complete_data_improved/`

**Output**: Updates existing `../alpha/{TICKER}_alpha_data.csv` files

**Usage**:
```bash
python fix_market_cap.py
```


---

## 🔧 Configuration

### Environment Variables (`.env` file)
```bash
# Alpha Vantage API Configuration
ALPHA_VANTAGE_API_KEYS=your_key_1,your_key_2,your_key_3

# Financial Data Configuration
START_YEAR=2015
END_YEAR=2025
RATE_LIMIT_DELAY=15

# News Collection Configuration
NEWS_START_YEAR=2015
NEWS_END_YEAR=2025
NEWS_RATE_LIMIT_DELAY=1

# SEC Configuration
SEC_USER_AGENT=YourName your.email@example.com
```

### Dependencies
All scripts require the packages listed in `../requirements.txt`:
- pandas, requests, yfinance, beautifulsoup4, python-dotenv, sec-edgar-downloader

---

## 📊 Data Flow

```
1. Company List (merged_tickers.csv)
   ↓
2. Financial Data Collection
   ├── alphadata.py → alpha/{TICKER}_alpha_data.csv (raw data + market cap)
   ├── calculate_metrics.py → calculated_data/complete_data_with_metrics_{timestamp}.csv
   ├── collect_complete_improved.py → complete_data_improved/{TICKER}_complete.csv
   └── fix_market_cap.py → Updates alpha files with market cap
   ↓
3. News Data Collection
   ├── news_collector.py → news_data/av_news/{TICKER}_news.csv
   ├── sec_collector.py → news_data/sec_filings/{TICKER}_filings.csv
   └── merge_news_data.py → news_data/complete/{TICKER}_complete_news.csv
   ↓
4. Analysis & Reporting
   └── analyze_news_trends.py → news_data/analysis/ (multiple files)
```

### 🔄 New Workflow (Separation of Concerns)
**Step 1**: Data Collection
- Run `alphadata.py` to collect raw financial data + market cap
- Output: Individual CSV files with raw data only

**Step 2**: Metrics Calculation  
- Run `calculate_metrics.py` to calculate all financial metrics
- Output: Combined dataset with all companies and calculated metrics

This separation allows for:
- ✅ Faster data collection (no calculation overhead)
- ✅ Flexible metrics calculation (can modify calculations without re-fetching data)
- ✅ Better error handling and debugging
- ✅ Ability to run calculations on existing data multiple times

---

## 🚀 Quick Start

### 1. Setup
```bash
cd /path/to/indicators
source DC/bin/activate  # Activate virtual environment
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Data Collection
```bash
# Financial data (new workflow)
python alphadata.py                    # Collect raw data + market cap
python calculate_metrics.py           # Calculate all financial metrics
python collect_complete_improved.py   # Additional comprehensive data
python fix_market_cap.py             # Fix market cap data

# News data
python news_collector.py
python sec_collector.py
python merge_news_data.py
```

### 4. Test International Companies (Optional)
```bash
python test_international_symbols.py
```

---

## 📈 Expected Outputs

After running all scripts, you'll have:

- **Financial Data**: ~100 CSV files with quarterly financial metrics
- **News Data**: ~60-160 CSV files with AI-related news articles
- **SEC Filings**: ~50 CSV files with official company filings
- **Merged Data**: ~100 CSV files with combined news and financial data
- **Analysis Files**: Summary statistics and trend analysis

---

## 🔍 Troubleshooting

### Common Issues

**API Rate Limits**:
- Financial data: 25 calls/day per key (free tier)
- News data: 75 calls/minute (premium tier)
- Scripts handle rotation automatically

**Missing Data**:
- Some international companies may not have data
- News coverage varies by company size and industry
- Scripts log missing data and continue processing

**Ticker Format Issues**:
- Use `test_international_symbols.py` to find correct formats
- Update ticker mappings in `news_collector.py` as needed

### Getting Help

1. Check script logs for specific error messages
2. Verify API keys and configuration in `.env` file
3. Test with a small subset of companies first
4. Review the generated CSV files for data quality

---

## 🔄 Recent Modifications

### Data Collection & Calculation Separation (Latest Update)
**Modified**: `alphadata.py` - Split into data collection and calculation phases

**Changes Made**:
1. **`alphadata.py`**: 
   - ✅ Removed `calculate_metrics()` function
   - ✅ Now saves only raw API data + historical market cap
   - ✅ Faster execution (no calculation overhead during API calls)
   - ✅ Cleaner separation of concerns

2. **`calculate_metrics.py`** (New):
   - ✅ Reads all raw data from `alpha/` directory
   - ✅ Calculates 11 comprehensive financial metrics
   - ✅ Combines all companies into single dataset
   - ✅ Saves to `calculated_data/` directory with timestamp

**Benefits**:
- 🚀 Faster data collection (API calls only)
- 🔧 Flexible metrics calculation (can modify without re-fetching)
- 🐛 Better debugging (separate data vs calculation issues)
- 📊 Reusable calculations on existing data

---

## 📝 Notes

- All scripts include comprehensive error handling and logging
- Progress is saved incrementally (resume capability)
- International companies may have limited data availability
- Some companies may not be available in all data sources
- Scripts are designed to handle missing data gracefully
