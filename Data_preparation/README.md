# Data Preparation & Processing

This directory contains the complete data preparation pipeline for AI bubble research, transforming raw financial data into analysis-ready datasets.

## Directory Structure

```text
Data_preparation/
├── scripts/                 # Processing scripts
│   ├── preprocess_datasets.py   # Step 1: Combine raw Excel files
│   ├── clean_datasets.py        # Step 2: Filter columns & dates
│   ├── currency_conversion.py   # Step 3: Convert to USD
│   └── README.md
└── datasets/                # Data at various processing stages
    ├── preprocessed_data/   # Combined financial statements by currency
    ├── cleaned_data/        # Filtered 33 columns, 2015-2025
    ├── normalized_data/     # USD-converted, analysis-ready
    └── README.md
```

## Processing Pipeline

### 1. Preprocessing Stage

**Script**: `scripts/preprocess_datasets.py`
**Input**: Raw Excel files from stock_analysis directories
**Output**: `datasets/preprocessed_data/`

- Combines 4 Excel files per company (Income Statement, Balance Sheet, Cash Flow, Key Metrics)
- Transposes data structure for time-series analysis
- Maintains currency-based folder organization
- Preserves all original financial metrics

### 2. Cleaning Stage

**Script**: `scripts/clean_datasets.py`
**Input**: `datasets/preprocessed_data/`
**Output**: `datasets/cleaned_data/`

- Filters to 33 standardized financial columns
- Restricts date range to 2015-2025
- Standardizes column naming across all files
- Maintains currency folder structure

### 3. Normalization Stage

**Script**: `scripts/currency_conversion.py`
**Input**: `datasets/cleaned_data/`
**Output**: `datasets/normalized_data/`

- Converts all currencies to USD using October 2025 rates
- Combines all currency folders into single directory
- Preserves original currency information
- Creates analysis-ready dataset

## Key Datasets

### Final Output: normalized_data/

- **153 companies** in standardized USD format
- **33 financial columns** spanning market valuation to capital structure
- **2015-2025 timeframe** for consistent analysis
- **Single currency** (USD) for cross-company comparisons

### Supported Currencies

- **USD** (133 companies) - Base currency
- **EUR** (4 companies) - European AI firms
- **HKD, JPY, KRW, SEK, TWD, CHF** (16 companies) - Asia-Pacific and other markets

## Quick Start

Run the complete pipeline:

```bash
# Navigate to scripts directory
cd scripts/

# Run pipeline in sequence
python preprocess_datasets.py
python clean_datasets.py
python currency_conversion.py
```

## Data Quality Features

- **Error Handling**: Minimal debugging with continue-on-error processing
- **File Preservation**: Original filenames maintained throughout pipeline
- **Currency Tracking**: Original currency preserved in final dataset
- **Standardization**: Consistent 33-column format for all companies
