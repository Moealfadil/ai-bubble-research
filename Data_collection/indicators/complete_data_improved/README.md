# Complete Data - Final Results

**Collection Date:** October 9, 2025  
**Companies:** 126 / 160 (78.8% success rate)  
**Data Records:** 14,691 monthly records (2015-2025)

---

## 📁 Files in This Folder

### 🎯 Main Files (Use These!)

1. **`ALL_COMPANIES_FINAL_CONSOLIDATED_20251009_141611.csv`** ⭐
   - **The master dataset** - contains all data for all companies
   - 14,691 rows × 37 columns
   - One row per company per month
   - Includes: prices, market cap, financials, user metrics
   - **START HERE** for your analysis

2. **`FINAL_COMBINED_SUMMARY_20251009_141540.csv`**
   - Summary of all 126 collected companies
   - Shows which companies have user metrics
   - Record counts for each company

### 📊 Individual Company Files

- `[TICKER]_complete.csv` - 133 separate files
- Each contains full historical data for one company
- Use these if you want to focus on specific companies
- Examples:
  - `NFLX_complete.csv` - Netflix with subscriber data
  - `NVDA_complete.csv` - Nvidia (40,000% growth!)
  - `META_complete.csv` - Meta/Facebook

### 📝 Processing Summaries

- `FULL_SUMMARY_20251009_110710.csv` - Original batch (101 companies)
- `MISSING_SUMMARY_20251009_141439.csv` - Second batch (25 companies)

---

## 📊 Data Structure

### Columns (37 total)

#### Basic Information (6)
- `ticker` - Stock ticker symbol
- `company_name` - Full company name
- `date` - Record date (monthly)
- `year`, `quarter`, `month` - Date components

#### Stock Data (8)
- `close_price`, `open_price`, `high_price`, `low_price`
- `volume` - Trading volume
- `shares_outstanding` - Total shares issued
- `market_cap` - Market capitalization ($)
- `market_cap_billions` - Market cap in billions

#### Financial Data (5)
- `revenue` - Quarterly revenue ($)
- `revenue_millions` - Revenue in millions
- `gross_profit`, `net_income`, `operating_income`
- `ebitda` - Earnings before interest, taxes, depreciation

#### Valuation Ratios (6)
- `ps_ratio` - Historical Price-to-Sales
- `current_pe` - Current P/E ratio
- `forward_pe` - Forward P/E ratio
- `current_ps` - Current P/S ratio
- `current_pb` - Price-to-Book ratio
- `peg_ratio` - PEG ratio

#### Growth Metrics (3)
- `revenue_qoq_pct` - Revenue quarter-over-quarter %
- `revenue_yoy_pct` - Revenue year-over-year %
- `market_cap_yoy_pct` - Market cap YoY %

#### User Metrics (3) 👥
- `user_subscribers_millions` - Subscriber count
- `user_dau_millions` - Daily Active Users
- `user_mau_millions` - Monthly Active Users

#### Company Metadata (4)
- `sector`, `industry`, `country`, `employees`

---

## 👥 Companies with User Metrics (10)

✅ **Successfully extracted user data for:**

1. **ADBE** - Adobe Inc
   - Subscribers: 50M → 100M (+100%)

2. **DOCU** - DocuSign Inc
   - Subscribers: 4M

3. **FTNT** - Fortinet Inc
   - Subscribers: 994M + DAU data

4. **HUBB** - Hubbell Inc
   - Subscribers: 88M

5. **HUT** - Hut 8 Corp
   - Subscribers: 41M + MAU data

6. **MSFT** - Microsoft Corp
   - Subscribers: 82.5M

7. **NFLX** - Netflix Inc ⭐
   - Subscribers: 260M → 302M (+16%)
   - Full historical subscriber data

8. **QCOM** - Qualcomm Inc
   - DAU: 3M

9. **STX** - Seagate Technology
   - Subscribers: 9.7M + DAU data

10. **VRNT** - Verint Systems Inc
    - Subscribers: 0.4M

---

## 🚀 Quick Start

### Load the Data

