from __future__ import annotations

import os
from typing import Literal

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from ..plotting.theme import set_theme, PALETTE


Weighting = Literal["equal", "cap"]


def _build_ticker_index(df: pd.DataFrame, start_date: str) -> pd.DataFrame:
    df = df[df["Date"] >= pd.to_datetime(start_date)].copy()
    if df.empty:
        return df

    # period return as percentage -> growth factor
    df["growth_factor"] = 1.0 + (pd.to_numeric(df["Total Return"], errors="coerce") / 100.0)
    df["growth_factor"] = df["growth_factor"].fillna(1.0)

    def _cum(idx_df: pd.DataFrame) -> pd.DataFrame:
        idx_df = idx_df.sort_values("Date").copy()
        idx_df["index"] = 100.0 * idx_df["growth_factor"].cumprod()
        # rebase to 100 at the first available date for each ticker
        first_val = idx_df["index"].iloc[0]
        if pd.notna(first_val) and first_val != 0:
            idx_df["index"] = idx_df["index"] * (100.0 / first_val)
        # Drop the temporary growth_factor column
        idx_df = idx_df.drop(columns=["growth_factor"], errors="ignore")
        return idx_df

    out = df.groupby("fixed_ticker", group_keys=False).apply(_cum)
    return out


def _group_cap_weights(df: pd.DataFrame) -> pd.Series:
    """Calculate market-cap weights. Returns None if weights sum to zero (fallback to equal weighting)."""
    caps = pd.to_numeric(df["Market Capitalization"], errors="coerce")
    caps = caps.where(caps > 0)
    cap_sum = caps.sum()
    
    # If sum is zero or NaN, return None to signal fallback to equal weighting
    if pd.isna(cap_sum) or cap_sum == 0:
        return None
    
    w = caps / cap_sum
    return w.fillna(0.0)


def aggregate_group_index(
    panel_indexed: pd.DataFrame,
    weighting: Weighting = "equal",
) -> pd.DataFrame:
    def _agg(g: pd.DataFrame) -> pd.Series:
        if weighting == "equal":
            val = g["index"].mean()
        else:
            w = _group_cap_weights(g)
            # If weights are None (sum to zero), fall back to equal weighting
            if w is None:
                val = g["index"].mean()
            else:
                w_array = w.to_numpy()
                # Double-check weights don't sum to zero
                if w_array.sum() == 0:
                    val = g["index"].mean()
                else:
                    val = np.average(g["index"].to_numpy(), weights=w_array)
        return pd.Series({"group_index": val})

    agg = (
        panel_indexed
        .groupby(["group", "Date"], as_index=True)
        .apply(_agg)
        .reset_index()
    )
    return agg


def build_group_indices(
    panel: pd.DataFrame,
    start_date: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Ensure necessary columns
    for c in ["fixed_ticker", "Date", "Total Return", "Market Capitalization", "group"]:
        if c not in panel.columns:
            panel[c] = np.nan

    idx_panel = _build_ticker_index(panel[["fixed_ticker", "Date", "Total Return", "Market Capitalization", "group"]], start_date)

    eq = aggregate_group_index(idx_panel, weighting="equal")
    cap = aggregate_group_index(idx_panel, weighting="cap")
    eq["weighting"] = "Equal-weighted"
    cap["weighting"] = "Cap-weighted"
    return eq, cap


def plot_group_indices(eq: pd.DataFrame, cap: pd.DataFrame, outpath: str, title_suffix: str) -> None:
    set_theme()
    data = pd.concat([eq, cap], ignore_index=True)
    g = sns.FacetGrid(data=data, row="weighting", hue="group", palette=PALETTE, sharex=True, sharey=True, height=4, aspect=1.8)
    g.map_dataframe(sns.lineplot, x="Date", y="group_index")
    g.add_legend(title="Group")
    g.set_axis_labels("Date", "Indexed return (rebased to 100)")
    g.set_titles(row_template="{row_name}")
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle(f"Indexed returns by group – {title_suffix}")
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    g.savefig(outpath, bbox_inches="tight")
    plt.show()
    plt.close(g.fig)


__all__ = [
    "build_group_indices",
    "plot_group_indices",
]


