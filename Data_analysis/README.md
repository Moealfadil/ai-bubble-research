# AI Bubble Analysis

A comprehensive quantitative analysis examining whether AI-related stocks exhibit bubble characteristics by comparing valuation multiples, fundamentals, and price performance across three company groups.

## 📊 Research Question

**Are AI companies trading at bubble-like valuations unsupported by fundamentals?**

This analysis investigates whether "Pure-Play AI" companies show signs of speculative excess by comparing them against "AI-Exposed / Big Tech" and a "Non-AI / Control Group" across multiple dimensions:
- Price performance (hype)
- Valuation multiples (price)
- Fundamental performance (substance)
- Financial health & risk

---

## 🗂️ Directory Structure

```
Data_analysis/
├── README.md                          # This file
├── data/
│   └── processed/
│       └── panel.parquet              # Consolidated panel dataset (5,543 quarterly observations, 118 companies)
├── mappings/
│   └── group_map.csv                  # Company → Group assignments (153 companies)
├── notebooks/
│   └── ai_bubble_analysis.ipynb       # Main orchestrator notebook
├── reports/
│   ├── figures/                       # All visualization outputs (19 PNG files)
│   │   ├── indexed_returns_*.png      # Price performance charts (3 files)
│   │   ├── box_*.png                  # Valuation & fundamental distributions (9 files)
│   │   ├── scatter_*.png              # Valuation-fundamental relationships (3 files)
│   │   └── risk_*.png                 # Financial health metrics (3 files)
│   └── tables/                        # All tabular outputs (10 CSV files)
│       ├── indexed_*.csv              # Time series of indexed returns (6 files)
│       ├── valuations_long_latest.csv # Latest quarter valuation metrics
│       ├── fundamentals_long_latest.csv # Latest quarter fundamentals
│       └── age_stratified_medians_latest.csv # Sensitivity analysis by company age
├── scripts/
│   └── build_group_map.py             # Utility to generate group_map.csv
└── src/
    ├── data_prep.py                   # Data loading, cleaning, and panel construction
    ├── analysis/
    │   ├── returns.py                 # Indexed price performance analysis
    │   ├── valuations.py              # Valuation multiples analysis
    │   ├── fundamentals.py            # Fundamental performance analysis
    │   ├── links.py                   # Valuation-fundamental scatter plots
    │   └── risk.py                    # Financial health & risk analysis
    └── plotting/
        └── theme.py                   # Shared visualization theme

```

---

## 📈 Methodology

### Company Groups (153 Total)

1. **Pure-Play AI** (7 companies): Companies whose primary business is AI products/services
   - Examples: C3.AI, SoundHound, Palantir, etc.

2. **AI-Exposed / Big Tech** (47 companies): Large tech companies with significant AI investments
   - Examples: Microsoft, Google, NVIDIA, Meta, Amazon, etc.

3. **Non-AI / Control Group** (64 companies): Technology companies with minimal AI focus
   - Examples: Traditional software, hardware, telecom companies

### Data Sources

- **Input**: 153 Excel files from `/Data_preparation/datasets/final_data/`
- **Frequency**: Quarterly financial data
- **Currency**: All values in USD (no conversion needed)
- **Time Range**: 2015-01-01 to latest available quarter

### Analysis Framework

#### 1. **Price Performance (The "Hype" Check)**
- Indexed returns rebased to 100 at three start dates: 2015-01-01, 2021-01-01, 2023-01-01
- Two weighting schemes:
  - **Equal-weighted**: Simple average across companies in each group
  - **Cap-weighted**: Weighted by market capitalization (rebalanced quarterly)
- **Interpretation**: Excessive returns relative to fundamentals suggest speculative pricing

#### 2. **Valuation Multiples (The "Price" Check)**
- Metrics analyzed (latest quarter):
  - **PS Ratio** (Price-to-Sales)
  - **PE Ratio** (Price-to-Earnings, profitable companies only)
  - **P/FCF Ratio** (Price-to-Free Cash Flow)
  - **PEG** (Price/Earnings-to-Growth)
- **Outlier handling**: Winsorized at 1st/99th percentile
- **Interpretation**: Higher multiples without fundamental support indicate overvaluation

#### 3. **Fundamental Performance (The "Substance" Check)**
- Metrics analyzed (latest quarter):
  - **Revenue Growth** (YoY %)
  - **EPS Growth** (YoY %)
  - **Operating Margin** (%)
  - **Free Cash Flow Margin** (%)
  - **R&D % of Revenue**
