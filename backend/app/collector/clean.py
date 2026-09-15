"""
Step 2: Clean the raw groundwater data.

This is where we actually FIX the data (unlike diagnostics, which only
looked and reported). Every step here is based on a real decision we
made after looking at the real data:

- Different files use different column names (Block Name vs block_name)
  -> normalize all column names to one standard set.
- 999.999 (and similar suspiciously round, out-of-range numbers) are
  sensor error codes, not real readings -> treat as missing.
- Missing Ground Water Level -> drop the row (nothing to detect anomalies on).
- Missing GP Name/Code, Basin, Sub Basin -> fill with 'Unknown'.
- Missing Latitude/Longitude -> try to fill from another row of the SAME
  station (a station's location shouldn't change); if still missing, drop.
- Same Station+Date appearing more than once with different values
  -> keep the LAST one seen (treated as the most likely correction).
- Exact duplicate rows -> remove.
- Monitoring Date -> convert to a real datetime, then sort each station's
  readings in time order.

The raw file is never modified. This script reads it and writes a
SEPARATE cleaned file.
"""

import pandas as pd
import os

RAW_FILE_PATH = os.path.join("data", "raw", "karnataka_telemetry_2026_part1.csv")
CLEAN_DATA_FOLDER = os.path.join("data", "processed")
CLEAN_FILE_PATH = os.path.join(CLEAN_DATA_FOLDER, "karnataka_telemetry_2026_part1_clean.csv")

# Any reading at or above this is treated as a sensor error code, not a
# real measurement. Based on real data: 75% of genuine readings are
# under 27, and 999.999 appears as a suspiciously round outlier far
# beyond any physically realistic value for this region.
SUSPICIOUS_VALUE_THRESHOLD = 500


