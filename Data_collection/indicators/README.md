# Financial Indicators Data Collection

This directory contains scripts and data for collecting comprehensive financial indicators from AI companies to analyze their fundamental performance and validate business sustainability. The data collection focuses on quarterly financial statements and key performance metrics to assess whether AI companies have strong fundamentals or are potentially overvalued.

## 📁 Folder Structure

```text
indicators/
├── README.md                                    # This file
├── requirements.txt                             # Python dependencies
├── scripts/                                     # Data collection scripts
│   ├── alphadata.py                            # Main Alpha Vantage data collector
│   ├── collect_complete_improved.py            # Enhanced data collection script
│   └── fix_market_cap.py                       # Market cap data correction utility
├── alpha/                                       # Alpha Vantage financial data output
│   ├── AAPL_alpha_data.csv                     # Apple financial data
│   ├── NVDA_alpha_data.csv                     # NVIDIA financial data
│   └── ... (160 company files)
├── complete_data_improved/                     # Enhanced complete datasets
│   └── ... (139 company files with market cap data)
├── DC/                                          # Data collection environment
│   └── ... (Python virtual environment)
├── stock_analysis/                              # Financial statement analysis data
│   ├── USD/                                     # US Dollar companies
│   │   ├── APPLE INC/                          # Apple financial statements
│   │   ├── MICROSOFT CORP/                     # Microsoft financial statements
│   │   └── ... (130+ US companies)
│   ├── EUR/                                     # Euro companies
│   │   ├── INFINEON TECHNOLOGIES AG/           # German semiconductor company
│   │   ├── SIEMENS ENERGY AG NPV/              # German energy company
│   │   └── ... (additional European companies)
│   ├── JPY/                                     # Japanese Yen companies
│   │   ├── FUJITSU LIMITED/                    # Japanese technology company
│   │   ├── NEC CORP/                           # Japanese electronics company
│   │   └── ... (additional Japanese companies)
│   ├── HKD/                                     # Hong Kong Dollar companies
│   │   ├── TENCENT HOLDINGS LTD/               # Chinese tech giant
│   │   └── MEITUAN DIANPING-CLASS B/           # Chinese food delivery company
│   ├── KRW/                                     # Korean Won companies
│   │   ├── Samsung Electronics/                # Korean electronics giant
│   │   └── SK HYNIX INC/                       # Korean memory chip company
│   ├── TWD/                                     # Taiwanese Dollar companies
│   │   ├── ACER INC/                           # Taiwanese computer company
│   │   ├── ADVANTECH CO LTD/                   # Taiwanese industrial computer company
│   │   └── ... (additional Taiwanese companies)
│   ├── CHF/                                     # Swiss Franc companies
│   │   └── TEMENOS AG - REG/                  # Swiss banking software company
│   ├── SEK/                                     # Swedish Krona companies
│   │   └── ERICSSON (LM) TEL-SP ADR/           # Swedish telecom equipment company
│   └── README.md                               # Stock analysis documentation
└── docs/                                        # Documentation and guides
    ├── ALPHADATA_README.md                     # Alpha Vantage setup guide
    ├── ALPHADATA_QUICKSTART.md                 # Quick start instructions
    └── ... (additional documentation)
```

## Scripts and Tools

### 1. `scripts/alphadata.py` - Main Financial Data Collector

**Purpose**: Collects comprehensive quarterly financial data from Alpha Vantage API for AI companies

**Features**:
- **Multi-API Key Rotation**: Uses multiple API keys to maximize daily data collection capacity
- **Rate Limiting**: Implements 15-second delays to respect API limits
- **Comprehensive Data Collection**: Fetches 4 data types per company:
  - Income Statement (quarterly revenue, profit, R&D expenses)
  - Earnings (EPS, surprises, estimates)
  - Balance Sheet (assets, liabilities, equity, cash)
  - Cash Flow (operating cash flow, capital expenditures, buybacks)
- **Market Cap Integration**: Loads quarter-matched market cap data from existing datasets
- **Automatic Resume**: Skips already processed companies, continues from where it left off
- **Error Handling**: Graceful handling of API errors and missing data

**Data Output**: Creates individual CSV files for each company with calculated financial metrics

### 2. `scripts/collect_complete_improved.py` - Enhanced Data Collection

**Purpose**: Alternative data collection script with improved market cap matching

**Features**:
- Enhanced market cap data integration
- Improved quarter matching algorithms
- Better handling of international tickers

### 3. `stock_analysis/` - Financial Statement Analysis Data

**Purpose**: Contains detailed quarterly financial statements for international AI companies organized by currency

**Structure**:
- **Multi-Currency Organization**: Data organized by reporting currency (USD, EUR, JPY, HKD, KRW, TWD, CHF, SEK)
- **Comprehensive Financial Statements**: Each company includes 4 Excel files:
  - Balance Sheet (quarterly assets, liabilities, equity)
  - Income Statement (quarterly revenue, expenses, profit)
  - Cash Flow Statement (quarterly operating, investing, financing cash flows)
  - Financial Ratios (calculated quarterly ratios and metrics)
- **International Coverage**: Companies from major global markets including US, Europe, Asia-Pacific
- **Quarterly Data**: Detailed quarterly financial data for fundamental analysis

**Use Cases**:
- Deep-dive fundamental analysis of individual companies
- Cross-border financial comparison and analysis
- Currency-specific market analysis
- Detailed ratio analysis and trend identification

## Financial Metrics Collected

When you run `alphadata.py`, you obtain comprehensive quarterly financial data including:

