# Data Preparation Datasets

This directory contains datasets at various stages of processing for AI bubble research analysis.

## Directory Structure

### preprocessed_data/

**Purpose**: Raw financial data combined and structured by company
**Source**: Output from `scripts/preprocess_datasets.py`
**Organization**: Currency-based folder structure (USD, EUR, HKD, JPY, KRW, SEK, TWD, CHF)

**Content**:

- Combined financial statements per company (Income Statement, Balance Sheet, Cash Flow, Key Metrics)
- Date-indexed rows with comprehensive financial metrics
- Original currency values preserved
- File count: ~155 companies across 8 currencies

**Structure**:

```text
preprocessed_data/
├── USD/ (133 files)
├── EUR/ (4 files)
├── HKD/ (2 files)
├── JPY/ (4 files)
├── KRW/ (3 files)
├── SEK/ (1 file)
├── TWD/ (7 files)
└── CHF/ (1 file)
```

**File Format**: Excel (.xlsx) with 100+ columns of financial data spanning 1990s-2025

### cleaned_data/

**Purpose**: Standardized datasets with filtered columns and date range
**Source**: Output from `scripts/clean_datasets.py`
**Organization**: Same currency folder structure as preprocessed_data

**Content**:

- 33 standardized financial columns only
- Date range filtered to 2015-2025
- Consistent column naming across all files
- Missing data handling applied

**Key Columns** (33 total):

- **Identifiers**: Ticker, Currency, Date
- **Market Valuation**: Market Capitalization, Enterprise Value, PE Ratio, PS Ratio, PB Ratio, P/FCF Ratio
- **Fundamentals**: Revenue, Revenue Growth, Gross Margin, Operating Income, Operating Margin
- **Profitability**: Net Income, Net Income Growth, EPS (Diluted), EPS Growth, EBITDA
- **Cash Flow**: Operating Cash Flow, Capital Expenditures, Free Cash Flow, Free Cash Flow Margin
- **Returns**: Total Return, ROE, ROA, ROIC
- **Capital Structure**: Total Debt, Net Cash (Debt), Debt/Equity, Buyback Yield
- **Investment**: Research & Development, Share-Based Compensation

**Structure**: Same as preprocessed_data but with filtered content

### normalized_data/

**Purpose**: Final analysis-ready dataset with all currencies converted to USD
**Source**: Output from `scripts/currency_conversion.py`
**Organization**: Single folder (no currency subfolders)

**Content**:

- All financial data converted to USD using October 2025 exchange rates
- Original currency preserved in "Original Currency" column
- 153 companies total (all currencies combined)
- Ready for cross-company analysis and valuation comparisons

**Features**:

- **Unified Currency**: All monetary values in USD
- **Original Currency Tracking**: "Original Currency" column preserves source currency
- **Updated Currency Column**: "Currency" column set to "USD" for all records
- **Exchange Rate Applied**: 14 monetary columns converted using accurate rates

**File Count**: 153 Excel files (combined from all currency folders)

## Data Quality Notes

### Coverage

- **Time Range**: 2015-2025 (cleaned and normalized datasets)
- **Geographic Coverage**: 8 currencies representing major AI markets
- **Company Coverage**: 153 AI-related companies from various sectors

### Data Processing Pipeline

1. **Preprocessing**: Raw Excel files → Combined financial statements
2. **Cleaning**: Full dataset → 33 standardized columns + date filtering
3. **Normalization**: Multi-currency → USD standardized

### Exchange Rates Used

**October 2025 rates applied to normalized_data**:

- EUR: 1.157 USD
- HKD: 0.1287 USD
- JPY: 0.00650 USD
- KRW: 0.000699 USD
- SEK: 0.1060 USD
- TWD: 0.0325 USD
- CHF: 1.248 USD

### Usage Recommendations

- **Analysis**: Use `normalized_data/` for cross-company comparisons
- **Currency-Specific**: Use `cleaned_data/` for regional analysis
- **Development**: Use `preprocessed_data/` for pipeline testing

### File Naming Convention

Files maintain consistent naming throughout pipeline:

- Example: `ADOBE_INC.xlsx` → same name in all three directories
- Company names preserve original stock_analysis formatting
- No currency prefixes added to filenames

## Dependencies

- **Source Data**: Stock analysis Excel files organized by currency
- **Processing Scripts**: preprocess_datasets.py → clean_datasets.py → currency_conversion.py
- **Requirements**: pandas, openpyxl for Excel processing
