# Data Collection

This folder contains datasets and scripts for collecting and analyzing AI-related stock holdings data, specifically focused on the GlobalX AI & Innovation ETF (AIQ) holdings. The data collection spans from 2020 to 2025 and includes tools for data processing, analysis, and visualization.

## 📁 Folder Structure

```text
Data_collection/
├── README.md                                    # This file
├── downloading_GlobalX_AIQ_holdings_datasets_23_25.py  # Data downloader script
├── merge_tickers.py                             # Ticker consolidation script
├── tickers_IPO_analysis.ipynb                  # IPO analysis notebook
├── merged_tickers.csv                           # Consolidated ticker list (162 unique tickers)
├── merged_tickers_IPO.csv                       # Ticker list with IPO dates
├── aiq_holdings.zip                             # Compressed archive of all holdings data
└── aiq_holdings/                                # Raw daily holdings data (568 files)
    ├── aiq_20200808.csv
    ├── aiq_20200927.csv
    └── ... (daily files from 2020-2025)
```

## 🔧 Scripts and Tools

### 1. `downloading_GlobalX_AIQ_holdings_datasets_23_25.py`

**Purpose**: Downloads frequent holdings data from GlobalX AI & Innovation ETF

**Features**:

- Downloads holdings data from 2023-2025 (with some 2020-2022 data available)
- Fetches data from GlobalX official holdings API
- Creates compressed ZIP archive of all downloaded files
- Handles network errors and missing dates gracefully

**Usage**:

```bash
python downloading_GlobalX_AIQ_holdings_datasets_23_25.py
```

**Output**:

- Individual CSV files in `aiq_holdings/` folder
- Compressed `aiq_holdings.zip` archive

### 2. `merge_tickers.py`

**Purpose**: Consolidates all unique tickers from holdings files

**Features**:

- Processes all CSV files in the `aiq_holdings/` folder
- Skips header rows and extracts ticker symbols with company names
- Removes duplicates to create a master ticker list
- Handles file reading errors gracefully

**Usage**:

```bash
python merge_tickers.py
```

**Output**: `merged_tickers.csv` with 162 unique AI-related stock tickers

### 3. `tickers_IPO_analysis.ipynb`

**Purpose**: Jupyter notebook for analyzing IPO dates of ETF holdings

**Features**:

- Loads the merged ticker list
- Fetches IPO dates using Yahoo Finance API
- Standardizes ticker formats for different exchanges
- Creates visualizations of IPO date distributions
- Filters tickers based on listing dates for historical analysis

**Key Analysis Points**:

- Identifies recently listed companies
- Ensures sufficient historical data for trend analysis
- Maps ticker symbols to proper Yahoo Finance formats
- Generates IPO date distribution charts

## 📊 Data Description

### Holdings Data Format

Each daily holdings file (`aiq_YYYYMMDD.csv`) contains:

- **Ticker**: Stock symbol
- **Name**: Company name
- **Shares**: Number of shares held
- **Market Value**: USD value of holdings
- **Weight**: Percentage weight in ETF

### Ticker Data

- **162 unique tickers** representing AI and innovation companies
- Mix of US and international stocks (HK, KS, GR exchanges)
- Companies span various AI sectors: semiconductors, cloud computing, e-commerce, software

## 🎯 Research Applications

This data collection supports research into:

1. **AI Bubble Analysis**: Tracking valuation trends in AI-focused investments
2. **Portfolio Composition Changes**: How AI ETF holdings evolve over time
3. **Market Concentration**: Analysis of top holdings and diversification
4. **IPO Impact Studies**: Performance of recently listed AI companies
5. **Cross-Market Analysis**: International AI stock performance comparison

## 📈 Data Timeline

- **Primary Period**: 2023-2025 (daily data)
- **Extended Period**: Some 2020-2022 data available (obtained via Wayback Machine)
- **Total Files**: 568 daily holdings snapshots
- **Data Sources**:
  - 2023-2025: GlobalX AI & Innovation ETF (AIQ) official holdings API
  - 2020-2022: Historical data retrieved from Wayback Machine archived pages

## 🔄 Data Updates

The data collection can be extended by:

1. Running the download script with updated date ranges
2. Re-running the ticker merge process to capture new holdings
3. Updating IPO analysis for newly added companies

## 📋 Dependencies

- **Python 3.7+**
- **pandas**: Data manipulation
- **requests**: HTTP requests for data download
- **yfinance**: Stock data and IPO information
- **matplotlib**: Visualization (for notebook)
- **zipfile**: Archive creation

## 🚀 Getting Started

1. **Install dependencies**:

   ```bash
   pip install pandas requests yfinance matplotlib
   ```

2. **Download latest holdings data**:

   ```bash
   python downloading_GlobalX_AIQ_holdings_datasets_23_25.py
   ```

3. **Create consolidated ticker list**:

   ```bash
   python merge_tickers.py
   ```

4. **Analyze IPO dates** (optional):
   Open and run `tickers_IPO_analysis.ipynb` in Jupyter

## 📝 Notes

- Holdings data reflects the actual composition of the GlobalX AI & Innovation ETF
- Some international tickers may require format adjustments for Yahoo Finance compatibility
- Data availability depends on GlobalX server availability and market trading days
- The ETF composition changes over time, so ticker lists may vary between periods