# A single standard name for every column, no matter what the source
# file happens to call it. Add more entries here if a future file uses
# yet another spelling.
COLUMN_NAME_MAP = {
    "station code": "station_code",
    "state": "state",
    "state code": "state_code",
    "district": "district",
    "district code": "district_code",
    "block name": "block_name",
    "block_name": "block_name",
    "block code": "block_code",
    "gp name": "gp_name",
    "gp code": "gp_code",
    "basin": "basin",
    "basin code": "basin_code",
    "sub basin": "sub_basin",
    "sub basin code": "sub_basin_code",
    "latitude": "latitude",
    "longitude": "longitude",
    "monitoring date": "monitoring_date",
    "ground water level": "ground_water_level",
}


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Rename every column to one consistent standard name, regardless
    of the exact spelling/casing/spacing the source file used."""
    # Build a lookup using lowercased column names, so "Block Name",
    # "block_name", and "BLOCK NAME" all map to the same standard name.
    rename_lookup = {}
    for original_col in df.columns:
        key = original_col.lower().replace("_", " ").strip()
        if key in COLUMN_NAME_MAP:
            rename_lookup[original_col] = COLUMN_NAME_MAP[key]
        else:
            # If we hit a column name we've never seen before, keep it
            # as-is but warn loudly — better to notice than silently drop it.
            print(f"WARNING: unrecognized column '{original_col}', keeping as-is")

    return df.rename(columns=rename_lookup)

#remembers how many rows we started with — so at the very end we can show "here's how much we removed in total.
def clean_data(raw_path: str) -> pd.DataFrame:
    print(f"Loading raw data from {raw_path} ...")
    df = pd.read_csv(raw_path)
    starting_rows = len(df)
    print(f"Starting rows: {starting_rows}")

    # --- Step 1: Normalize column names ---
    df = normalize_column_names(df)

    # --- Step 2: Parse Monitoring Date into a real datetime ---
    # dayfirst=True correctly handles "01-01-2026" style dates (day-month-year).
    # It doesn't break ISO-style "2021-01-01" dates either, since those are
    # unambiguous (year always comes first) regardless of this setting.
    # errors="coerce" turns any date pandas can't understand into NaT
    # (pandas' "not a time" missing value) instead of crashing.
    df["monitoring_date"] = pd.to_datetime(
        df["monitoring_date"], dayfirst=True, errors="coerce"#errors="coerce" — if any single value is too broken to understand as a date, don't crash the whole program; just turn that one value into a special "missing date" marker (NaT) instead
    )
    unparseable_dates = df["monitoring_date"].isna().sum()
    if unparseable_dates > 0:
        print(f"Dropping {unparseable_dates} rows with unreadable dates")
        df = df.dropna(subset=["monitoring_date"])

    # --- Step 3: Treat suspicious placeholder values as missing ---
    # We do this BEFORE dropping missing values, so 999.999-style codes
    # get treated exactly the same as a truly blank cell.
    #df["ground_water_level"] >= SUSPICIOUS_VALUE_THRESHOLD — this creates a column of True/False values, one per row: True if that row's reading is 500 or higher (catches 999.999), False otherwise
    #.sum() — adds up all the Trues (Python treats True as 1, False as 0), giving us a count
    suspicious_count = (df["ground_water_level"] >= SUSPICIOUS_VALUE_THRESHOLD).sum()
    print(f"Flagging {suspicious_count} suspicious placeholder readings (>= {SUSPICIOUS_VALUE_THRESHOLD}) as missing")
    df.loc[df["ground_water_level"] >= SUSPICIOUS_VALUE_THRESHOLD, "ground_water_level"] = pd.NA

    # Also guard against negative readings — a water level can't be negative.
    negative_count = (df["ground_water_level"] < 0).sum()
    if negative_count > 0:
        print(f"Flagging {negative_count} negative readings as missing")
        df.loc[df["ground_water_level"] < 0, "ground_water_level"] = pd.NA

    # --- Step 4: Drop rows with missing Ground Water Level ---
    # There's nothing to run anomaly detection on if the core value is blank.
    missing_level_count = df["ground_water_level"].isna().sum()
    print(f"Dropping {missing_level_count} rows with missing/invalid Ground Water Level")
    df = df.dropna(subset=["ground_water_level"])

    # --- Step 5: Fill missing metadata columns with 'Unknown' ---
    metadata_columns_to_fill = [
        "gp_name", "gp_code", "basin", "basin_code", "sub_basin", "sub_basin_code"
    ]
    for col in metadata_columns_to_fill:
        df[col] = df[col].fillna("Unknown")
        
        

    # --- Step 6: Fill missing Latitude/Longitude from the same station ---
    # A station's physical location shouldn't change day to day, so if
    # one row for a station is missing coordinates but another row for
    # the SAME station has them, we can safely reuse that value.
    df["latitude"] = df.groupby("station_code")["latitude"].transform(
        lambda x: x.ffill().bfill()
    )
    df["longitude"] = df.groupby("station_code")["longitude"].transform(
        lambda x: x.ffill().bfill()
    )
    # If a station has NO valid coordinates anywhere in the file, we can't
    # place it on a map at all — drop those rows.
    still_missing_coords = df["latitude"].isna() | df["longitude"].isna()
    if still_missing_coords.sum() > 0:
        print(f"Dropping {still_missing_coords.sum()} rows from stations with no coordinates anywhere")
        df = df[~still_missing_coords]

    # --- Step 7: Clean up text columns (remove stray spaces) ---
    #.astype(str) — make sure the column is definitely treated as text (sometimes pandas gets confused about types)
    text_columns = ["state", "district", "block_name", "gp_name", "basin", "sub_basin"]
    for col in text_columns:
        df[col] = df[col].astype(str).str.strip()

    # --- Step 8: Remove exact duplicate rows ---
    before = len(df)
    df = df.drop_duplicates()
    print(f"Removed {before - len(df)} fully identical duplicate rows")

    # --- Step 9: Resolve Station+Date duplicates (keep the LAST one seen) ---
    before = len(df)
    df = df.sort_index()  # preserve original file order first
    df = df.drop_duplicates(subset=["station_code", "monitoring_date"], keep="last")
    print(f"Removed {before - len(df)} rows for duplicate Station+Date combinations (kept latest)")

    # --- Step 10: Sort into proper time-series order ---
    df = df.sort_values(["station_code", "monitoring_date"]).reset_index(drop=True)

    # --- Step 11: Flag (not fix) stations with inconsistent coordinates ---
    coords_per_station = df.groupby("station_code")[["latitude", "longitude"]].nunique()
    inconsistent = coords_per_station[
        (coords_per_station["latitude"] > 1) | (coords_per_station["longitude"] > 1)
    ]
    if len(inconsistent) > 0:
        print(f"WARNING: {len(inconsistent)} stations have inconsistent coordinates across readings — "
              f"kept as-is for now, worth reviewing manually later.")

    print(f"\nFinal cleaned rows: {len(df)} (started with {starting_rows})")
    return df

#Calls the whole cleaning process, creates the output folder if it doesn't exist yet, and saves the final cleaned table as a new CSV file — index=False just means "don't add pandas' internal row-number column into the saved file, we don't need it."
if __name__ == "__main__":
    cleaned_df = clean_data(RAW_FILE_PATH)

    os.makedirs(CLEAN_DATA_FOLDER, exist_ok=True)
    cleaned_df.to_csv(CLEAN_FILE_PATH, index=False)
    print(f"\nSaved cleaned data to: {CLEAN_FILE_PATH}")