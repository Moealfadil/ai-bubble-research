import os
import pandas as pd

# === CONFIGURATION ===
folder_path = r"D:\MIT\Develop_Workflow\ELO2\ai-bubble-research\Data_collection\Tickers\aiq_holdings"  # ← change this to your actual folder path
output_file = os.path.join(r"D:\MIT\Develop_Workflow\ELO2\ai-bubble-research\Data_collection\Tickers", "merged_tickers.csv")
left_out_file = r"D:\MIT\Develop_Workflow\ELO2\ai-bubble-research\Data_collection\Tickers\stock_analysis\companies_left_out.csv"

# Create an empty DataFrame to store combined results
all_data = pd.DataFrame(columns=["Ticker", "Name"])

# Loop through each CSV file in the folder
for file in os.listdir(folder_path):
    if file.endswith(".csv"):
        file_path = os.path.join(folder_path, file)
        print(f"Processing: {file}")

        # Read the CSV file while skipping the first two rows
        try:
            df = pd.read_csv(file_path, skiprows=2, usecols=["Ticker", "Name"])
        except Exception as e:
            print(f"Skipping {file} due to error: {e}")
            continue

        # Drop null values
        df = df.dropna(subset=["Ticker", "Name"])

        # Append to the main DataFrame
        all_data = pd.concat([all_data, df], ignore_index=True)

# Drop duplicates based on Ticker
all_data = all_data.drop_duplicates(subset=["Ticker"])

print(f"Tickers from ETF holdings: {len(all_data)}")

# === ADD LEFT OUT COMPANIES ===
print(f"\nAdding companies from: {left_out_file}")

try:
    # Read the companies_left_out.csv file
    left_out_df = pd.read_csv(left_out_file)
    
    # Rename the column to match our format if needed
    if "Company Name" in left_out_df.columns:
        left_out_df = left_out_df.rename(columns={"Company Name": "Name"})
    
    print(f"Found {len(left_out_df)} additional companies in left_out file")
    
    # Append the left out companies to the main DataFrame
    all_data = pd.concat([all_data, left_out_df], ignore_index=True)
    
    # Drop duplicates again (in case some companies are in both lists)
    all_data = all_data.drop_duplicates(subset=["Ticker"])
    
    print(f"Added {len(left_out_df)} companies from left_out file")
    
except Exception as e:
    print(f"Error reading left_out file: {e}")

# Save the merged result
all_data.to_csv(output_file, index=False)
print(f"\n✅ Merged file saved as: {output_file}")
print(f"Total unique tickers: {len(all_data)}")
print("Final breakdown:")
print(f"  - ETF holdings companies: {len(all_data) - len(left_out_df)}")
print(f"  - Additional left-out companies: {len(left_out_df)}")
print(f"  - Total unique companies: {len(all_data)}")
