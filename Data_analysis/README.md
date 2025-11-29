# AI Bubble Analysis

A comprehensive quantitative analysis examining whether AI-related stocks exhibit bubble characteristics by comparing valuation multiples, fundamentals, and price performance across two company groups.

## Research Question

**Are AI companies trading at bubble-like valuations unsupported by fundamentals?**

This analysis investigates whether AI-related companies show signs of speculative excess by comparing them against Non-AI technology companies across multiple dimensions:

- Price performance (hype)
- Valuation multiples (price)
- Fundamental performance (substance)
- Financial health & risk

## Directory Structure

```text
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

## Methodology

### Company Groups (153 Total)

1. **AI** (54 companies): Companies with significant AI focus, including both:
   - Pure-play AI companies (e.g., C3.AI, SoundHound, Palantir)
   - AI-exposed Big Tech companies (e.g., Microsoft, Google, NVIDIA, Meta, Amazon)

2. **Non-AI** (64 companies): Technology companies with minimal AI focus
   - Examples: Traditional software, hardware, telecom companies

### Data Sources

- **Input**: 153 Excel files from `/Data_preparation/datasets/final_data/`
- **Frequency**: Quarterly financial data
- **Currency**: All values in USD (no conversion needed)
- **Time Range**: 2015-01-01 to latest available quarter

### Analysis Framework

#### 1. Price Performance (The "Hype" Check)

- Indexed returns rebased to 100 at three start dates: 2015-01-01, 2021-01-01, 2023-01-01
- Two weighting schemes:
  - **Equal-weighted**: Simple average across companies in each group
  - **Cap-weighted**: Weighted by market capitalization (rebalanced quarterly)
- **Interpretation**: Excessive returns relative to fundamentals suggest speculative pricing

#### 2. Valuation Multiples (The "Price" Check)

- Metrics analyzed (latest quarter):
  - **PS Ratio** (Price-to-Sales)
  - **PE Ratio** (Price-to-Earnings, profitable companies only)
  - **P/FCF Ratio** (Price-to-Free Cash Flow)
  - **PEG** (Price/Earnings-to-Growth)
- **Outlier handling**: Winsorized at 1st/99th percentile
- **Interpretation**: Higher multiples without fundamental support indicate overvaluation

#### 3. Fundamental Performance (The "Substance" Check)

- Metrics analyzed (latest quarter):
  - **Revenue Growth** (YoY %)
  - **EPS Growth** (YoY %)
  - **Operating Margin** (%)
  - **Free Cash Flow Margin** (%)
  - **R&D % of Revenue**
- **Interpretation**: Strong fundamentals justify higher valuations; weak fundamentals with high prices suggest bubble

#### 4. Linking Valuation to Fundamentals

- Scatter plots examining relationships:
  - PS Ratio vs Revenue Growth
  - PEG vs EPS Growth
  - R&D/Market Cap vs Revenue Growth
- **Interpretation**: Weak correlations or high valuations with low growth are red flags

#### 5. Financial Health & Risk

- Metrics:
  - **Debt/Equity** distribution
  - **% of companies with negative Free Cash Flow**
  - **% of companies with negative Net Income**
- **Interpretation**: High leverage and cash-burning are bubble warning signs

#### 6. Cohort Controls (Sensitivity Analysis)

- Age stratification: 0-3 years, 3-6 years, >6 years since first data point
- **Purpose**: Control for IPO/maturity effects (younger companies naturally have higher multiples)

## Understanding the Analysis Outputs

### Output Files and Their Significance

After running the analysis notebook, you'll generate **19 visualization files** and **10 data tables**. Here's how each output relates to the bubble analysis:

#### Price Performance Outputs (3 figures + 6 tables)

**Figures:**

- `indexed_returns_2015-01-01.png`, `indexed_returns_2021-01-01.png`, `indexed_returns_2023-01-01.png`
  - **Purpose**: Show price performance trajectories for AI vs Non-AI groups
  - **Bubble Signal**: Exponential upward curves would indicate bubble; flat or declining suggests no bubble
  - **What to Look For**: Whether AI group shows dramatic outperformance or modest gains

**Tables:**

- `indexed_eq_*.csv` and `indexed_cap_*.csv` (6 files total)
  - **Purpose**: Time series data of indexed returns (equal-weighted and cap-weighted)
  - **Use**: Allows detailed analysis of performance over time, identification of peak periods, calculation of volatility

#### Valuation Analysis Outputs (4 figures + 1 table)

**Figures:**

- `box_ps_ratio.png`, `box_pe_ratio.png`, `box_p_fcf_ratio.png`, `box_peg.png`
  - **Purpose**: Distribution of valuation multiples for each group
  - **Bubble Signal**: Extremely high medians or wide distributions suggest overvaluation
  - **What to Look For**: Whether AI group shows consistently higher multiples across all metrics

**Table:**

- `valuations_long_latest.csv`
  - **Purpose**: Long-format data of all valuation metrics for statistical analysis
  - **Use**: Enables calculation of percentiles, identification of outliers, statistical testing

#### Fundamental Analysis Outputs (5 figures + 1 table)

**Figures:**

- `box_revenue_growth.png`, `box_eps_growth.png`, `box_operating_margin.png`, `box_free_cash_flow_margin_y.png`, `box_r&d_pct_of_revenue.png`
  - **Purpose**: Distribution of fundamental performance metrics
  - **Bubble Signal**: Low/negative fundamentals with high valuations indicate bubble
  - **What to Look For**: Whether AI group shows superior fundamentals to justify premium valuations

**Table:**

- `fundamentals_long_latest.csv`
  - **Purpose**: Long-format data of all fundamental metrics
  - **Use**: Enables correlation analysis, identification of fundamental drivers of valuation

#### Valuation-Fundamental Relationships (3 figures)

**Figures:**

- `scatter_ps_vs_revgrowth.png`, `scatter_peg_vs_epsgrowth.png`, `scatter_rndmc_vs_revgrowth.png`
  - **Purpose**: Test whether high valuations are justified by strong fundamentals
  - **Bubble Signal**: High valuations with low fundamentals (points in upper-left quadrant) indicate bubble
  - **What to Look For**: Correlation strength and whether AI companies cluster in "high price, low growth" region

#### Risk Analysis Outputs (3 figures)

**Figures:**

- `risk_debt_equity.png`, `risk_share_negative_free_cash_flow.png`, `risk_share_negative_net_income_y.png`
  - **Purpose**: Assess financial health and sustainability
  - **Bubble Signal**: High leverage, high unprofitability rates suggest financial stress
  - **What to Look For**: Whether AI group shows elevated risk metrics

#### Sensitivity Analysis (1 table)

**Table:**

- `age_stratified_medians_latest.csv`
  - **Purpose**: Control for company age effects (younger companies naturally have higher multiples)
  - **Bubble Signal**: Premium valuations persist even after controlling for age
  - **Use**: Identifies whether valuation differences are due to lifecycle stage or true overvaluation

### How Outputs Answer the Bubble Question

Each output addresses a specific aspect of bubble detection:

1. **Price Performance** - Tests for "hype" (excessive price appreciation)
2. **Valuation Multiples** - Tests for "price" (overvaluation relative to fundamentals)
3. **Fundamentals** - Tests for "substance" (whether performance justifies valuations)
4. **Valuation-Fundamental Links** - Tests for "justification" (correlation between price and performance)
5. **Risk Profiles** - Tests for "sustainability" (financial health and viability)
6. **Age Stratification** - Tests for "maturity effects" (controlling for lifecycle stage)

**Bubble Characteristics** would show:

- High price performance (exponential gains)
- High valuation multiples (PS, PE, P/FCF)
- Weak fundamentals (low growth, negative margins)
- Weak valuation-fundamental correlation
- High risk (unprofitability, cash-burning)
- Premium persists after age controls

**No Bubble** would show:

- Modest price performance
- Reasonable valuation multiples
- Strong fundamentals
- Strong valuation-fundamental correlation
- Low risk
- Premium explained by age/maturity

## Key Findings

### 1. Price Performance (Indexed Returns)

**Latest Indexed Returns by Start Date:**

| Start Date | Group | Equal-Weighted | Cap-Weighted |
|------------|-------|----------------|--------------|
| **2023-01-01** | AI | 100.02 | 100.02 |
| | Non-AI | 95.71 | 98.31 |
| **2021-01-01** | AI | 100.16 | 100.16 |
| | Non-AI | 93.88 | 97.59 |
| **2015-01-01** | AI | 100.89 | 100.89 |
| | Non-AI | 93.20 | 96.85 |

**Interpretation:**

- **No dramatic price run-up since 2023**: Both groups remain near their starting point (100)
- **AI group has modestly outperformed Non-AI**: ~4-7% higher returns depending on weighting and time period
- **Since 2021**: AI group essentially flat (~100), Non-AI down ~6-7%
- **Since 2015**: Both groups show minimal gains, with AI slightly ahead
- **Cap-weighted vs Equal-weighted**: Cap-weighted shows smaller gap, suggesting larger AI companies haven't outperformed as dramatically

**Conclusion**: Price performance shows **modest AI outperformance** but does NOT show bubble-like exponential growth. The AI group has maintained its value better than Non-AI, but the difference is relatively small (~4-7%), not the 50-100%+ gains typical of bubbles.

### 2. Valuation Multiples (Latest Quarter)

**Median Valuation Metrics by Group:**

| Metric | AI | Non-AI | Difference |
|--------|-------|---------|------------|
| **PS Ratio** | 5.29 | 3.94 | +34% (AI premium) |
| **PE Ratio** | 29.64 | 33.24 | -11% (AI discount) |
| **P/FCF Ratio** | 27.29 | 21.82 | +25% (AI premium) |
| **PEG** | 0.44 | 0.33 | +33% (AI premium) |

**Sample Sizes:**

- PS Ratio: AI (n=54), Non-AI (n=64)
- PE Ratio: AI (n=28), Non-AI (n=35) - *only profitable companies*
- P/FCF Ratio: AI (n=54), Non-AI (n=64)
- PEG: AI (n=22), Non-AI (n=28) - *only companies with EPS growth data*

**Interpretation:**

- **AI trades at 34% premium on PS Ratio** (5.29 vs 3.94) - sales-based valuation is higher
- **AI trades at 11% discount on PE Ratio** (29.64 vs 33.24) - earnings-based valuation is actually lower
- **AI trades at 25% premium on P/FCF Ratio** (27.29 vs 21.82) - cash flow valuation is higher
- **AI has 33% higher PEG** (0.44 vs 0.33) - but both are relatively low, suggesting reasonable growth-adjusted valuations
- **Mixed signals**: Higher sales/cash flow multiples but lower earnings multiples suggests AI companies may be investing more (lower current earnings) but generating similar or better cash flows

**Conclusion**: AI companies show **moderate premium valuations** on sales and cash flow metrics, but **lower earnings multiples**. This pattern suggests AI companies are investing heavily (depressing current earnings) while maintaining strong cash generation. The premium is **moderate (25-34%)**, not extreme, and may be justified by growth prospects.

### 3. Fundamental Performance (Latest Quarter)

**Median Fundamental Metrics by Group:**

| Metric | AI | Non-AI | Difference |
|--------|-------|---------|------------|
| **Revenue Growth** | 9.44% | 11.78% | -20% (AI lower) |
| **EPS Growth** | 7.20% | 14.41% | -50% (AI lower) |
| **Operating Margin** | 4.53% | 2.72% | +67% (AI higher) |
| **FCF Margin** | 9.88% | 6.04% | +64% (AI higher) |
| **R&D % of Revenue** | 16.30% | 14.33% | +14% (AI higher) |

**Sample Sizes:**

- Revenue Growth: AI (n=53), Non-AI (n=64)
- EPS Growth: AI (n=22), Non-AI (n=28) - *only profitable companies*
- Operating Margin: AI (n=54), Non-AI (n=64)
- FCF Margin: AI (n=54), Non-AI (n=64)
- R&D % of Revenue: AI (n=54), Non-AI (n=64)

**Interpretation:**

- **AI has LOWER revenue growth** (9.44% vs 11.78%) - surprising finding, suggests growth premium may not be justified by current growth rates
- **AI has LOWER EPS growth** (7.20% vs 14.41%) - but this is for profitable companies only; many AI companies may be unprofitable
- **AI has HIGHER operating margins** (4.53% vs 2.72%) - better profitability despite lower growth
- **AI has HIGHER FCF margins** (9.88% vs 6.04%) - significantly better cash generation
- **AI invests more in R&D** (16.30% vs 14.33%) - building for future growth

**Conclusion**: AI companies show a **paradoxical fundamental profile**: lower current growth rates but **superior profitability and cash generation**. This suggests AI companies may be:

1. **More mature/established** (hence lower growth but higher margins)
2. **Investing in future growth** (higher R&D spending)
3. **Better at converting revenue to cash** (higher FCF margins)

The **lower growth but higher margins** pattern is unusual and suggests AI companies may be in a different stage of the business lifecycle than Non-AI companies.

### 4. Valuation-Fundamental Relationships

**Key Scatter Plot Insights:**

The analysis generates three scatter plots examining relationships between valuations and fundamentals:

1. **PS Ratio vs Revenue Growth** (`scatter_ps_vs_revgrowth.png`):
   - Tests whether higher price-to-sales ratios are justified by superior revenue growth
   - **Expected finding**: AI companies may cluster at higher PS ratios
   - **Bubble signal**: High PS ratios with low/negative growth would indicate overvaluation

2. **PEG vs EPS Growth** (`scatter_peg_vs_epsgrowth.png`):
   - Tests whether growth-adjusted valuations (PEG) correlate with actual EPS growth
   - **Expected finding**: Positive correlation would indicate efficient pricing
   - **Bubble signal**: High PEG ratios with low/negative growth would indicate overvaluation

3. **R&D/Market Cap vs Revenue Growth** (`scatter_rndmc_vs_revgrowth.png`):
   - Tests whether R&D investment (relative to market cap) translates to revenue growth
   - **Expected finding**: Positive correlation would justify high R&D spending
   - **Bubble signal**: High R&D spending with low growth would suggest inefficient investment

**Conclusion**: These scatter plots help identify whether the **valuation premium** for AI companies is supported by **fundamental performance**. Weak correlations or negative relationships would suggest the premium is speculative rather than justified.

### 5. Financial Health and Risk

**Risk Metrics (Latest Quarter):**

The analysis generates three risk profile visualizations:

1. **Debt/Equity Distribution** (`risk_debt_equity.png`):
   - Box plot comparing leverage ratios between AI and Non-AI groups
   - **Bubble signal**: High leverage combined with unprofitability suggests financial stress

2. **% Negative Free Cash Flow** (`risk_share_negative_free_cash_flow.png`):
   - Bar chart showing percentage of companies with negative FCF in each group
   - **Bubble signal**: High percentage of cash-burning companies suggests dependence on external capital

3. **% Negative Net Income** (`risk_share_negative_net_income_y.png`):
   - Bar chart showing percentage of unprofitable companies in each group
   - **Bubble signal**: High percentage of unprofitable companies suggests speculative pricing

**Interpretation:**

- These metrics help assess **financial sustainability** of each group
- High percentages of unprofitable or cash-burning companies would indicate **bubble risk**
- Lower percentages would suggest **healthier financial profiles**

**Conclusion**: The risk profile analysis helps determine whether AI companies are **financially sustainable** or **dependent on external capital**. High rates of unprofitability or cash-burning would suggest bubble characteristics, while healthy financial profiles would support current valuations.

### 6. Age-Stratified Sensitivity Analysis

**Median Metrics by Age Cohort (Latest Quarter):**

| Group | Age | PS Ratio | PE Ratio | P/FCF Ratio | PEG | Revenue Growth | Operating Margin |
|-------|-----|----------|----------|------------|-----|----------------|------------------|
| **AI** | 0-3y | 7.62 | 36.14 | 44.98 | -0.57 | 8.62% | 5.06% |
| | 3-6y | 5.09 | 48.24 | 26.74 | 3.20 | 1.73% | -3.09% |
| | >6y | 4.28 | 22.40 | 15.76 | -0.15 | 9.63% | 6.27% |
| **Non-AI** | 0-3y | 3.53 | 22.36 | 19.93 | 0.58 | 6.48% | -0.90% |
| | 3-6y | 4.46 | 53.49 | 24.26 | 1.91 | 16.51% | 8.01% |
| | >6y | 3.42 | 35.29 | 21.92 | -0.97 | 11.66% | 3.26% |

**Interpretation:**

- **Young companies (0-3y)**: AI trades at **2.2x higher PS ratio** (7.62 vs 3.53) but has similar growth (8.62% vs 6.48%) and better margins (5.06% vs -0.90%)
- **Mid-age companies (3-6y)**: AI has **similar PS ratios** (5.09 vs 4.46) but **much lower growth** (1.73% vs 16.51%) and **negative margins** (-3.09% vs 8.01%)
- **Mature companies (>6y)**: AI has **25% higher PS ratio** (4.28 vs 3.42) but **lower growth** (9.63% vs 11.66%) and **higher margins** (6.27% vs 3.26%)

**Key Insights:**

- **Young AI companies** show premium valuations with similar growth but better profitability
- **Mid-age AI companies** show concerning pattern: similar valuations but much lower growth and negative margins
- **Mature AI companies** show premium valuations with slightly lower growth but significantly better margins

**Conclusion**: Age stratification reveals **heterogeneous patterns** across company lifecycles. The mid-age AI cohort (3-6y) shows the most concerning pattern (low growth, negative margins), while young and mature AI companies show more reasonable valuation-fundamental relationships. This suggests the AI group contains companies at different stages, and the aggregate metrics may mask important differences.

## Overall Conclusion: Is There an AI Bubble?

### Evidence FOR a Bubble

1. **Premium Valuations**: AI trades at 34% higher PS Ratio and 25% higher P/FCF Ratio than Non-AI
2. **Lower Growth**: AI has 20% lower revenue growth and 50% lower EPS growth than Non-AI
3. **Valuation-Growth Mismatch**: Higher valuations despite lower growth rates suggests overvaluation
4. **Mid-Age Cohort Concerns**: AI companies aged 3-6 years show negative margins and low growth despite premium valuations

### Evidence AGAINST a Bubble

1. **Modest Price Performance**: Only 4-7% outperformance since 2023, not exponential bubble growth
2. **Superior Profitability**: AI has 67% higher operating margins and 64% higher FCF margins
3. **Better Cash Generation**: Higher FCF margins suggest better business quality, not speculation
4. **Reasonable PEG Ratios**: Both groups have low PEG ratios (0.33-0.44), suggesting growth-adjusted valuations are reasonable
5. **Lower PE Ratios**: AI actually trades at 11% discount on earnings multiples

### Final Assessment

#### MODERATE BUBBLE RISK - MIXED SIGNALS

The 2-group analysis reveals a **complex picture** with both bubble-like and non-bubble-like characteristics:

**Key Findings:**

- **Valuation Premium**: AI companies trade at 25-34% premium on sales/cash flow metrics
- **Growth Paradox**: AI has LOWER growth but HIGHER profitability - unusual pattern
- **Price Performance**: Modest outperformance (4-7%), not bubble-like exponential gains
- **Fundamental Quality**: AI shows superior cash generation and margins, suggesting better business quality

**Interpretation:**

The combination of **premium valuations + lower growth + higher margins** suggests:

1. AI companies may be **more mature/established** than Non-AI (hence lower growth but better margins)
2. The premium may reflect **quality premium** (better cash generation) rather than **growth premium**
3. The modest price outperformance suggests **efficient pricing** rather than speculative bubble

**Risk Assessment:**

- **Lower Risk**: Modest price gains, superior cash generation, reasonable PEG ratios
- **Higher Risk**: Valuation-growth mismatch, mid-age cohort concerns, premium on sales multiples

**Conclusion**: The AI group shows **moderate premium valuations** that are **partially justified** by superior profitability and cash generation, but **not justified** by growth rates. This suggests a **quality premium** rather than a **growth bubble**, but the valuation-growth disconnect remains a concern. The risk is **moderate** - not a full bubble, but valuations may compress if growth doesn't accelerate or margins compress.

## How to Use This Analysis

### Running the Analysis

1. **Prerequisites:**

   ```bash
   pip install pandas numpy matplotlib seaborn pyarrow openpyxl
   ```

2. **Execute the notebook:**

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

- **`src/data_prep.py`** - Loads Excel files, harmonizes schema, attaches group labels, saves to Parquet
- **`src/analysis/returns.py`** - Computes indexed returns (equal & cap-weighted)
- **`src/analysis/valuations.py`** - Prepares valuation metrics, creates box plots
- **`src/analysis/fundamentals.py`** - Prepares fundamental metrics, creates box plots
- **`src/analysis/links.py`** - Creates scatter plots linking valuations to fundamentals
- **`src/analysis/risk.py`** - Analyzes financial health (debt, profitability, cash flow)
- **`src/plotting/theme.py`** - Shared visualization theme (colors, fonts, style)

## References

### Financial Data Sources

- Financial data: `/Data_preparation/datasets/final_data/` (153 Excel files)
- Company groupings: `mappings/group_map.csv`

### Key Metrics Definitions

- **PS Ratio** - Price-to-Sales = Market Cap / Revenue
- **PE Ratio** - Price-to-Earnings = Price per Share / EPS (Diluted)
- **P/FCF Ratio** - Price-to-Free Cash Flow = Market Cap / Free Cash Flow
- **PEG** - (PE Ratio) / (EPS Growth Rate)
- **Operating Margin** - Operating Income / Revenue
- **FCF Margin** - Free Cash Flow / Revenue
- **R&D % of Revenue** - R&D Expense / Revenue

### Analysis Techniques

- **Winsorization** - Outliers capped at 1st/99th percentile to reduce noise
- **Indexed Returns** - Prices rebased to 100 at start date for comparability
- **Cap-Weighted Returns** - Weighted by market capitalization, rebalanced quarterly
- **Age Stratification** - Companies grouped by years since first data point (0-3y, 3-6y, >6y)

## Notes

- **Currency** - All values are in USD (no conversion needed)
- **Frequency** - Quarterly data
- **Missing Data** - Some companies lack PE Ratio (unprofitable) or PEG (no EPS growth data)
- **Sample Size** - AI group (n=54) and Non-AI group (n=64) provide reasonable statistical power
- **Group Composition** - AI group combines Pure-Play AI (7 companies) and AI-Exposed Big Tech (47 companies), creating a more diverse but larger sample
- **Time Lag** - Analysis uses latest available quarterly data; real-time prices may differ

## Contributing

To extend this analysis:

1. Add new companies to `mappings/group_map.csv`
2. Place corresponding Excel files in `Data_preparation/datasets/final_data/`
3. Run the notebook to regenerate all outputs
4. Add new analysis modules to `src/analysis/` following existing patterns
