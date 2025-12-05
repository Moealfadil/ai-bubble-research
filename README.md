# AI Bubble Research

This repository contains the code, data artifacts, notebooks, and reports for a quantitative study comparing valuation, performance, fundamentals and risk between AI-focused companies and other technology firms.

<!-- markdownlint-disable MD033 -->
<p align="center">
  <img src="https://raw.githubusercontent.com/Moealfadil/ai-bubble-research/results/assests/AI_bubble.png" alt="AI Bubble Overview" style="max-width: 100%; width: 100%; height: auto; max-height: 100px; object-fit: contain;"/>
</p>
<!-- markdownlint-enable MD033 -->

## Project overview

The goal of this project is to evaluate whether a distinct "AI" equity bubble exists by comparing AI-labelled companies to a peer set of Non-AI technology companies across multiple dimensions: price performance, valuation multiples, fundamental performance, valuation-to-fundamentals links, risk indicators, and lifecycle (age) stratification. The analysis covers quarterly financial data from 2015 through 2025 and includes 153 companies.

## Problem statement

Investors and stakeholders need clarity on whether high AI-sector valuations are supported by fundamentals or driven by narrative and speculation. This project quantifies valuation gaps, tests whether fundamentals justify premium multiples, and highlights financial sustainability risks (profitability and free cash flow) that could make parts of the sector fragile to changing market conditions.

## Repository Structure

```plaintext
/ai-bubble-research
│
├── README.md                        # Main project overview
├── research_findings.md             # Investor-facing summary of results
│
├── Data_analysis/                   # Analysis code, notebook, reports
│   ├── notebooks/
│   │   └── ai_bubble_analysis.ipynb
│   ├── reports/
│   │   ├── figures/
│   │   └── tables/
│   └── src/
│
├── Data_collection/                 # Collected indicators and helper scripts
│   ├── indicators/
│   │   ├── alpha/
│   │   ├── calculated_data/
│   │   └── complete_data_improved/
│   ├── scripts/
│   └── stock_analysis/
│
├── Data_preparation/                # Cleaning and preprocessing pipelines
│   ├── datasets/
│   │   ├── cleaned_data/
│   │   ├── final_data/
│   │   ├── normalized_data/
│   │   └── preprocessed_data/
│   └── scripts/
│
└── collaboration/                   # Team communication and retrospectives
    ├── communication.md
    └── retrospective.md
```

## Folder Descriptions

- Data_analysis — [Data_analysis folder](https://github.com/Moealfadil/ai-bubble-research/tree/main/Data_analysis)
  - Main analysis assets. Notebook: [ai_bubble_analysis.ipynb](https://github.com/Moealfadil/ai-bubble-research/blob/main/Data_analysis/notebooks/ai_bubble_analysis.ipynb); Figures: [reports/figures](https://github.com/Moealfadil/ai-bubble-research/tree/main/Data_analysis/reports/figures); Tables: [reports/tables](https://github.com/Moealfadil/ai-bubble-research/tree/main/Data_analysis/reports/tables); Source code: [src](https://github.com/Moealfadil/ai-bubble-research/tree/main/Data_analysis/src).

- Data_collection — [Data_collection folder](https://github.com/Moealfadil/ai-bubble-research/tree/main/Data_collection)
  - Indicator datasets (e.g., alpha), calculation outputs, and helper scripts for data acquisition and stock analysis.

- Data_preparation — [Data_preparation folder](https://github.com/Moealfadil/ai-bubble-research/tree/main/Data_preparation)
  - Scripts and datasets for cleaning, transforming, and standardizing inputs consumed by Data_analysis.


- collaboration — [collaboration folder](https://github.com/Moealfadil/ai-bubble-research/tree/main/collaboration)
  - Team communication and process docs (see `communication.md`, `retrospective.md`).

- research_findings.md — [research_findings.md file](https://github.com/Moealfadil/ai-bubble-research/blob/main/research_findings.md)
  - Condensed, investor-facing write-up with embedded figures and implications.

## Contributors

This project was developed collaboratively by the following contributors:

<!-- markdownlint-disable MD033 -->
<div align="center">
<table>
  <tr>
    <td align="center" valign="top">
      <a href="https://github.com/Moealfadil">
        <img src="https://avatars.githubusercontent.com/u/142026026?v=4&s=100" alt="Mohammed Elfadil" width="90" style="border-radius:50%; object-fit:cover;" />
        <br />
        <sub><b>Mohammed Elfadil</b></sub>
      </a>
    </td>
    <td width="32">&nbsp;</td>
    <td align="center" valign="top">
      <a href="https://github.com/k1llay">
        <img src="https://avatars.githubusercontent.com/u/133220318?v=4&s=100" alt="k1llay" width="90" style="border-radius:50%; object-fit:cover;" />
        <br />
        <sub><b>k1llay</b></sub>
      </a>
    </td>
  </tr>
  
</table>
</div>
<!-- markdownlint-enable MD033 -->

Contributions, issues, and pull requests are welcome. Please open an issue if you find discrepancies in the data or want to propose improvements.

## Getting started

Follow these steps to run the analysis locally and reproduce the figures/tables.

### Prerequisites

- Python 3.10 or newer
- Git
- Jupyter (via VS Code or classic Jupyter)

### 1) Clone the repository

```powershell
git clone https://github.com/Moealfadil/ai-bubble-research.git
cd ai-bubble-research
```

### 2) Create and activate a virtual environment (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 3) Install dependencies

If you have a minimal environment already, install the core packages used by the analysis:

```powershell
pip install pandas numpy matplotlib seaborn plotly pyarrow jupyter
```

Alternatively, if you want to start from the indicators environment as a base:

```powershell
pip install -r Data_collection/indicators/requirements.txt
```

### 4) Open and run the main notebook

- Open `Data_analysis/notebooks/ai_bubble_analysis.ipynb`
- In the first setup cells, update the `ai_bubble_research` path to your local repo root, for example:

```python
ai_bubble_research = r"D:/MIT/Develop_Workflow/ELO2/ai-bubble-research"
```

- If needed, also update the `DATA_DIR`, `GROUP_MAP_CSV`, `PANEL_PARQUET`, `FIG_DIR`, and `TAB_DIR` variables in the paths cell to match your local folders.
- Run all cells to generate outputs.

### 5) View outputs

- Figures: `Data_analysis/reports/figures/`
- Tables (CSV): `Data_analysis/reports/tables/`
