"""Add valuation and market columns to normalized dataset files.

This script will:
- For each file in datasets/normalized_data (Excel), compute and add:
  - PEG (PE Ratio / EPS Growth percent)
  - R&D % of Revenue
  - R&D to Market Cap
- For each company, pull latest open/close/high/low and shares outstanding
  from the matching CSV in Data_collection/indicators/complete_data_improved
  (matching is done via company name derived from filename -> underscores to spaces,
  and case-insensitive normalized matching against CSV "company name" column).

Outputs are written as Excel files to datasets/final_data with the same filename.

Logging is intentionally minimal.
"""

from pathlib import Path
import argparse
import logging
import re
import pandas as pd
import numpy as np


logger = logging.getLogger("add_columns")


def get_exchange_rates():
    """Exchange rates for currency conversion (same as currency_conversion.py)."""
    return {
        'USD': 1.0,
        'EUR': 1.157,
        'HKD': 0.1287,
        'JPY': 0.00650,
        'KRW': 0.000699,
        'SEK': 0.1060,
        'TWD': 0.0325,
        'CHF': 1.248
    }


def normalize_str(s: str) -> str:
    """Normalize company name for matching."""
    if s is None:
        return ""
    s = str(s).upper()
    return re.sub(r"[^A-Z0-9]", "", s)


def read_complete_files(complete_dir: Path):
    """Read CSVs and map normalized company names to dataframes with price data."""
    mapping = {}
    for p in complete_dir.glob("*.csv"):
        try:
            df = pd.read_csv(p, low_memory=False)
        except Exception:
            try:
                df = pd.read_csv(p, encoding="latin1", low_memory=False)
            except Exception:
                continue

        # Extract company names and parse dates
        if "company_name" not in df.columns or "date" not in df.columns:
            continue
            
        try:
            df['parsed_date'] = pd.to_datetime(df["date"], errors='coerce', utc=True).dt.date
        except Exception:
            df['parsed_date'] = pd.NaT

        # Map each unique company name to this dataframe
        for company in df["company_name"].dropna().astype(str).unique():
            key = normalize_str(company)
            if key not in mapping:
                mapping[key] = {"path": p, "df": df}

    return mapping
def compute_new_columns(df: pd.DataFrame):
    """Compute PEG, R&D ratios per row."""
    # Convert columns to numeric
    pe = pd.to_numeric(df.get("PE Ratio"), errors='coerce')
    eps = pd.to_numeric(df.get("EPS Growth"), errors='coerce')
    rd = pd.to_numeric(df.get("Research & Development"), errors='coerce')
    revenue = pd.to_numeric(df.get("Revenue"), errors='coerce')
    mktcap = pd.to_numeric(df.get("Market Capitalization"), errors='coerce')

    # Normalize EPS to percent if it's a decimal
    eps_pct = eps.apply(lambda x: x * 100 if pd.notna(x) and abs(x) <= 1 else x)

    # Compute ratios and replace inf with NaN
    peg = (pe / eps_pct).replace([np.inf, -np.inf], np.nan)
    rd_pct = (rd / revenue).replace([np.inf, -np.inf], np.nan)
    rd_mkt = (rd / mktcap).replace([np.inf, -np.inf], np.nan)

    return {
        "PEG": peg,
        "EPS_Growth_pct_used": eps_pct,
        "R&D_pct_of_Revenue": rd_pct,
        "R&D_to_MarketCap": rd_mkt,
    }


def merge_price_data_by_date(norm_df: pd.DataFrame, complete_df: pd.DataFrame):
    """Merge price data from complete_df into norm_df based on closest date match."""
    if "Date" not in norm_df.columns or 'parsed_date' not in complete_df.columns:
        return None
    
    # Parse dates for merge
    norm_df = norm_df.copy()
    complete_df = complete_df.copy()
    norm_df['temp_date'] = pd.to_datetime(norm_df["Date"], errors='coerce').dt.tz_localize(None)
    complete_df['temp_date'] = pd.to_datetime(complete_df['parsed_date'], errors='coerce')
    
    # Select price columns from complete data
    price_cols = ['open_price', 'close_price', 'high_price', 'low_price', 'shares_outstanding', 'ticker']
    merge_cols = ['temp_date'] + [c for c in price_cols if c in complete_df.columns]
    complete_subset = complete_df[merge_cols].dropna(subset=['temp_date'])
    
    # Merge on nearest date
    merged = pd.merge_asof(
        norm_df.sort_values('temp_date').dropna(subset=['temp_date']),
        complete_subset.sort_values('temp_date'),
        on='temp_date',
        direction='nearest'
    ).drop(columns=['temp_date'])
    
    # Rename ticker to fixed_ticker
    if 'ticker' in merged.columns:
        merged = merged.rename(columns={'ticker': 'fixed_ticker'})
    
    # Convert prices to USD
    if "Original Currency" in merged.columns:
        currency = merged["Original Currency"].dropna().iloc[0] if not merged["Original Currency"].dropna().empty else 'USD'
        rate = get_exchange_rates().get(currency, 1.0)
        for col in ['open_price', 'close_price', 'high_price', 'low_price']:
            if col in merged.columns:
                merged[col] = pd.to_numeric(merged[col], errors='coerce') * rate
    
    # Reorder: put price columns after Date
    date_idx = merged.columns.get_loc("Date")
    new_cols = ['open_price', 'close_price', 'high_price', 'low_price', 'shares_outstanding', 'fixed_ticker']
    existing_new = [c for c in new_cols if c in merged.columns]
    other_cols = [c for c in merged.columns if c not in existing_new]
    merged = merged[other_cols[:date_idx+1] + existing_new + other_cols[date_idx+1:]]
    
    return merged


