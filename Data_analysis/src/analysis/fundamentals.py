from __future__ import annotations

import os

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from ..data_prep import latest_cross_section, winsorize_series
from ..plotting.theme import set_theme, PALETTE


FUND_COLS: list[str] = [
    "Revenue Growth",
    "EPS Growth",
    "Operating Margin",
    "Free Cash Flow Margin_y",
    "R&D_pct_of_Revenue",
]


def make_long_fundamentals(panel: pd.DataFrame, winsorize: bool = True) -> pd.DataFrame:
    latest = latest_cross_section(panel)
    df = latest[["group", *FUND_COLS]].copy()
    for c in FUND_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        if winsorize:
            df[c] = winsorize_series(df[c])
    long_df = df.melt(id_vars="group", value_vars=FUND_COLS, var_name="metric", value_name="value")
    long_df = long_df.dropna(subset=["value"])  # drop missing
    return long_df


def plot_fundamentals_boxplots(long_df: pd.DataFrame, outdir: str) -> None:
    set_theme()
    os.makedirs(outdir, exist_ok=True)
    for metric in long_df["metric"].unique():
        sub = long_df[long_df["metric"] == metric]
        plt.figure(figsize=(8, 5))
        ax = sns.boxplot(data=sub, x="group", y="value", hue="group", palette=PALETTE, legend=False)
        sns.stripplot(data=sub, x="group", y="value", color="#444444", size=3, alpha=0.4, dodge=True)
        ax.set_xlabel("")
        ax.set_ylabel(metric)
        ax.set_title(f"{metric} by group (latest quarter)")
        plt.xticks(rotation=15, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"box_{metric.replace(' ', '_').lower()}.png"), dpi=150)
        plt.show()
        plt.close()


__all__ = [
    "make_long_fundamentals",
    "plot_fundamentals_boxplots",
]


