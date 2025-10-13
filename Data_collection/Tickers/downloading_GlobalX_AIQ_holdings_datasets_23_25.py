import datetime
import os
import zipfile
import requests

# Create output folder
out_dir = "aiq_holdings"
os.makedirs(out_dir, exist_ok=True)

# Date range for 2023 to 2025
start_date = datetime.date(2023, 1, 1)
end_date = datetime.date(2025, 9, 30)

delta = datetime.timedelta(days=1)
current_date = start_date

# Base URL pattern
base_url = "https://assets.globalxetfs.com/holdings/aiq_full-holdings_{date}.csv"

downloaded = []

while current_date <= end_date:
    date_str = current_date.strftime("%Y%m%d")
    url = base_url.format(date=date_str)
    filename = os.path.join(out_dir, f"aiq_{date_str}.csv")

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and r.content.strip():  # valid file
            with open(filename, "wb") as f:
                f.write(r.content)
            print(f"Downloaded: {url}")
            downloaded.append(filename)
        else:
            print(f"Not found: {url}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

    current_date += delta

# Create ZIP archive
zip_filename = "aiq_holdings.zip"
with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
    for file in downloaded:
        zipf.write(file, os.path.basename(file))

print(f"\n🎉 Done! Saved {len(downloaded)} files into {zip_filename}")
