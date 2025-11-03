"""
Stock Analysis Data Preprocessing Script

This script processes Excel files from the stock_analysis directory structure:
- Transposes data (swaps rows and columns)
- Combines 4 Excel files per company using date as ID
- Adds ticker column as first column
- Generates Excel output files named by company folder
- Maintains currency folder structure

Author: AI Bubble Research Team
Date: October 26, 2025
"""

import pandas as pd
import os
import re

def extract_ticker_from_filename(filename):
    """
    Extract ticker symbol from filename
    Example: 'nvda-balance-sheet-quarterly.xlsx' -> 'NVDA'
    """
    ticker = filename.split('-')[0].upper()
    return ticker

def transpose_dataframe(df):
    """
    Transpose dataframe - swap rows and columns
    Assumes first column contains metric names and first row contains dates
    """
    if df.empty:
        return df
    
    # Set the first column as index (metrics)
    df_transposed = df.set_index(df.columns[0]).T
    
    # Reset index to make dates a column
    df_transposed = df_transposed.reset_index()
    df_transposed = df_transposed.rename(columns={'index': 'Date'})
    
    return df_transposed

def process_company_files(company_folder_path, currency):
    """
    Process all Excel files for a single company
    """
    company_name = os.path.basename(company_folder_path)
    print(f"Processing company: {company_name}")
    
    # Find all Excel files in the company folder
    excel_files = []
    for file in os.listdir(company_folder_path):
        if file.endswith('.xlsx') or file.endswith('.xls'):
            excel_files.append(file)
    
    if len(excel_files) == 0:
        print(f"No Excel files found in {company_name}")
        return None
    
    # Extract ticker from first file
    ticker = extract_ticker_from_filename(excel_files[0])
    
    # Dictionary to store processed dataframes
    dataframes = {}
    
    # Process each Excel file
    for file in excel_files:
        file_path = os.path.join(company_folder_path, file)
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Transpose the data
            df_transposed = transpose_dataframe(df)
            
            if df_transposed.empty:
                continue
            
            # Determine file type from filename
            if 'balance-sheet' in file:
                file_type = 'balance_sheet'
            elif 'income-statement' in file:
                file_type = 'income_statement'
            elif 'cash-flow' in file:
                file_type = 'cash_flow'
            elif 'ratios' in file:
                file_type = 'ratios'
            else:
                file_type = 'unknown'
            
            # Keep original column names (no prefix)
            dataframes[file_type] = df_transposed
            
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
            continue
    
    if not dataframes:
        return None
    
    # Merge all dataframes on Date
    combined_df = None
    for file_type, df in dataframes.items():
        if combined_df is None:
            combined_df = df
        else:
            combined_df = pd.merge(combined_df, df, on='Date', how='outer')
    
    if combined_df is None:
        return None
    
    # Add ticker column as first column
    combined_df.insert(0, 'Ticker', ticker)
    
    # Add currency column as second column
    combined_df.insert(1, 'Currency', currency)
    
    # Sort by Date
    if 'Date' in combined_df.columns:
        combined_df = combined_df.sort_values('Date')
    
    return combined_df, company_name, ticker

def main():
    """
    Main function to process all companies in the stock_analysis directory
    """
    base_path = r"D:\MIT\Develop_Workflow\ELO2\ai-bubble-research\Data_collection\indicators\stock_analysis"
    output_base_path = r"D:\MIT\Develop_Workflow\ELO2\ai-bubble-research\Data_preparation\processed_data"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_base_path, exist_ok=True)
    
    # Get all currency folders
    currency_folders = [d for d in os.listdir(base_path) 
                       if os.path.isdir(os.path.join(base_path, d)) and d != '.DS_Store']
    
    print(f"Found currency folders: {currency_folders}")
    
    processed_count = 0
    error_count = 0
    
    # Process each currency folder
    for currency in currency_folders:
        currency_path = os.path.join(base_path, currency)
        print(f"Processing currency: {currency}")
        
        # Create currency folder in output directory
        output_currency_path = os.path.join(output_base_path, currency)
        os.makedirs(output_currency_path, exist_ok=True)
        
        # Get all company folders in this currency
        company_folders = [d for d in os.listdir(currency_path) 
                          if os.path.isdir(os.path.join(currency_path, d)) and d != '.DS_Store']
        
        # Process each company
        for company_folder in company_folders:
            company_folder_path = os.path.join(currency_path, company_folder)
            
            try:
                result = process_company_files(company_folder_path, currency)
                
                if result is not None:
                    combined_df, company_name, ticker = result
                    
                    # Create output filename using only company name
                    safe_company_name = re.sub(r'[^\w\s-]', '', company_name).strip()
                    safe_company_name = re.sub(r'[-\s]+', '_', safe_company_name)
                    output_filename = f"{safe_company_name}.xlsx"
                    output_file_path = os.path.join(output_currency_path, output_filename)
                    
                    # Save to Excel
                    combined_df.to_excel(output_file_path, index=False)
                    print(f"Saved: {currency}/{output_filename}")
                    processed_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"Error processing {company_folder}: {str(e)}")
                error_count += 1
                continue
    
    print("Processing complete!")
    print(f"Successfully processed: {processed_count} companies")
    print(f"Errors/Skipped: {error_count} companies")
    print(f"Output directory: {output_base_path}")

if __name__ == "__main__":
    main()