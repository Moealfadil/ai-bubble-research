#!/usr/bin/env python3
"""Extract all tickers from Excel files and build complete group_map.csv"""

import os
import glob
import pandas as pd
from pathlib import Path

# Paths
DATA_DIR = "/Users/k./Documents/projects/AI_Bubble/ai-bubble-research/Data_preparation/datasets/final_data"
OUTPUT_CSV = "/Users/k./Documents/projects/AI_Bubble/ai-bubble-research/Data_analysis/mappings/group_map.csv"

# User-provided groups
PURE_PLAY_AI = {
    "CGNX", "CRWV", "PLTR", "PONY", "SOUN", "SYM", "TEMP", "WRD"
}

AI_EXPOSED = {
    "000660 KS", "000660.KS", "005930 KS", "005930.KS", "6526 JP", "6526.JP",
    "700 HK", "0700.HK", "ADBE", "ALAB", "AMD", "AMZN", "ANET", "APP", "ARM",
    "ASML", "AVGO", "BABA", "BIDU", "BZ", "CRM", "DOCU", "EPAM", "FB", "META",
    "GEHC", "GOOGL", "IBM", "INTC", "ISRG", "KLAC", "MRVL", "MSFT", "MU",
    "NICE", "NOW", "NVDA", "ORCL", "PANW", "QCOM", "SNOW", "SNPS", "TEAM",
    "TER", "TSM", "UBER", "VRSK"
}

NON_AI = {
    "25557878D TT", "3690 HK", "4755 JP", "6588 JP", "AVAV", "CLS", "CSCO",
    "EBAY", "EXPN LN", "HUT", "IFX GR", "IRM", "NFLX", "NOC", "QUBT", "SHOP",
    "SIE GR", "SPLK", "STM IM", "TRI", "TWLO", "TWTR", "WDAY"
}

def extract_all_tickers(data_dir: str) -> set[str]:
    """Extract all unique fixed_ticker values from Excel files."""
    files = glob.glob(os.path.join(data_dir, "*.xlsx"))
    all_tickers = set()
    
    for fp in files:
        try:
            df = pd.read_excel(fp)
            if "fixed_ticker" in df.columns:
                tickers = df["fixed_ticker"].astype(str).str.strip().unique()
                all_tickers.update(tickers)
        except Exception as e:
            print(f"Warning: Could not read {os.path.basename(fp)}: {e}")
    
    return all_tickers

def assign_group(ticker: str) -> str:
    """Assign ticker to group based on user-provided lists."""
    ticker_clean = ticker.strip()
    
    if ticker_clean in PURE_PLAY_AI:
        return "Pure-Play AI"
    elif ticker_clean in AI_EXPOSED:
        return "AI-Exposed / Big Tech"
    elif ticker_clean in NON_AI:
        return "Non-AI / Control Group"
    else:
        # Default to Non-AI for unmapped tickers
        return "Non-AI / Control Group"

def main():
    print("Extracting tickers from Excel files...")
    all_tickers = extract_all_tickers(DATA_DIR)
    print(f"Found {len(all_tickers)} unique tickers")
    
    # Build mapping
    mapping = []
    for ticker in sorted(all_tickers):
        group = assign_group(ticker)
        mapping.append({"fixed_ticker": ticker, "group": group})
    
    df_map = pd.DataFrame(mapping)
    
    # Save
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df_map.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df_map)} mappings to {OUTPUT_CSV}")
    
    # Print summary
    print("\nGroup distribution:")
    print(df_map["group"].value_counts())

if __name__ == "__main__":
    main()