- **Interpretation**: Strong fundamentals justify higher valuations; weak fundamentals with high prices suggest bubble

#### 4. **Linking Valuation to Fundamentals**
- Scatter plots examining relationships:
  - PS Ratio vs Revenue Growth
  - PEG vs EPS Growth
  - R&D/Market Cap vs Revenue Growth
- **Interpretation**: Weak correlations or high valuations with low growth are red flags

#### 5. **Financial Health & Risk**
- Metrics:
  - **Debt/Equity** distribution
  - **% of companies with negative Free Cash Flow**
  - **% of companies with negative Net Income**
- **Interpretation**: High leverage and cash-burning are bubble warning signs

#### 6. **Cohort Controls (Sensitivity Analysis)**
- Age stratification: 0-3 years, 3-6 years, >6 years since first data point
- **Purpose**: Control for IPO/maturity effects (younger companies naturally have higher multiples)

---

## 🔍 Key Findings

### 1. Price Performance (Since 2023-01-01)

**Latest Indexed Returns (Rebased to 100 at 2023-01-01):**

| Group | Equal-Weighted | Cap-Weighted |
|-------|----------------|--------------|
| AI-Exposed / Big Tech | 100.02 | 100.02 |
| Pure-Play AI | 99.11 | 99.11 |
| Non-AI / Control Group | 95.71 | 98.31 |

**Interpretation:**
- ✅ **No dramatic price run-up since 2023**: All groups remain near their starting point (100)
- ✅ Pure-Play AI has NOT significantly outperformed other groups
- 📊 Since 2021, all groups have declined slightly, with Pure-Play AI down ~7.6%
- 📊 Since 2015, minimal overall gains across all groups

**Conclusion**: Price performance does NOT show bubble-like exponential growth in AI stocks relative to peers.

---

### 2. Valuation Multiples (Latest Quarter)

**Median Valuation Metrics by Group:**

| Metric | Pure-Play AI | AI-Exposed / Big Tech | Non-AI / Control |
|--------|--------------|----------------------|------------------|
| **PS Ratio** | 8.17 | 5.01 | 3.94 |
| **PE Ratio** | 32.43 (n=2) | 29.64 (n=26) | 33.24 (n=35) |
| **P/FCF Ratio** | 30.02 | 24.57 | 21.82 |
| **PEG** | 10.84 (n=2) | -0.15 (n=20) | 0.33 (n=28) |

**Interpretation:**
- ⚠️ **Pure-Play AI trades at 2.1x higher PS Ratio** than Non-AI (8.17 vs 3.94)
- ⚠️ **Pure-Play AI has significantly higher PEG** (10.84 vs 0.33), suggesting growth expectations may be overpriced
- ⚠️ **Higher P/FCF Ratio** for Pure-Play AI (30.02 vs 21.82)
- ⚠️ **Small sample size** for Pure-Play AI PE and PEG (only 2 profitable companies)

**Conclusion**: Pure-Play AI companies ARE trading at premium valuations, particularly on sales-based metrics.

---

### 3. Fundamental Performance (Latest Quarter)

**Median Fundamental Metrics by Group:**

| Metric | Pure-Play AI | AI-Exposed / Big Tech | Non-AI / Control |
|--------|--------------|----------------------|------------------|
| **Revenue Growth** | 9.5% | 9.5% | 9.5% |
| **EPS Growth** | 99.1% (n=2) | 0.1% (n=20) | 14.4% (n=28) |
| **Operating Margin** | -24.2% | 4.5% | 4.5% |
| **FCF Margin** | -18.2% | 11.0% | 10.9% |
| **R&D % of Revenue** | 34.0% | 16.1% | 16.1% |

**Interpretation:**
- ⚠️ **Pure-Play AI is UNPROFITABLE**: Median operating margin of -24.2% vs +4.5% for others
- ⚠️ **Pure-Play AI is CASH-BURNING**: Median FCF margin of -18.2% vs +11.0% for others
- ✅ **Revenue growth is SIMILAR** across all groups (~9.5%)
- ✅ **Higher R&D spend** (34% vs 16%) suggests investment in future growth, but not yet translating to profits
- ⚠️ **Small sample size** for Pure-Play AI EPS growth (only 2 profitable companies)

