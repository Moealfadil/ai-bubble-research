# Data Preparation Scripts

This directory contains Python scripts for processing and transforming financial datasets from raw to analysis-ready format.

## Scripts Overview

### 1. preprocess_datasets.py

**Purpose**: Processes raw Excel files from stock_analysis directory structure

- **Input**: Excel files organized by currency folders (USD, EUR, HKD, JPY, KRW, SEK, TWD, CHF)
- **Process**: Transposes data from rows to columns, combines multiple Excel files per company, adds ticker and currency columns
- **Output**: Preprocessed Excel files in `datasets/preprocessed_data/` maintaining currency folder structure

**Key Features**:

- Handles 4 Excel files per company (Income Statement, Balance Sheet, Cash Flow, Key Metrics)
- Preserves date-based row structure while combining financial metrics
- Robust error handling for missing files or data inconsistencies

### 2. clean_datasets.py

**Purpose**: Filters preprocessed datasets to standardized columns and date range

- **Input**: Preprocessed Excel files from `datasets/preprocessed_data/`
- **Process**: Selects 33 specific financial columns, filters to 2015-2025 date range
- **Output**: Cleaned Excel files in `datasets/cleaned_data/` with same currency structure

**Column Selection** (33 columns):

- Identifiers: Ticker, Currency, Date
- Market Valuation: Market Cap, Enterprise Value, PE/PS/PB Ratios
- Fundamentals: Revenue, Operating Income, Net Income, Cash Flow metrics
- Performance: ROE, ROA, ROIC, margins and growth rates
- Capital Structure: Debt metrics, R&D spending, share-based compensation

### 3. currency_conversion.py

**Purpose**: Converts all financial data to USD for consistent analysis

- **Input**: Cleaned Excel files from `datasets/cleaned_data/`
- **Process**: Applies exchange rates to monetary columns, standardizes to USD
- **Output**: Normalized Excel files in `datasets/normalized_data/` (single folder, all USD)

**Exchange Rates** (October 2025):

- EUR: 1.157 USD
- HKD: 0.1287 USD
- JPY: 0.00650 USD
- KRW: 0.000699 USD
- SEK: 0.1060 USD
- TWD: 0.0325 USD
- CHF: 1.248 USD

**Converted Columns** (14 monetary columns):

- Market metrics: Market Cap, Enterprise Value
- Income: Revenue, Operating Income, Net Income, EBITDA
- Cash Flow: Operating CF, CapEx, Free Cash Flow
- Capital: Total Debt, Net Cash/Debt, R&D, Share-based Comp
- Per-share: EPS (Diluted)

### 4. adding_missing_columns.py

**Purpose**: Enriches normalized data with calculated metrics and daily price data

- **Input**: Normalized Excel files from `datasets/normalized_data/` + Complete price data from `Data_collection/indicators/complete_data_improved/`
- **Process**: Calculates valuation ratios, merges date-matched price data with currency conversion
- **Output**: Final analysis-ready Excel files in `datasets/final_data/`

**Added Calculated Columns** (4 columns):

- **PEG Ratio**: PE Ratio / (EPS Growth × 100) - valuation metric normalized by growth
- **R&D % of Revenue**: Research & Development / Revenue - R&D intensity
- **R&D to Market Cap**: Research & Development / Market Capitalization - R&D spending relative to company size
- **EPS Growth % (used)**: Normalized EPS Growth percentage (handles decimal/percentage formats)

**Added Price Data Columns** (6 columns):

- **open_price, close_price, high_price, low_price**: Daily stock prices (USD-converted, date-matched)
- **shares_outstanding**: Number of shares outstanding
- **fixed_ticker**: Standardized ticker symbol from price data source

**Key Features**:

- Date-based nearest-neighbor matching between quarterly financials and daily prices
- Automatic currency conversion for international stocks (KRW, JPY, EUR, etc. → USD)
- Fuzzy company name matching between normalized files and price data CSVs
- Handles missing data gracefully (adds NaN for unmatched companies)
- Prices positioned immediately after Date column for easy analysis

**Matching Logic**:

- Filename → Company name conversion (underscores to spaces)
- Normalized alphanumeric matching against CSV "company_name" column
- Fuzzy fallback for partial matches
- **Note**: 3-4 companies may not match due to name differences (e.g., "Splunk Inc", "Tencent Holdings Ltd")

## Data Pipeline Flow

```text
Raw Stock Analysis Data
         ↓
   preprocess_datasets.py
         ↓
   Preprocessed Data (by currency)
         ↓
   clean_datasets.py
         ↓
   Cleaned Data (33 columns, 2015-2025)
         ↓
   currency_conversion.py
         ↓
   Normalized Data (USD only)
         ↓
   adding_missing_columns.py
         ↓
   Final Data (with PEG, R&D ratios, prices)
```

## Usage

### Run Individual Scripts

```bash
# Step 1: Preprocess raw data
python preprocess_datasets.py

# Step 2: Clean and filter data
python clean_datasets.py

# Step 3: Convert currencies to USD
python currency_conversion.py

# Step 4: Add calculated metrics and price data
python adding_missing_columns.py
```

### Command-Line Options (adding_missing_columns.py)

```bash
# Run with default paths
python adding_missing_columns.py

# Specify custom paths
python adding_missing_columns.py \
  --normalized "path/to/normalized_data" \
  --complete "path/to/complete_data_improved" \
  --out "path/to/final_data"

# Dry run (validate without writing files)
python adding_missing_columns.py --dry-run
```

### File Naming Convention

- **Input**: Company names as they appear in stock_analysis folders
- **Output**: Same filenames preserved throughout pipeline
- **Example**: `ADOBE_INC.xlsx` → `ADOBE_INC.xlsx` (content transformed, name unchanged)

## Requirements

- Python 3.9+
- pandas
- openpyxl
- Excel files in expected directory structure

## Error Handling

All scripts include minimal error handling to:

- Report problematic files without stopping processing
- Continue processing remaining files if individual files fail
- Provide basic debugging information for troubleshooting

## Output Validation

- **Preprocessed**: Combined financial statements with proper date indexing
- **Cleaned**: Standardized 33-column format with 2015-2025 data only
- **Normalized**: All monetary values in USD with original currency preserved
- **Final**: 43 total columns including PEG ratio, R&D metrics, and date-matched daily prices in USD