```python
import pandas as pd

# Load master dataset
df = pd.read_csv('ALL_COMPANIES_FINAL_CONSOLIDATED_20251009_141611.csv')
df['date'] = pd.to_datetime(df['date'])

print(f"Companies: {df['ticker'].nunique()}")
print(f"Records: {len(df):,}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
```

### Example 1: Netflix Analysis

```python
# Get Netflix data
nflx = df[df['ticker'] == 'NFLX'].copy()

# Plot subscribers vs stock price
import matplotlib.pyplot as plt

fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.plot(nflx['date'], nflx['close_price'], 'b-', label='Stock Price')
ax1.set_ylabel('Stock Price ($)', color='b')

ax2 = ax1.twinx()
ax2.plot(nflx['date'], nflx['user_subscribers_millions'], 'r-', label='Subscribers (M)')
ax2.set_ylabel('Subscribers (Millions)', color='r')

plt.title('Netflix: Stock Price vs Subscribers')
plt.show()
```

### Example 2: Find Bubble Candidates

```python
# Get latest data for each company
latest = df.sort_values('date').groupby('ticker').last()

# Find high P/S ratios (potential bubble)
bubble_candidates = latest[latest['current_ps'] > 10].sort_values('current_ps', ascending=False)

print("Potential Bubble Companies (P/S > 10x):")
print(bubble_candidates[['company_name', 'current_ps', 'market_cap_billions']])
```

### Example 3: Growth Analysis

```python
# Calculate total growth for each company
growth = []

for ticker in df['ticker'].unique():
    ticker_data = df[df['ticker'] == ticker].sort_values('date')
    
    if len(ticker_data) < 12:  # Need at least 1 year
        continue
    
    first_price = ticker_data['close_price'].iloc[0]
    last_price = ticker_data['close_price'].iloc[-1]
    
    if pd.notna(first_price) and pd.notna(last_price):
        growth_pct = ((last_price - first_price) / first_price) * 100
        
        growth.append({
            'ticker': ticker,
            'name': ticker_data['company_name'].iloc[0],
            'growth_pct': growth_pct
        })

growth_df = pd.DataFrame(growth).sort_values('growth_pct', ascending=False)
print(growth_df.head(15))
```

---

## 📈 Key Insights

### Highest Valuations (Bubble Risk?)
1. **NVDA** - 27.9x P/S, +40,946% growth
2. **AVGO** - 27.2x P/S, +4,338% growth
3. **TSLA** - 15.7x P/S, +3,132% growth
4. **ORCL** - 13.9x P/S
5. **MSFT** - 13.8x P/S

### Lowest Valuations (Value?)
1. **TSM** - 0.5x P/S
2. **Rakuten** - 0.9x P/S
3. **Meituan** - 1.8x P/S
4. **Samsung** - 1.9x P/S

### User Growth Observations
- **Netflix**: Slowing growth (16% total increase)
- **Adobe**: Doubling subscribers (100% increase)
- Most companies don't report user metrics publicly

---

## ⚠️ Data Limitations

1. **Revenue data**: Only 4-5 years available (Yahoo Finance API)
2. **User metrics**: Limited to 10 US companies with SEC filings
3. **International companies**: No SEC filings, so no user data
4. **Some tickers**: 34 companies failed (M&A, delisting, data issues)

---

## 📚 Additional Documentation

- **`../DATA_COLLECTION_FINAL_REPORT.md`** - Full methodology and analysis
- **`../quick_analysis.py`** - Script to analyze the data
- **`../collect_complete_improved.py`** - Collection script (if you want to rerun)

---

## 🎯 Recommended Analysis

1. **Bubble Detection**
   - Compare P/S ratios to historical norms
   - Identify unsustainable valuations
   - Correlate with revenue growth

2. **User Validation**
   - Check if user growth matches market cap growth
   - Calculate revenue per user
   - Identify user growth deceleration

3. **Sector Analysis**
   - Compare valuations within sectors
   - Find outliers
   - Identify bubble sectors

4. **Risk Assessment**
   - High P/S + slowing user growth = high risk
   - High P/S + accelerating users = justified?
   - Low P/S + strong revenue = opportunity?

---

**🎉 You're ready to analyze the AI bubble!**

For questions or issues, see the main documentation in:
`../DATA_COLLECTION_FINAL_REPORT.md`