### Revenue & Growth Metrics
- **Total Revenue** - Quarterly revenue figures
- **Revenue Growth (%)** - Quarter-over-quarter growth rates
- **Net Income Margin (%)** - Profitability as percentage of revenue

### Profitability Indicators
- **Gross Profit** - Revenue minus cost of goods sold
- **Operating Income** - Core business profitability
- **Net Income** - Bottom-line profit
- **EBIT/EBITDA** - Earnings before interest, taxes, depreciation, amortization

### Cash Flow Analysis
- **Operating Cash Flow** - Cash generated from core operations
- **Free Cash Flow** - Operating cash flow minus capital expenditures
- **Capital Expenditures** - Investment in property, plant, equipment
- **Dividend Payouts** - Cash returned to shareholders

### Balance Sheet Health
- **Total Assets** - Company's total resources
- **Total Liabilities** - Company's total debts
- **Shareholder Equity** - Net worth
- **Cash & Cash Equivalents** - Liquid assets
- **Debt-to-Equity Ratio** - Financial leverage indicator

### Valuation Metrics (with Market Cap)
- **P/E Ratio** - Price-to-earnings ratio
- **P/S Ratio** - Price-to-sales ratio
- **Market Cap** - Total company valuation (quarter-matched)

### Innovation & Growth Indicators
- **R&D Intensity (%)** - Research spending as percentage of revenue
- **EPS Surprise (%)** - Actual vs estimated earnings performance
- **Buyback Ratio** - Share repurchase activity relative to net income

## Getting Started

### Step 1: Install Dependencies

```bash
cd ai-bubble-research/Data_collection/indicators
pip install -r requirements.txt
```

### Step 2: Set Up API Keys

1. **Get Alpha Vantage API Keys**:
   - Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - Sign up for free (25 calls/day per key)
   - Get multiple keys for higher daily capacity

2. **Create Environment File**:
   ```bash
   cp .env.example .env
   ```

3. **Add Your API Keys**:
   Edit `.env` file and add your keys:
   ```bash
   ALPHA_VANTAGE_API_KEYS=your_key_1,your_key_2,your_key_3,your_key_4
   ```

4. **Optional Configuration**:
   You can also customize other settings in `.env`:
   ```bash
   START_YEAR=2015
   END_YEAR=2025
   RATE_LIMIT_DELAY=15
   ```

### Step 3: Run Financial Data Collection

```bash
python scripts/alphadata.py
```

This will:
- Process all 160 companies from the merged tickers list
- Fetch quarterly financial data from 2015-2025
- Calculate comprehensive financial metrics
- Save individual CSV files for each company
- Handle API rate limits automatically
- Resume from where it left off if interrupted

### Step 4: Review Collected Data

After completion, you'll have:
- **160 individual company files** in `alpha/` directory
- **Quarterly financial data** spanning 2015-2025 or from the time the company was listed
- **Calculated metrics** including growth rates, ratios, and valuations
- **Market cap integration** for accurate P/E and P/S calculations

## Data Sources

- **Primary**: Alpha Vantage API (financial statements)
- **Secondary**: Existing market cap datasets in `complete_data_improved/`
- **Coverage**: 160 AI-related companies from GlobalX AIQ ETF holdings
- **Timeframe**: Quarterly data from 2015-2025

## Research Applications

This financial data collection supports research into:

1. **AI Bubble Analysis**: Identifying overvalued companies through fundamental analysis
2. **Revenue Validation**: Distinguishing real businesses from hype through revenue metrics
3. **Growth Pattern Analysis**: Understanding sustainable vs unsustainable growth
4. **Cash Flow Analysis**: Identifying companies burning cash vs generating cash
5. **R&D Investment Analysis**: Understanding innovation spending patterns
6. **Valuation Metrics**: P/E and P/S ratio analysis across AI companies

## API Management

The script includes sophisticated API management:
- **Multiple API Keys**: Rotates automatically when limits reached
- **Rate Limiting**: 15-second delays between calls
- **Daily Limits**: 25 calls per key per day (free tier)
- **Progress Tracking**: Shows API usage statistics
- **Automatic Pause**: Stops when all keys exhausted, resumes next day

## Output File Format

Each company file (`TICKER_alpha_data.csv`) contains:
- **ticker**: Company symbol
- **fiscalDateEnding**: Quarter end date
- **Financial Data**: Revenue, profit, cash flow, balance sheet items
- **Calculated Metrics**: Growth rates, ratios, margins
- **Market Cap**: Quarter-matched valuation data

## Security Notes

- **API Keys**: Never commit your `.env` file to version control
- **Environment Variables**: The `.env` file is automatically ignored by git
- **Key Rotation**: Use multiple API keys to distribute load and avoid limits
- **Free Tier**: Each key allows 25 calls/day, so 4 keys = 100 calls/day capacity

## Troubleshooting

### API Key Issues
- **Missing Keys**: Ensure `.env` file exists and contains `ALPHA_VANTAGE_API_KEYS`
- **Invalid Keys**: Check that keys are valid and not expired
- **Format**: Keys should be comma-separated without spaces: `key1,key2,key3`

### API Rate Limiting
- Script automatically handles rate limits
- Shows progress and remaining capacity
- Pauses when all keys exhausted, resumes next day

### Missing Data
- Some companies may have limited financial history
- International companies may have different reporting standards
- Script saves partial data when available

### File Management
- Creates backup files before overwriting
- Skips already processed companies
- Maintains progress across multiple runs
