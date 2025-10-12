import os
import pandas as pd

# === CONFIGURATION ===
folder_path = r"D:\MIT\Develop_Workflow\ELO2\ai-bubble-research\Data_collection\aiq_holdings"  # ← change this to your actual folder path
output_file = os.path.join(folder_path, "merged_tickers.csv")

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

# Save the merged result
all_data.to_csv(output_file, index=False)
print(f"\n✅ Merged file saved as: {output_file}")
print(f"Total unique tickers: {len(all_data)}")
