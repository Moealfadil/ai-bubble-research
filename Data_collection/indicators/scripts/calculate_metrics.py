import pandas as pd
import os
import glob
from datetime import datetime

# ==== CONFIG ====
# Get script directory for absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# Input and output directories
ALPHA_DIR = os.path.join(BASE_DIR, "alpha")
OUTPUT_DIR = os.path.join(BASE_DIR, "calculated_data")

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==== DATA LOADING ====
def load_alpha_data():
    """Read all CSV files from alpha directory"""
    csv_files = glob.glob(os.path.join(ALPHA_DIR, "*_alpha_data.csv"))
    
    if not csv_files:
        print(f"❌ No CSV files found in {ALPHA_DIR}")
        return None
    
    print(f"📊 Found {len(csv_files)} CSV files in alpha directory")
    
    all_data = []
    processed_count = 0
    
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            if not df.empty:
                all_data.append(df)
                processed_count += 1
            else:
                print(f"⚠️  Skipping empty file: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ Error reading {os.path.basename(file_path)}: {e}")
    
    if not all_data:
        print("❌ No valid data found in any CSV files")
        return None
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"✅ Successfully loaded data from {processed_count} companies")
    print(f"📊 Total records: {len(combined_df)}")
    
    return combined_df

# ==== METRICS CALCULATION ====
def calculate_all_metrics(df):
    """Calculate all financial metrics for the dataframe
    
    Args:
        df: DataFrame with financial data and fiscalDateEnding column
    
    Returns:
        DataFrame with calculated metrics added
    """
    df = df.copy()
    
    # Convert all numeric columns
    numeric_cols = [col for col in df.columns if col not in ['fiscalDateEnding', 'ticker', 'priceDate']]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Sort by ticker and date for proper calculation
    df = df.sort_values(['ticker', 'fiscalDateEnding'], ascending=[True, True])
    
    # Group by ticker for ticker-specific calculations
    df_list = []
    
    for ticker in df['ticker'].unique():
        ticker_df = df[df['ticker'] == ticker].copy()
        
        # 1. Revenue Growth (%)
        ticker_df['revenueGrowthPct'] = ticker_df['totalRevenue'].pct_change(fill_method=None) * 100        
        # 2. Net Income Margin (%)
        ticker_df['netIncomeMarginPct'] = (ticker_df['netIncome'] / ticker_df['totalRevenue']) * 100
        
        # 3. EPS Surprise (%) - only if earnings data available
        if 'reportedEPS' in ticker_df.columns and 'estimatedEPS' in ticker_df.columns:
            # Handle division by zero and missing values
            eps_surprise = ((ticker_df['reportedEPS'] - ticker_df['estimatedEPS']) / 
                           ticker_df['estimatedEPS'].abs().replace(0, pd.NA)) * 100
            ticker_df['epsSurprisePct'] = eps_surprise
        else:
            ticker_df['epsSurprisePct'] = None
        
        # 4. Free Cash Flow (FCF) - only if cash flow data available
        if 'operatingCashflow' in ticker_df.columns and 'capitalExpenditures' in ticker_df.columns:
            ticker_df['freeCashFlow'] = ticker_df['operatingCashflow'] + ticker_df['capitalExpenditures']  # capEx is usually negative
        else:
            ticker_df['freeCashFlow'] = None
        
        # 5. Debt-to-Equity Ratio - only if balance sheet data available
        if 'totalLiabilities' in ticker_df.columns and 'totalShareholderEquity' in ticker_df.columns:
            ticker_df['debtToEquityRatio'] = ticker_df['totalLiabilities'] / ticker_df['totalShareholderEquity']
        else:
            ticker_df['debtToEquityRatio'] = None
        
        # 6. Cash Ratio - only if balance sheet data available
        if 'cashAndCashEquivalentsAtCarryingValue' in ticker_df.columns and 'shortTermDebt' in ticker_df.columns:
            ticker_df['cashRatio'] = ticker_df['cashAndCashEquivalentsAtCarryingValue'] / ticker_df['shortTermDebt']
        else:
            ticker_df['cashRatio'] = None
        
        # 7. R&D Intensity - only if income statement data available
        if 'researchAndDevelopment' in ticker_df.columns and 'totalRevenue' in ticker_df.columns:
            ticker_df['rdIntensityPct'] = (ticker_df['researchAndDevelopment'] / ticker_df['totalRevenue']) * 100
        else:
            ticker_df['rdIntensityPct'] = None
        
        # 8. Buyback Ratio - only if cash flow and income statement data available
        if 'proceedsFromRepurchaseOfEquity' in ticker_df.columns and 'netIncome' in ticker_df.columns:
            ticker_df['buybackRatio'] = -ticker_df['proceedsFromRepurchaseOfEquity'] / ticker_df['netIncome']
        else:
            ticker_df['buybackRatio'] = None
        
        # 9. P/E and P/S Ratios (using historical market cap)
        if 'marketCap' in ticker_df.columns and 'netIncome' in ticker_df.columns:
            ticker_df['peRatio'] = ticker_df['marketCap'] / ticker_df['netIncome']
        else:
            ticker_df['peRatio'] = None
        
        if 'marketCap' in ticker_df.columns and 'totalRevenue' in ticker_df.columns:
            ticker_df['psRatio'] = ticker_df['marketCap'] / ticker_df['totalRevenue']
        else:
            ticker_df['psRatio'] = None
        
        # 10. Price-to-Book Ratio (using historical market cap)
        if 'marketCap' in ticker_df.columns and 'totalShareholderEquity' in ticker_df.columns:
            ticker_df['priceToBookRatio'] = ticker_df['marketCap'] / ticker_df['totalShareholderEquity']
        else:
            ticker_df['priceToBookRatio'] = None
        
        # Sort back to newest first for this ticker
        ticker_df = ticker_df.sort_values('fiscalDateEnding', ascending=False)
        df_list.append(ticker_df)
    
    # Combine all ticker dataframes
    final_df = pd.concat(df_list, ignore_index=True)
    
    return final_df

