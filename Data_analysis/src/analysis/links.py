from __future__ import annotations

import os

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from ..data_prep import latest_cross_section
from ..plotting.theme import set_theme, PALETTE


def _clean_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    outpath: str,
    title: str,
) -> None:
    set_theme()
    plt.figure(figsize=(8, 6))
    ax = sns.scatterplot(data=df, x=x, y=y, hue="group", palette=PALETTE, alpha=0.8)
    sns.regplot(data=df, x=x, y=y, scatter=False, color="#333333", line_kws={"alpha": 0.6})
    ax.set_title(title)
    plt.tight_layout()
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    plt.savefig(outpath, dpi=150)
    plt.show()
    plt.close()


def plot_link_scatter_panels(panel: pd.DataFrame, outdir: str) -> None:
    latest = latest_cross_section(panel)
    latest = _clean_numeric(
        latest,
        [
            "PS Ratio",
            "Revenue Growth",
            "PEG",
            "EPS_Growth_pct_used",
            "R&D_to_MarketCap",
        ],
    )
    # Drop missing rows per plot
    p1 = latest.dropna(subset=["PS Ratio", "Revenue Growth", "group"]) 
    _scatter(p1, "Revenue Growth", "PS Ratio", os.path.join(outdir, "scatter_ps_vs_revgrowth.png"), "P/S vs Revenue Growth (latest)")

    p2 = latest.dropna(subset=["PEG", "EPS_Growth_pct_used", "group"]) 
    _scatter(p2, "EPS_Growth_pct_used", "PEG", os.path.join(outdir, "scatter_peg_vs_epsgrowth.png"), "PEG vs EPS Growth Used (latest)")

    p3 = latest.dropna(subset=["R&D_to_MarketCap", "Revenue Growth", "group"]) 
    _scatter(p3, "Revenue Growth", "R&D_to_MarketCap", os.path.join(outdir, "scatter_rndmc_vs_revgrowth.png"), "R&D to MarketCap vs Revenue Growth (latest)")


__all__ = [
    "plot_link_scatter_panels",
]


