from __future__ import annotations

import os
import glob
from typing import Iterable, Tuple

import pandas as pd
import numpy as np


DEFAULT_GROUP_LABEL = "Non-AI / Control Group"


def read_group_map(group_map_csv: str) -> pd.DataFrame:
    """Read the ticker → group mapping file.

    The file must contain columns: fixed_ticker, group.
    """
    mapping = pd.read_csv(group_map_csv, dtype=str)
    mapping.columns = [c.strip() for c in mapping.columns]
    if "fixed_ticker" not in mapping or "group" not in mapping:
        raise ValueError("group_map.csv must have columns: fixed_ticker, group")
    mapping["fixed_ticker"] = mapping["fixed_ticker"].str.strip()
    mapping["group"] = mapping["group"].str.strip()
    return mapping.drop_duplicates(subset=["fixed_ticker"], keep="last")


def list_excel_files(data_dir: str) -> list[str]:
    pattern = os.path.join(data_dir, "*.xlsx")
    files = sorted(glob.glob(pattern))
    return files


def _coerce_numeric(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


def _ensure_required_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Minimal required for downstream steps
    required = [
        "fixed_ticker",
        "Date",
        "Total Return",
        "Market Capitalization",
    ]
    for c in required:
        if c not in df.columns:
            df[c] = np.nan
    return df


NUMERIC_COLUMNS = [
    "open_price", "close_price", "high_price", "low_price", "shares_outstanding",
    "Market Capitalization", "Enterprise Value", "PE Ratio", "PS Ratio", "PB Ratio",
    "P/FCF Ratio", "Revenue", "Revenue Growth", "Gross Margin", "Operating Income",
    "Operating Margin", "Net Income_y", "Net Income Growth", "EPS (Diluted)",
    "EPS Growth", "Operating Cash Flow", "Capital Expenditures", "Free Cash Flow",
    "Free Cash Flow Margin_y", "EBITDA", "Total Return", "Return on Invested Capital (ROIC)",
    "Total Debt", "Net Cash (Debt)", "Debt/Equity", "Buyback Yield", "Research & Development",
    "Share-Based Compensation", "PEG", "EPS_Growth_pct_used", "R&D_pct_of_Revenue",
    "R&D_to_MarketCap",
]


def read_single_excel(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df = _parse_dates(df)
    df = _coerce_numeric(df, NUMERIC_COLUMNS)
    df = _ensure_required_columns(df)
    # Standardize ticker formatting - convert to string to avoid mixed types
    if "fixed_ticker" in df.columns:
        df["fixed_ticker"] = df["fixed_ticker"].astype(str).str.strip()
    if "Ticker" in df.columns:
        df["Ticker"] = df["Ticker"].astype(str).str.strip()
    if "Currency" in df.columns:
        df["Currency"] = df["Currency"].astype(str).str.strip()
    if "Original Currency" in df.columns:
        df["Original Currency"] = df["Original Currency"].astype(str).str.strip()
    return df


def load_all_excels(data_dir: str) -> pd.DataFrame:
    files = list_excel_files(data_dir)
    frames: list[pd.DataFrame] = []
    for fp in files:
        try:
            frames.append(read_single_excel(fp))
        except Exception as exc:  # narrow failure to a single file
            # Skip problematic file but keep going
            print(f"WARN: failed reading {fp}: {exc}")
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    # Sort for stable latest-quarter extraction
    df = df.sort_values(["fixed_ticker", "Date"]).reset_index(drop=True)
    return df


def attach_groups(panel: pd.DataFrame, group_map: pd.DataFrame) -> pd.DataFrame:
    panel = panel.copy()
    panel = panel.merge(group_map, on="fixed_ticker", how="left")
    panel["group"] = panel["group"].fillna(DEFAULT_GROUP_LABEL)
    return panel


def winsorize_series(s: pd.Series, lower_pct: float = 0.01, upper_pct: float = 0.99) -> pd.Series:
    if s.empty:
        return s
    lo, hi = s.quantile([lower_pct, upper_pct]).tolist()
    return s.clip(lower=lo, upper=hi)


def latest_cross_section(panel: pd.DataFrame) -> pd.DataFrame:
    """Return latest row per ticker (by Date)."""
    if panel.empty:
        return panel
    idx = panel.groupby("fixed_ticker")["Date"].idxmax()
    return panel.loc[idx].reset_index(drop=True)


def _prepare_for_parquet(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all columns are parquet-compatible by fixing types."""
    df = df.copy()
    
    # List of known string columns that should always be strings
    # Note: Ticker is dropped before this function is called
    string_columns = ["fixed_ticker", "Currency", "Original Currency", "group"]
    
    # Convert known string columns using a method that ensures pure Python strings
    for col in string_columns:
        if col in df.columns:
            # Use list comprehension to force conversion to Python strings
            # This ensures PyArrow sees actual string objects, not mixed types
            converted = []
            for val in df[col]:
                if pd.isna(val) or val is None:
                    converted.append(None)
                else:
                    # Force to Python string
                    s = str(val)
                    # Clean up
                    if s.lower() in ['nan', 'none', '<na>', 'nat', '']:
                        converted.append(None)
                    else:
                        converted.append(s.strip())
            # Replace the column using pd.Series to ensure proper type handling
            df[col] = pd.Series(converted, dtype='object', index=df.index)
    
    # Convert ALL object columns to ensure consistency
    for col in df.columns:
        if col not in string_columns:
            if df[col].dtype == 'object':
                # Convert object columns that might have mixed types
                try:
                    converted = []
                    for val in df[col]:
                        if pd.isna(val) or val is None:
                            converted.append(None)
                        else:
                            s = str(val)
                            if s.lower() in ['nan', 'none', '<na>', 'nat', '']:
                                converted.append(None)
                            else:
                                converted.append(s)
                    df[col] = pd.Series(converted, dtype='object', index=df.index)
                except Exception as e:
                    # If conversion fails, skip this column
                    print(f"Warning: Could not convert column {col}: {e}")
            elif df[col].dtype.name == 'category':
                # Convert categories to string
                converted = [str(v) if pd.notna(v) else None for v in df[col]]
                cleaned = [None if (v and v.lower() in ['nan', 'none', '<na>', '']) else v for v in converted]
                df[col] = pd.Series(cleaned, dtype='object', index=df.index)
    
    return df


def build_and_save_panel(
    data_dir: str,
    group_map_csv: str,
    parquet_path: str,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load raw excels, harmonize, attach groups, and persist panel.

    Returns (full_panel, latest_cs)
    """
    raw = load_all_excels(data_dir)
    mapping = read_group_map(group_map_csv)
    panel = attach_groups(raw, mapping)
    
    # Drop Ticker column upfront - we use fixed_ticker, so Ticker is redundant
    # This avoids parquet conversion issues with mixed types
    if "Ticker" in panel.columns:
        panel = panel.drop(columns=["Ticker"])
    
    # Prepare for parquet (fix type issues)
    panel_clean = _prepare_for_parquet(panel)
    
    # Final aggressive cleanup: ensure ALL object columns are pure strings
    # This is a safety net in case the conversion didn't catch everything
    for col in panel_clean.columns:
        if panel_clean[col].dtype == 'object':
            # Double-check: convert any remaining non-strings
            def _force_str(x):
                if pd.isna(x) or x is None:
                    return None
                if isinstance(x, str):
                    return x
                return str(x)
            panel_clean[col] = panel_clean[col].apply(_force_str)
            # Ensure it's still object dtype
            panel_clean[col] = panel_clean[col].astype('object')
    
    # Persist
    os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
    try:
        panel_clean.to_parquet(parquet_path, index=False)
    except Exception as e:
        # If still failing, try dropping all problematic object columns except essential ones
        print(f"Error saving to parquet: {e}")
        print("Attempting to save with minimal columns...")
        # Keep only essential string columns and all non-object columns
        essential_string_cols = ["fixed_ticker", "group"]
        numeric_cols = [c for c in panel_clean.columns if panel_clean[c].dtype != 'object']
        date_cols = [c for c in panel_clean.columns if pd.api.types.is_datetime64_any_dtype(panel_clean[c])]
        essential_cols = essential_string_cols + numeric_cols + date_cols
        # Filter to only columns that exist
        essential_cols = [c for c in essential_cols if c in panel_clean.columns]
        panel_minimal = panel_clean[essential_cols].copy()
        panel_minimal.to_parquet(parquet_path, index=False)
        print(f"Saved with {len(essential_cols)} columns (dropped {len(panel_clean.columns) - len(essential_cols)} object columns). Full panel available in memory.")
    
    latest = latest_cross_section(panel)
    return panel, latest


__all__ = [
    "read_group_map",
    "list_excel_files",
    "read_single_excel",
    "load_all_excels",
    "attach_groups",
    "winsorize_series",
    "latest_cross_section",
    "build_and_save_panel",
]


