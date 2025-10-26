# Stock Analysis Data

## Data Source

This directory contains raw financial data obtained from [StockAnalysis.com](https://stockanalysis.com), a comprehensive financial data platform that provides accurate information on over 100,000+ stocks and funds.

## Dataset Overview

This dataset contains financial statements and ratios for **160 companies** listed in the `merged_tickers.csv` file. The companies span multiple currencies and markets including:

- **USD**: US-based companies (majority of the dataset)
- **EUR**: European companies 
- **JPY**: Japanese companies
- **KRW**: Korean companies
- **HKD**: Hong Kong companies
- **TWD**: Taiwanese companies
- **SEK**: Swedish companies

## Data Structure

Each company has four types of financial data files:

1. **Balance Sheet Quarterly** (`{ticker}-balance-sheet-quarterly.xlsx`)
   - Assets, liabilities, and equity data
   - Quarterly reporting periods

2. **Cash Flow Statement Quarterly** (`{ticker}-cash-flow-statement-quarterly.xlsx`)
   - Operating, investing, and financing cash flows
   - Quarterly reporting periods

3. **Income Statement Quarterly** (`{ticker}-income-statement-quarterly.xlsx`)
   - Revenue, expenses, and profit metrics
   - Quarterly reporting periods

4. **Ratios Quarterly** (`{ticker}-ratios-quarterly.xlsx`)
   - Financial ratios and key performance indicators
   - Quarterly reporting periods

## Directory Structure

```
stock_analysis/
├── USD/           # US Dollar companies
│   ├── APPLE INC/
│   ├── MICROSOFT CORP/
│   └── ...
├── EUR/           # Euro companies
│   ├── INFINEON TECHNOLOGIES AG/
│   └── ...
├── JPY/           # Japanese Yen companies
│   ├── FUJITSU LIMITED/
│   └── ...
├── KRW/           # Korean Won companies
│   ├── Samsung Electronics/
│   └── ...
├── HKD/           # Hong Kong Dollar companies
│   ├── TENCENT HOLDINGS LTD/
│   └── ...
├── TWD/           # Taiwanese Dollar companies
│   ├── ACER INC/
│   └── ...
└── SEK/           # Swedish Krona companies
    └── ERICSSON (LM) TEL-SP ADR/
```

## Company Coverage

The dataset includes major technology, semiconductor, and AI-related companies such as:

- **Technology Giants**: Apple, Microsoft, Google (Alphabet), Amazon, Meta, NVIDIA
- **Semiconductor Companies**: Intel, AMD, Qualcomm, Broadcom, TSMC
- **AI & Cloud Companies**: Salesforce, ServiceNow, Snowflake, Datadog, CrowdStrike
- **International Companies**: Samsung, Tencent, Infineon, Fujitsu

## Data Usage

This raw financial data serves as the foundation for:

- AI bubble analysis and valuation metrics
- Financial ratio calculations
- Trend analysis across technology sectors
- Comparative analysis between companies
- Market research and investment analysis

## Data Quality

All data has been sourced from StockAnalysis.com's comprehensive database, which includes:
- Standardized financial statement formats
- Quarterly reporting periods
- Consistent currency denominations
- Historical data spanning multiple quarters

## Related Files

- **Source Ticker List**: `../Tickers/merged_tickers.csv` - Complete list of 160 companies included in this dataset
- **Processed Data**: `../calculated_data/` - Calculated metrics and derived indicators from this raw data
- **Analysis Scripts**: `../scripts/` - Python scripts for data processing and analysis

---

*Data collected from [StockAnalysis.com](https://stockanalysis.com) - Accurate information on 100,000+ stocks and funds*