def process_all(norm_dir: Path, complete_dir: Path, out_dir: Path, dry_run: bool = False):
    norm_dir = Path(norm_dir)
    complete_dir = Path(complete_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    mapping = read_complete_files(complete_dir)

    files = list(norm_dir.glob("*.xlsx")) + list(norm_dir.glob("*.xls")) + list(norm_dir.glob("*.csv"))
    processed = 0
    missing = []

    for f in files:
        # derive company name from filename: underscores -> spaces
        stem = f.stem
        company_name = stem.replace("_", " ")
        key = normalize_str(company_name)

        try:
            if f.suffix.lower() in (".xls", ".xlsx"):
                df = pd.read_excel(f)
            else:
                df = pd.read_csv(f)
        except Exception:
            # skip problematic files
            missing.append((f.name, "read_error"))
            continue

        # Compute new columns (PEG, R&D ratios)
        new_vals = compute_new_columns(df)
        df["PEG"] = new_vals["PEG"]
        df["EPS_Growth_pct_used"] = new_vals["EPS_Growth_pct_used"]
        df["R&D_pct_of_Revenue"] = new_vals["R&D_pct_of_Revenue"]
        df["R&D_to_MarketCap"] = new_vals["R&D_to_MarketCap"]

        # Find matching complete data (exact or fuzzy match)
        price_info = mapping.get(key)
        if not price_info:
            for mk in mapping:
                if mk == key or mk.startswith(key) or key.startswith(mk):
                    price_info = mapping[mk]
                    break

        # Merge price data or add NaN columns
        if price_info:
            final_df = merge_price_data_by_date(df, price_info["df"])
        
        if not price_info or final_df is None:
            missing.append((f.name, company_name if not price_info else "no_date_column"))
            for col in ["open_price", "close_price", "high_price", "low_price", "shares_outstanding", "fixed_ticker"]:
                df[col] = np.nan
            final_df = df

        out_path = out_dir / f.name
        if not dry_run:
            try:
                # save as excel for xls/xlsx sources, otherwise csv
                if f.suffix.lower() in (".xls", ".xlsx"):
                    final_df.to_excel(out_path, index=False)
                else:
                    final_df.to_csv(out_path, index=False)
            except Exception as e:
                missing.append((f.name, f"write_error:{e}"))
                continue

        processed += 1

    # minimal logging
    logger.info(f"Processed {processed} files; {len(missing)} missing/unmatched")
    if missing:
        logger.debug(f"Missing examples: {missing[:10]}")


def main():
    parser = argparse.ArgumentParser(description="Add PEG, R&D ratios and price info to normalized data files.")
    parser.add_argument("--normalized", default=r"d:\\MIT\\Develop_Workflow\\ELO2\\ai-bubble-research\\Data_preparation\\datasets\\normalized_data", help="Path to normalized data folder")
    parser.add_argument("--complete", default=r"d:\\MIT\\Develop_Workflow\\ELO2\\ai-bubble-research\\Data_collection\\indicators\\complete_data_improved", help="Path to complete CSVs folder")
    parser.add_argument("--out", default=r"d:\\MIT\\Develop_Workflow\\ELO2\\ai-bubble-research\\Data_preparation\\datasets\\final_data", help="Output folder")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files")
    args = parser.parse_args()

    # minimal logging: INFO only
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    process_all(Path(args.normalized), Path(args.complete), Path(args.out), dry_run=args.dry_run)


if __name__ == "__main__":
    main()

