from __future__ import annotations

import os
from typing import Iterable

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from ..data_prep import latest_cross_section, winsorize_series
from ..plotting.theme import set_theme, PALETTE


VALUATION_COLS: list[str] = [
    "PS Ratio",
    "PE Ratio",
    "P/FCF Ratio",
    "PEG",
]


def _prep_latest(panel: pd.DataFrame) -> pd.DataFrame:
    latest = latest_cross_section(panel)
    # Filter for PE: require positive EPS
    if "EPS (Diluted)" in latest.columns:
        mask_pe = pd.to_numeric(latest["EPS (Diluted)"], errors="coerce") > 0
        latest.loc[~mask_pe, "PE Ratio"] = np.nan
    return latest


def make_long_valuations(latest: pd.DataFrame, winsorize: bool = True) -> pd.DataFrame:
    df = latest[["group", *VALUATION_COLS]].copy()
    for c in VALUATION_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        if winsorize:
            df[c] = winsorize_series(df[c])
    long_df = df.melt(id_vars="group", value_vars=VALUATION_COLS, var_name="metric", value_name="value")
    long_df = long_df.dropna(subset=["value"])  # drop missing
    return long_df


def plot_valuation_boxplots(long_df: pd.DataFrame, outdir: str) -> None:
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
        plt.savefig(os.path.join(outdir, f"box_{metric.replace('/', '_').replace(' ', '_').lower()}.png"), dpi=150)
        plt.show()
        plt.close()


__all__ = [
    "make_long_valuations",
    "plot_valuation_boxplots",
    "_prep_latest",
]


