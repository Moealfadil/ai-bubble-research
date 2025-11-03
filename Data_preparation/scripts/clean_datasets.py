"""
Dataset Cleaning Script for AI Bubble Research

This script cleans the processed datasets to include only specified columns
and filters data to 2015-2025 timeframe while maintaining currency structure.

Author: AI Bubble Research Team
Date: October 31, 2025
"""

import pandas as pd
import os

def get_desired_columns():
    """
    Define the 33 columns to keep in the cleaned datasets
    """
    return [
        # Identifiers
        'Ticker',
        'Currency', 
        'Date',
        
        # Market Valuation Metrics
        'Market Capitalization',
        'Enterprise Value',
        'PE Ratio',
        'PS Ratio',
        'PB Ratio',
        'P/FCF Ratio',
        
        # Fundamentals & Performance Metrics
        'Revenue',
        'Revenue Growth',
        'Gross Margin',
        'Operating Income',
        'Operating Margin',
        'Net Income_y',  
        'Net Income Growth',
        'EPS (Diluted)',
        'EPS Growth',
        'Operating Cash Flow',
        'Capital Expenditures',
        'Free Cash Flow',
        'Free Cash Flow Margin_y',
        'EBITDA',
        
        # Returns & Efficiency
        'Total Return',
        'Return on Invested Capital (ROIC)',
        
        # Capital & Financial Health
        'Total Debt',
        'Net Cash (Debt)',
        'Debt/Equity',
        'Buyback Yield',
        
        # AI-Related or Internal Spending
        'Research & Development',
        'Share-Based Compensation'
    ]

def filter_date_range(df, start_year=2015, end_year=2025):
    """
    Filter dataframe to include only data from specified year range
    """
    if 'Date' not in df.columns:
        print("Warning: No Date column found")
        return df
    
    # Convert Date column to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Filter by year range
    start_date = pd.Timestamp(f'{start_year}-01-01')
    end_date = pd.Timestamp(f'{end_year}-12-31')
    
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    return filtered_df

def clean_company_file(file_path, desired_columns):
    """
    Clean a single company Excel file
    """
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        if df.empty:
            print(f"Empty file: {file_path}")
            return None
        
        # Filter by date range (2015-2025)
        df = filter_date_range(df)
        
        if df.empty:
            print(f"No data in 2015-2025 range for: {file_path}")
            return None
        
        # Select columns that exist in the data
        available_columns = [col for col in desired_columns if col in df.columns]
        missing_columns = [col for col in desired_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Missing columns in {os.path.basename(file_path)}: {missing_columns[:3]}{'...' if len(missing_columns) > 3 else ''}")
        
        # Select available columns
        if available_columns:
            cleaned_df = df[available_columns].copy()
            
            # Sort by date
            if 'Date' in cleaned_df.columns:
                cleaned_df = cleaned_df.sort_values('Date')
            
            return cleaned_df
        else:
            print(f"No matching columns found in: {file_path}")
            return None
            
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None

def process_currency_folder(currency_path, output_currency_path, desired_columns):
    """
    Process all files in a currency folder
    """
    if not os.path.exists(currency_path):
        return
    
    # Create output currency folder
    os.makedirs(output_currency_path, exist_ok=True)
    
    processed_count = 0
    total_files = 0
    
    # Process each Excel file
    for filename in os.listdir(currency_path):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            total_files += 1
            file_path = os.path.join(currency_path, filename)
            
            # Clean the file
            cleaned_df = clean_company_file(file_path, desired_columns)
            
            if cleaned_df is not None and not cleaned_df.empty:
                # Save cleaned file
                output_path = os.path.join(output_currency_path, filename)
                cleaned_df.to_excel(output_path, index=False)
                processed_count += 1
                
                if processed_count % 10 == 0:
                    print(f"Processed {processed_count}/{total_files} files in {os.path.basename(currency_path)}")
    
    print(f"Currency {os.path.basename(currency_path)}: {processed_count}/{total_files} files processed")
    return processed_count, total_files

def main():
    """
    Main function to clean all datasets
    """
    # Define paths
    input_base_path = r"D:\MIT\Develop_Workflow\ELO2\ai-bubble-research\Data_preparation\datasets\processed_data"
    output_base_path = r"D:\MIT\Develop_Workflow\ELO2\ai-bubble-research\Data_preparation\datasets\cleaned_data"
    
    # Create output directory
    os.makedirs(output_base_path, exist_ok=True)
    
    # Get desired columns
    desired_columns = get_desired_columns()
    
    print("Starting dataset cleaning...")
    print(f"Input directory: {input_base_path}")
    print(f"Output directory: {output_base_path}")
    print(f"Target columns: {len(desired_columns)}")
    print("Date range: 2015-2025")
    print("-" * 50)
    
    # Get all currency folders
    currency_folders = [d for d in os.listdir(input_base_path) 
                       if os.path.isdir(os.path.join(input_base_path, d))]
    
    total_processed = 0
    total_files = 0
    
    # Process each currency
    for currency in sorted(currency_folders):
        currency_path = os.path.join(input_base_path, currency)
        output_currency_path = os.path.join(output_base_path, currency)
        
        print(f"\nProcessing {currency} currency...")
        processed, files = process_currency_folder(currency_path, output_currency_path, desired_columns)
        total_processed += processed
        total_files += files
    
    print("\n" + "=" * 50)
    print("CLEANING SUMMARY")
    print("=" * 50)
    print(f"Total files processed: {total_processed}/{total_files}")
    print(f"Success rate: {total_processed/total_files*100:.1f}%" if total_files > 0 else "No files found")
    print(f"Output directory: {output_base_path}")
    
    # Display column list summary
    print(f"\nColumns selected: {len(desired_columns)}")
    print("Selected columns:")
    for i, column in enumerate(desired_columns, 1):
        print(f"{i:2d}. {column}")
    
    print("\n✅ Dataset cleaning completed!")

if __name__ == "__main__":
    main()