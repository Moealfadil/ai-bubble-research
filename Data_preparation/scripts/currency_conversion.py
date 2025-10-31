"""
Currency Conversion Script

This script converts all financial data from various currencies to USD
and saves the normalized files to the normalized_data directory.

Author: AI Bubble Research Team
Date: October 31, 2025
"""

import pandas as pd
import os

def get_exchange_rates():
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

def get_monetary_columns():
    return [
        'Market Capitalization',
        'Enterprise Value',
        'Revenue',
        'Operating Income',
        'Net Income_y',
        'EPS (Diluted)',
        'Operating Cash Flow',
        'Capital Expenditures',
        'Free Cash Flow',
        'EBITDA',
        'Total Debt',
        'Net Cash (Debt)',
        'Research & Development',
        'Share-Based Compensation'
    ]

def convert_file(file_path, currency_code, exchange_rate, monetary_columns, output_path):
    try:
        df = pd.read_excel(file_path)
        df['Original Currency'] = currency_code
        
        for col in monetary_columns:
            if col in df.columns:
                df[col] = df[col] * exchange_rate
        
        df['Currency'] = 'USD'
        df.to_excel(output_path, index=False)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    input_base = r"D:\MIT\Develop_Workflow\ELO2\ai-bubble-research\Data_preparation\datasets\cleaned_data"
    output_base = r"D:\MIT\Develop_Workflow\ELO2\ai-bubble-research\Data_preparation\datasets\normalized_data"
    
    os.makedirs(output_base, exist_ok=True)
    
    exchange_rates = get_exchange_rates()
    monetary_columns = get_monetary_columns()
    
    for currency in os.listdir(input_base):
        currency_path = os.path.join(input_base, currency)
        if os.path.isdir(currency_path) and currency in exchange_rates:
            exchange_rate = exchange_rates[currency]
            
            for filename in os.listdir(currency_path):
                if filename.endswith('.xlsx'):
                    file_path = os.path.join(currency_path, filename)
                    output_path = os.path.join(output_base, filename)
                    convert_file(file_path, currency, exchange_rate, monetary_columns, output_path)

if __name__ == "__main__":
    main()

