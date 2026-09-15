"""
Step 2a: Diagnostics — gather real facts about the data BEFORE writing
cleaning rules, so our decisions are based on what's actually there,
not guesses.

This does NOT change or save anything. It only reads and reports.
"""

import pandas as pd
import os

RAW_FILE_PATH = os.path.join("data", "raw", "karnataka_telemetry_2026_part1.csv")


def run_diagnostics(csv_path: str) -> None:
    df = pd.read_csv(csv_path)

    # ---- 1. Ground Water Level: real min/max/average ----
    print("=" * 60)
    print("GROUND WATER LEVEL — VALUE RANGE")
    print("=" * 60)
    print(df["Ground Water Level"].describe())
    # .describe() gives count, mean, std (spread), min, 25%/50%/75%
    # percentiles, and max — a fast way to spot impossible values
    # like negative numbers or something absurdly huge.

    # ---- 2. Exact duplicate rows ----
    print("\n" + "=" * 60)
    print("EXACT DUPLICATE ROWS")
    print("=" * 60)
    num_duplicates = df.duplicated().sum()
    print(f"Fully identical duplicate rows: {num_duplicates}")

    # Also check duplicates on just Station + Date, since two rows could
    # differ slightly (e.g. rounding) but still represent the same
    # station+timestamp reading being logged twice.
    station_date_duplicates = df.duplicated(
        subset=["Station Code", "Monitoring Date"]
    ).sum()
    print(f"Duplicate Station+Date combinations: {station_date_duplicates}")

    # ---- 3. Messy text: leading/trailing spaces or inconsistent casing ----
    print("\n" + "=" * 60)
    print("TEXT COLUMN SPACING CHECK")
    print("=" * 60)
    text_columns = ["District", "Block Name", "State"]
    for col in text_columns:
        # .str.strip() removes leading/trailing spaces; if that changes
        # any value, it means messy spacing exists in the raw data.
        has_extra_spaces = (df[col].astype(str) != df[col].astype(str).str.strip()).sum()
        print(f"{col}: {has_extra_spaces} rows have extra leading/trailing spaces")
        # Show a few unique example values so we can eyeball inconsistencies
        # like "Bengaluru Urban" vs "bengaluru urban" vs "Bengaluru  Urban"
        print(f"  Sample unique values: {df[col].dropna().unique()[:5]}")

    # ---- 4. Station coordinate consistency ----
    print("\n" + "=" * 60)
    print("STATION LOCATION CONSISTENCY")
    print("=" * 60)
    # For each station, count how many DIFFERENT lat/long pairs it has.
    # A station should always be in the same physical place — if a
    # Station Code has more than 1 unique coordinate pair, that's a
    # data quality problem worth flagging.
    coords_per_station = df.groupby("Station Code")[["Latitude", "Longitude"]].nunique()
    inconsistent_stations = coords_per_station[
        (coords_per_station["Latitude"] > 1) | (coords_per_station["Longitude"] > 1)
    ]
    print(f"Stations with inconsistent coordinates: {len(inconsistent_stations)}")

    # ---- 5. Time gaps per station (quick check) ----
    print("\n" + "=" * 60)
    print("TIME GAP CHECK (sample of 1 station)")
    print("=" * 60)
    df["Monitoring Date"] = pd.to_datetime(df["Monitoring Date"])
    sample_station = df["Station Code"].iloc[0]
    station_data = df[df["Station Code"] == sample_station].sort_values("Monitoring Date")
    gaps = station_data["Monitoring Date"].diff()
    print(f"Sample station: {sample_station}")
    print(f"Expected gap (six-hourly): ~6 hours between readings")
    print(f"Largest actual gap found: {gaps.max()}")
    print(f"Number of readings: {len(station_data)}")


if __name__ == "__main__":
    run_diagnostics(RAW_FILE_PATH)