# ==== PROCESS ALL COMPANIES ====
def process_all_companies():
    """Process all companies and combine into single dataset"""
    print("\n" + "="*60)
    print("FINANCIAL METRICS CALCULATION")
    print("="*60)
    
    # Load data
    print("📊 Loading data from alpha directory...")
    combined_df = load_alpha_data()
    
    if combined_df is None:
        print("❌ Failed to load data. Exiting.")
        return False
    
    # Calculate metrics
    print("🧮 Calculating financial metrics...")
    try:
        final_df = calculate_all_metrics(combined_df)
        print(f"✅ Successfully calculated metrics for {len(final_df)} records")
    except Exception as e:
        print(f"❌ Error calculating metrics: {e}")
        return False
    
    # Save combined dataset
    print("💾 Saving combined dataset...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"complete_data_with_metrics_{timestamp}.csv")
    
    try:
        final_df.to_csv(output_file, index=False)
        print(f"✅ Successfully saved combined dataset")
        print(f"📁 Output file: {output_file}")
        print(f"📊 Total records: {len(final_df)}")
        print(f"📊 Companies: {final_df['ticker'].nunique()}")
        
        # Show date range
        if 'fiscalDateEnding' in final_df.columns:
            date_range = f"{final_df['fiscalDateEnding'].min()} to {final_df['fiscalDateEnding'].max()}"
            print(f"📅 Date range: {date_range}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving dataset: {e}")
        return False

# ==== MAIN EXECUTION ====
def main():
    """Main execution function"""
    success = process_all_companies()
    
    if success:
        print("\n🎉 Metrics calculation completed successfully!")
    else:
        print("\n❌ Metrics calculation failed!")
    
    print("="*60)

if __name__ == "__main__":
    main()