**Conclusion**: Pure-Play AI companies show WEAK fundamentals (negative profitability, cash-burning) despite premium valuations.

---

### 4. Valuation-Fundamental Relationships

**Key Scatter Plot Insights:**

1. **PS Ratio vs Revenue Growth**:
   - Pure-Play AI companies cluster at higher PS Ratios (6-12x) but with SIMILAR or LOWER revenue growth than Non-AI
   - **Red flag**: High prices not justified by superior growth

2. **PEG vs EPS Growth**:
   - Limited data for Pure-Play AI (only 2 profitable companies)
   - Wide dispersion suggests inconsistent growth-to-valuation relationships

3. **R&D/Market Cap vs Revenue Growth**:
   - Pure-Play AI invests heavily in R&D relative to market cap
   - However, this has NOT translated to superior revenue growth yet

**Conclusion**: Weak link between high valuations and actual growth performance for Pure-Play AI.

---

### 5. Financial Health & Risk

**Risk Metrics (Latest Quarter):**

| Metric | Pure-Play AI | AI-Exposed / Big Tech | Non-AI / Control |
|--------|--------------|----------------------|------------------|
| **Median Debt/Equity** | ~Moderate | ~Moderate | ~Moderate |
| **% Negative FCF** | ~57% (4/7) | ~30% | ~30% |
| **% Negative Net Income** | ~71% (5/7) | ~20% | ~25% |

**Interpretation:**
- ⚠️ **Majority of Pure-Play AI companies are unprofitable** (71% have negative net income)
- ⚠️ **Majority are cash-burning** (57% have negative free cash flow)
- ⚠️ This is a classic bubble characteristic: speculative investments in unprofitable companies

**Conclusion**: Pure-Play AI group shows elevated financial risk with high dependence on external capital.

---

### 6. Age-Stratified Sensitivity Analysis

**Median PS Ratio by Age Cohort:**

| Group | 0-3 years | 3-6 years | >6 years |
|-------|-----------|-----------|----------|
| Pure-Play AI | 6.72 | 13.67 | 9.32 |
| AI-Exposed / Big Tech | 7.62 | 4.86 | 4.26 |
| Non-AI / Control | 3.53 | 4.46 | 3.42 |

**Median Operating Margin by Age Cohort:**

| Group | 0-3 years | 3-6 years | >6 years |
|-------|-----------|-----------|----------|
| Pure-Play AI | 0.9% | -94.2% | -72.5% |
| AI-Exposed / Big Tech | 5.1% | -1.3% | 6.3% |
| Non-AI / Control | -0.9% | 8.0% | 3.3% |

**Interpretation:**
- ⚠️ Even controlling for age, Pure-Play AI maintains high valuations (PS Ratio)
- ⚠️ Older Pure-Play AI companies (>6 years) remain deeply unprofitable (-72.5% operating margin)
- ⚠️ This suggests structural profitability challenges, not just "startup phase" losses

**Conclusion**: Age does NOT explain away the valuation-fundamental disconnect for Pure-Play AI.

---

## 🎯 Overall Conclusion: Is There an AI Bubble?

### Evidence FOR a Bubble:

1. ⚠️ **Premium Valuations**: Pure-Play AI trades at 2.1x higher PS Ratios than Non-AI
2. ⚠️ **Weak Fundamentals**: Median operating margin of -24.2%, FCF margin of -18.2%
3. ⚠️ **No Superior Growth**: Revenue growth (~9.5%) matches Non-AI companies
4. ⚠️ **High Unprofitability Rate**: 71% have negative net income, 57% have negative FCF
5. ⚠️ **Weak Valuation-Growth Link**: High PS Ratios not justified by revenue growth
6. ⚠️ **Persistent Losses**: Even mature companies (>6 years) remain unprofitable

### Evidence AGAINST a Bubble:

1. ✅ **No Price Explosion**: Indexed returns since 2023 are flat (~99-100), not exponential
2. ✅ **High R&D Investment**: 34% of revenue vs 16% for Non-AI (future growth potential)
3. ✅ **Small Sample Size**: Only 7 Pure-Play AI companies; results may not be representative
4. ✅ **PE Ratios Similar**: Median PE of 32.43 vs 33.24 for Non-AI (for profitable companies)

### Final Assessment:

**⚠️ MODERATE BUBBLE RISK**

