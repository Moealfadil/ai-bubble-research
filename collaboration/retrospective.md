# End-of-Research Retrospective

This retrospective captures what went well, what was challenging, and what we would adjust in future iterations of the AI bubble research project.

## Data Collection: Hardest Stage

Finding the right data was the most difficult part of the project.

- Limited free access: Many platforms restrict historical and granular financial data behind paid tiers; free accounts do not provide full access.
- Subscriptions and multi-platform workflow: We had to subscribe to select services and stitch datasets from multiple sources to cover gaps.
- US-centric availability: Data was readily available for U.S.-listed companies, but coverage for international markets was sparse and inconsistent.
- Additional digging: For non-U.S. companies, we relied on alternative sources, company filings, and bespoke scraping to assemble comparable metrics.
- Consistency risks: Different platforms use varying definitions and update cadences, requiring verification and harmonization before use.

## Data Preparation: Filtering for Research Usefulness

After collecting company-level financial datasets, we focused on filtering and standardization to ensure analytical relevance.

- Inclusion criteria: Selected variables directly linked to our research questions (e.g., revenue, EPS, margins, market cap, free cash flow, R&D).
- Cleaning and normalization: Resolved missing values, standardized units and date formats, and aligned tickers and identifiers across sources.
- Outlier handling: Winsorized extreme values to reduce noise while preserving signal in distributions and relationships.
- Cohort assignment: Labeled companies into AI vs. Non-AI groups using a transparent mapping, then validated edge cases.
- Panel construction: Built a consolidated panel across time to support return indexing, valuations, fundamentals, risk, and age stratification.
  
## Data Analysis Approach

To enable a fair and comparable study, we divided companies into two groups and evaluated a focused set of metrics:

- Grouping: AI vs. Non-AI technology companies based on a transparent mapping of business focus.
- Metrics studied: Price performance (indexed returns), valuation multiples (PS, PE, P/FCF, PEG), fundamentals (revenue growth, margins, R&D intensity), valuation–fundamental links (scatter relationships), and risk (debt/equity, profitability, cash burn).
- Structure: Analysis ran across six dimensions with outputs saved to figures and tables for traceability.

## What Worked Well

- Clear analytical framework: The multi-dimension approach (price, valuations, fundamentals, links, risk, age) kept the analysis focused and comparable.
- Reproducible workflow: Modular notebook + scripts structure allowed fast iteration and re-runs when data changed.
- Visual evidence: Box plots and scatter panels effectively communicated distribution differences and correlation patterns.

## Challenges and Mitigations

- Access constraints: Addressed via selective subscriptions and prioritizing high-signal variables.
- Cross-source inconsistencies: Invested time in harmonization, documentation, and sanity checks.
- International coverage: Accepted partial coverage where necessary and highlighted scope limits in findings.

## Lessons Learned

- Budget early for data: Plan subscriptions and access needs upfront to avoid delays.
- Define variables tightly: A narrow, well-defined metric list speeds cleaning and reduces ambiguity.
- Document assumptions: Keep a running log of definitions, transformations, and any imputations.

## Next Steps

- Create predictive model: Build a baseline model to forecast valuation normalization and company-level risk (e.g., probability of negative FCF persistence), using the prepared features.
- Define modeling pipeline: Feature selection, train/validation split, baseline models (logistic/linear), and transparent evaluation metrics.

## Brief Results Summary

Highlights (see `research_findings.md` for full details):

- AI has outperformed long term; performance moderated in 2023–2025.
- Valuations show a ~69% PS premium for AI vs. Non-AI peers.
- Risk is elevated: many AI firms are unprofitable and cash-burning.
