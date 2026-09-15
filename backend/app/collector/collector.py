
#Step1 explore data · PY
"""
Step 1: Download one groundwater CSV and look at what's actually inside it.
 
This is just exploration — we're not cleaning or storing anything yet.
Goal: see the real column names, real data types, and a few real rows,
so we can design the cleaning pipeline (Step 2) based on facts, not guesses.
"""
 #IMPORT LIB
import requests
import pandas as pd
import os
 
# ---  DTA URL ---
 
# The Karnataka groundwater telemetry CSV we found (2021-2022 range).
# This is a DIRECT file download link, no login or API key needed.
DATA_URL = (
    "https://nwdp.nwic.gov.in/dataset/e67cc282-0399-49db-84af-c1416838cd5b/"
    "resource/a2540dd2-6248-4a3e-95b5-d9f76f2a8c2c/download/"
    "karnataka_tel_gw_wl_six_hourly_data_2026_1.csv"
)
 
# Where to save the raw, untouched file. We NEVER edit this file later —
# it's our permanent original copy in case we need to re-check anything.
RAW_DATA_FOLDER = "data/raw"
RAW_FILE_PATH = os.path.join(RAW_DATA_FOLDER, "karnataka_telemetry_2026_part1.csv")
 # download_file=>1.take input2.save to path
 
 
 #DOWNLAOD FUNCTION
def download_file(url: str, save_path: str) -> None:
    """Download a file from a URL and save it to disk, showing progress."""
    #create folder on computer
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
 
    print(f"Downloading from:\n{url}\n")
 
    # stream=True means we download in chunks instead of all at once —
    # important because this file might be tens of MB.
    response = requests.get(url, stream=True, timeout=60)
 
    # This will raise an error immediately if something went wrong
    # (like a 404 Not Found or 500 Server Error), instead of silently
    # saving a broken/empty file.
    response.raise_for_status()
 
    total_bytes_downloaded = 0
    #with =>ensure close after use
    #wb=>wirte bytes
    with open(save_path, "wb") as f:
        #response.iter_content(chunk_size=1024*1024) — since we said stream=True earlier, this reads the download 1 MB at a time instead of all at once, and the for loop processes each MB-sized piece as it arrives
        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB at a time
            f.write(chunk)
            total_bytes_downloaded += len(chunk)
            print(f"\rDownloaded: {total_bytes_downloaded / (1024*1024):.1f} MB", end="")
 
    print(f"\nSaved to: {save_path}\n")
 
 
 
 #INSPECT DATA
def inspect_data(csv_path: str) -> None:
    """Load the CSV and print out useful facts about its structure."""
    df = pd.read_csv(csv_path)
 
 
 #O/P OF DATA
    print("=" * 60)
    print("BASIC INFO")
    print("=" * 60)
    print(f"Number of rows: {len(df)}")#df=>how many rows present
    print(f"Number of columns: {len(df.columns)}")
 
 
    print("\n" + "=" * 60)
    print("COLUMN NAMES")
    print("=" * 60)
    for col in df.columns:
        print(f"- {col}")
 
    print("\n" + "=" * 60)
    print("DATA TYPES (what pandas thinks each column is)")
    print("=" * 60)
    print(df.dtypes)
 
    print("\n" + "=" * 60)
    print("FIRST 5 ROWS (a real sample of the data)")
    print("=" * 60)
    print(df.head())#shows the first 5 actual rows, so we can see real values
 
    print("\n" + "=" * 60)
    print("MISSING VALUES PER COLUMN")
    print("=" * 60)
    print(df.isnull().sum())#or each column, counts how many rows have a missing/blank value — tells us how messy the data is
 
    print("\n" + "=" * 60)
    print("HOW MANY UNIQUE STATIONS ARE THERE?")
    print("=" * 60)
    # We don't know the exact station-name column yet — this loop checks
    # any column with 'station' in its name (case-insensitive) and shows
    # how many unique values it has.
    station_like_cols = [c for c in df.columns if "station" in c.lower()]
    if station_like_cols:
        for col in station_like_cols:
            print(f"{col}: {df[col].nunique()} unique values")
    else:
        print("No column with 'station' in its name was found — "
              "check the COLUMN NAMES list above to find the right one.")
 
 
if __name__ == "__main__":
    if not os.path.exists(RAW_FILE_PATH):
        download_file(DATA_URL, RAW_FILE_PATH)
    else:
        print(f"File already downloaded at {RAW_FILE_PATH}, skipping download.\n")
 
    inspect_data(RAW_FILE_PATH)
 
