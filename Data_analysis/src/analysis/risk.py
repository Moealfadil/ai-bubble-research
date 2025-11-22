from __future__ import annotations

import os

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from ..data_prep import latest_cross_section, winsorize_series
from ..plotting.theme import set_theme, PALETTE


def plot_debt_equity_distribution(panel: pd.DataFrame, outpath: str) -> None:
    set_theme()
    latest = latest_cross_section(panel)
    latest["Debt/Equity"] = pd.to_numeric(latest["Debt/Equity"], errors="coerce")
    latest["Debt/Equity"] = winsorize_series(latest["Debt/Equity"])  # tame outliers
    latest = latest.dropna(subset=["Debt/Equity", "group"]) 

    plt.figure(figsize=(8, 5))
    ax = sns.boxplot(data=latest, x="group", y="Debt/Equity", hue="group", palette=PALETTE, legend=False)
    sns.stripplot(data=latest, x="group", y="Debt/Equity", color="#444444", size=3, alpha=0.4, dodge=True)
    ax.set_xlabel("")
    ax.set_ylabel("Debt/Equity")
    ax.set_title("Debt/Equity by group (latest quarter)")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    plt.savefig(outpath, dpi=150)
    plt.show()
    plt.close()


def plot_unprofitable_shares(panel: pd.DataFrame, outpath_prefix: str) -> None:
    set_theme()
    latest = latest_cross_section(panel)
    latest["Free Cash Flow"] = pd.to_numeric(latest["Free Cash Flow"], errors="coerce")
    latest["Net Income_y"] = pd.to_numeric(latest["Net Income_y"], errors="coerce")

    def _share_negative(col: str) -> pd.DataFrame:
        df = latest.dropna(subset=[col, "group"]).copy()
        if df.empty:
            return pd.DataFrame(columns=["group", "share_negative"])  # type: ignore
        agg = (
            df.assign(is_negative=df[col] < 0)
              .groupby("group")
              .agg(share_negative=("is_negative", "mean"))
              .reset_index()
        )
        agg["share_negative"] = 100.0 * agg["share_negative"]
        return agg

    for col, label in [("Free Cash Flow", "Negative Free Cash Flow"), ("Net Income_y", "Negative Net Income")]:
        agg = _share_negative(col)
        plt.figure(figsize=(7, 4))
        ax = sns.barplot(data=agg, x="group", y="share_negative", hue="group", palette=PALETTE, legend=False)
        ax.bar_label(ax.containers[0], fmt="%.1f%%")
        ax.set_xlabel("")
        ax.set_ylabel("% of companies")
        ax.set_title(f"Share with {label} (latest quarter)")
        plt.xticks(rotation=15, ha="right")
        plt.tight_layout()
        os.makedirs(os.path.dirname(outpath_prefix), exist_ok=True)
        plt.savefig(f"{outpath_prefix}_{col.replace(' ', '_').lower()}.png", dpi=150)
        plt.show()
        plt.close()


__all__ = [
    "plot_debt_equity_distribution",
    "plot_unprofitable_shares",
]