Pure-Play AI companies exhibit **classic bubble characteristics**:
- Premium valuations (high PS Ratios)
- Weak current fundamentals (unprofitable, cash-burning)
- Valuation-growth disconnect (high prices without superior growth)
- High financial risk (majority unprofitable)

**However**, the bubble is NOT in an explosive phase:
- Price performance has been flat since 2023 (no parabolic run-up)
- High R&D spending suggests potential for future growth
- Small sample size limits generalizability

**Risk**: If AI revenue expectations fail to materialize, or if capital markets tighten, Pure-Play AI valuations could face significant compression. The sector is priced for **perfection** (high future growth) but currently delivering **losses**.

---

## 🚀 How to Use This Analysis

### Running the Analysis

1. **Prerequisites**:
   ```bash
   pip install pandas numpy matplotlib seaborn pyarrow openpyxl
   ```

2. **Execute the notebook**:
   ```bash
   cd /Users/k./Documents/projects/AI_Bubble/ai-bubble-research/Data_analysis
   jupyter notebook notebooks/ai_bubble_analysis.ipynb
   ```

3. **Run all cells** to regenerate:
   - `data/processed/panel.parquet` (consolidated dataset)
   - `reports/figures/*.png` (19 visualizations)
   - `reports/tables/*.csv` (10 data tables)

### Modifying the Analysis

- **Add companies**: Edit `mappings/group_map.csv` and add Excel files to `Data_preparation/datasets/final_data/`
- **Change time periods**: Modify start dates in Cell 6 of the notebook
- **Add metrics**: Extend functions in `src/analysis/` modules
- **Customize plots**: Edit `src/plotting/theme.py` for styling

### Module Structure

- **`src/data_prep.py`**: Loads Excel files, harmonizes schema, attaches group labels, saves to Parquet
- **`src/analysis/returns.py`**: Computes indexed returns (equal & cap-weighted)
- **`src/analysis/valuations.py`**: Prepares valuation metrics, creates box plots
- **`src/analysis/fundamentals.py`**: Prepares fundamental metrics, creates box plots
- **`src/analysis/links.py`**: Creates scatter plots linking valuations to fundamentals
- **`src/analysis/risk.py`**: Analyzes financial health (debt, profitability, cash flow)
- **`src/plotting/theme.py`**: Shared visualization theme (colors, fonts, style)

---

## 📚 References

### Data Sources
- Financial data: `/Data_preparation/datasets/final_data/` (153 Excel files)
- Company groupings: `mappings/group_map.csv`

### Key Metrics Definitions

- **PS Ratio**: Price-to-Sales = Market Cap / Revenue
- **PE Ratio**: Price-to-Earnings = Price per Share / EPS (Diluted)
- **P/FCF Ratio**: Price-to-Free Cash Flow = Market Cap / Free Cash Flow
- **PEG**: (PE Ratio) / (EPS Growth Rate)
- **Operating Margin**: Operating Income / Revenue
- **FCF Margin**: Free Cash Flow / Revenue
- **R&D % of Revenue**: R&D Expense / Revenue

### Analysis Techniques

- **Winsorization**: Outliers capped at 1st/99th percentile to reduce noise
- **Indexed Returns**: Prices rebased to 100 at start date for comparability
- **Cap-Weighted Returns**: Weighted by market capitalization, rebalanced quarterly
- **Age Stratification**: Companies grouped by years since first data point (0-3y, 3-6y, >6y)

---

## 📝 Notes

- **Currency**: All values are in USD (no conversion needed)
- **Frequency**: Quarterly data
- **Missing Data**: Some companies lack PE Ratio (unprofitable) or PEG (no EPS growth data)
- **Sample Size**: Pure-Play AI group is small (n=7), limiting statistical power
- **Time Lag**: Analysis uses latest available quarterly data; real-time prices may differ

---

## 🤝 Contributing

To extend this analysis:

1. Add new companies to `mappings/group_map.csv`
2. Place corresponding Excel files in `Data_preparation/datasets/final_data/`
3. Run the notebook to regenerate all outputs
4. Add new analysis modules to `src/analysis/` following existing patterns

---

## 📧 Contact

For questions or suggestions about this analysis, please refer to the main project documentation.

---

**Last Updated**: November 2025  
**Analysis Version**: 1.0  
**Companies Analyzed**: 153 (7 Pure-Play AI, 47 AI-Exposed, 64 Non-AI, 35 unclassified)

