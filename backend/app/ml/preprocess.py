# ============================================================
# GROUNDWATER DATA PREPROCESSING
# ============================================================

import pandas as pd
import os


# ============================================================
# FILE PATH
# ============================================================

CLEAN_FILE_PATH = os.path.join(
    "backend",
    "data",
    "processed",
    "karnataka_telemetry_2026_part1_clean.csv"
)


# ============================================================
# 1. STATION-WISE COVERAGE
# ============================================================

def check_station_coverage(clean_file_path: str) -> pd.DataFrame:

    # Load cleaned data
    df = pd.read_csv(
        clean_file_path,
        low_memory=False
    )

    # Convert date column to datetime
    df["monitoring_date"] = pd.to_datetime(
        df["monitoring_date"],
        errors="coerce"
    )

    # Calculate coverage for each station
    station_coverage = (
        df.groupby("station_code")
        .agg(
            first_reading=("monitoring_date", "min"),
            last_reading=("monitoring_date", "max"),
            reading_count=("monitoring_date", "count")
        )
        .reset_index()
    )

    return station_coverage


# ============================================================
# 2. TIME-SERIES FREQUENCY
# ============================================================

def check_time_frequency(clean_file_path: str) -> pd.DataFrame:

    # Load cleaned data
    df = pd.read_csv(
        clean_file_path,
        low_memory=False
    )

    # Convert date column
    df["monitoring_date"] = pd.to_datetime(
        df["monitoring_date"],
        errors="coerce"
    )

    # Sort readings by station and date
    df = df.sort_values(
        ["station_code", "monitoring_date"]
    )

    # Calculate difference between consecutive readings
    df["time_difference"] = (
        df.groupby("station_code")["monitoring_date"]
        .diff()
    )

    # Ignore very small timestamp differences.
    # We are interested in actual monitoring intervals.
    valid_intervals = df[
        df["time_difference"] >= pd.Timedelta(hours=1)
    ].copy()

    # Find most common meaningful interval for each station
    frequency = (
        valid_intervals
        .groupby("station_code")["time_difference"]
        .agg(
            lambda x:
            x.mode().iloc[0]
            if not x.mode().empty
            else pd.NaT
        )
        .reset_index()
    )

    # Rename column
    frequency = frequency.rename(
        columns={
            "time_difference": "typical_frequency"
        }
    )

    return frequency


# ============================================================
# 3. TIME-SERIES GAP ANALYSIS
# ============================================================

def analyze_gaps(clean_file_path: str) -> pd.DataFrame:

    # Load cleaned data
    df = pd.read_csv(
        clean_file_path,
        low_memory=False
    )

    # Convert dates
    df["monitoring_date"] = pd.to_datetime(
        df["monitoring_date"],
        errors="coerce"
    )

    # Sort data
    df = df.sort_values(
        ["station_code", "monitoring_date"]
    )

    # Calculate difference between consecutive readings
    df["time_difference"] = (
        df.groupby("station_code")["monitoring_date"]
        .diff()
    )

    # Keep meaningful intervals only
    gap_report = df[
        df["time_difference"] >= pd.Timedelta(hours=1)
    ][
        [
            "station_code",
            "monitoring_date",
            "time_difference"
        ]
    ].copy()

    return gap_report


# ============================================================
# 4. GAP HANDLING DECISION
# ============================================================

def classify_gaps(clean_file_path: str) -> pd.DataFrame:

    # Load cleaned data
    df = pd.read_csv(
        clean_file_path,
        low_memory=False
    )

    # Convert dates
    df["monitoring_date"] = pd.to_datetime(
        df["monitoring_date"],
        errors="coerce"
    )

    # Sort data
    df = df.sort_values(
        ["station_code", "monitoring_date"]
    )

    # Calculate difference between consecutive readings
    df["time_difference"] = (
        df.groupby("station_code")["monitoring_date"]
        .diff()
    )

    # --------------------------------------------------------
    # Calculate meaningful intervals
    # --------------------------------------------------------

    meaningful_intervals = df[
        df["time_difference"] >= pd.Timedelta(hours=1)
    ].copy()

    # --------------------------------------------------------
    # Calculate typical frequency for each station
    # --------------------------------------------------------

    typical_frequency = (
        meaningful_intervals
        .groupby("station_code")["time_difference"]
        .agg(
            lambda x:
            x.mode().iloc[0]
            if not x.mode().empty
            else pd.NaT
        )
        .rename("typical_frequency")
    )

    # --------------------------------------------------------
    # Add typical frequency to original dataframe
    # --------------------------------------------------------

    df = df.merge(
        typical_frequency,
        on="station_code",
        how="left"
    )

    # --------------------------------------------------------
    # Identify gaps
    # --------------------------------------------------------

    df["is_gap"] = (
        df["time_difference"] > df["typical_frequency"]
    )

    # --------------------------------------------------------
    # Gap handling decision
    # --------------------------------------------------------

    df["gap_decision"] = "normal_interval"

    df.loc[
        df["is_gap"] == True,
        "gap_decision"
    ] = "needs_review"

    # --------------------------------------------------------
    # Create gap report
    # --------------------------------------------------------

    gap_report = df[
        df["is_gap"] == True
    ][
        [
            "station_code",
            "monitoring_date",
            "time_difference",
            "typical_frequency",
            "is_gap",
            "gap_decision"
        ]
    ].copy()

    return gap_report


# ============================================================
# 5. FINAL VALIDATION
# ============================================================

def final_validation(clean_file_path: str):

    # Load cleaned data
    df = pd.read_csv(
        clean_file_path,
        low_memory=False
    )

    # Convert date
    df["monitoring_date"] = pd.to_datetime(
        df["monitoring_date"],
        errors="coerce"
    )

    # Convert groundwater level to numeric
    groundwater_numeric = pd.to_numeric(
        df["ground_water_level"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Validation 1: Missing station codes
    # --------------------------------------------------------

    missing_stations = df[
        "station_code"
    ].isna().sum()

    # --------------------------------------------------------
    # Validation 2: Invalid dates
    # --------------------------------------------------------

    invalid_dates = df[
        "monitoring_date"
    ].isna().sum()

    # --------------------------------------------------------
    # Validation 3: Invalid groundwater values
    # --------------------------------------------------------

    invalid_groundwater = groundwater_numeric.isna().sum()

    # --------------------------------------------------------
    # Validation 4: Duplicate station + date
    # --------------------------------------------------------

    duplicate_station_dates = df.duplicated(
        [
            "station_code",
            "monitoring_date"
        ]
    ).sum()

    # --------------------------------------------------------
    # Validation 5: Check sorting
    # --------------------------------------------------------

    sorted_df = df.sort_values(
        [
            "station_code",
            "monitoring_date"
        ]
    )

    is_sorted = df[
        [
            "station_code",
            "monitoring_date"
        ]
    ].equals(
        sorted_df[
            [
                "station_code",
                "monitoring_date"
            ]
        ]
    )

    # --------------------------------------------------------
    # Print validation results
    # --------------------------------------------------------

    print("\n===== 5. FINAL VALIDATION =====")

    print(
        f"Missing station codes: "
        f"{missing_stations}"
    )

    print(
        f"Invalid dates: "
        f"{invalid_dates}"
    )

    print(
        f"Invalid groundwater values: "
        f"{invalid_groundwater}"
    )

    print(
        f"Duplicate station-date rows: "
        f"{duplicate_station_dates}"
    )

    print(
        f"Data sorted by station/date: "
        f"{is_sorted}"
    )

    # --------------------------------------------------------
    # Final decision
    # --------------------------------------------------------

    if (
        missing_stations == 0
        and invalid_dates == 0
        and invalid_groundwater == 0
        and duplicate_station_dates == 0
        and is_sorted
    ):

        print(
            "\n✓ FINAL VALIDATION PASSED"
        )

        print(
            "✓ DATA READY FOR FEATURE ENGINEERING"
        )

    else:

        print(
            "\n⚠ FINAL VALIDATION NEEDS ATTENTION"
        )


# ============================================================
# RUN ALL PREPROCESSING STEPS
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # 1. Station-wise coverage
    # --------------------------------------------------------

    coverage = check_station_coverage(
        CLEAN_FILE_PATH
    )

    print(
        "\n===== 1. STATION-WISE COVERAGE ====="
    )

    print(
        coverage.head(10)
    )

    print(
        f"Total stations: {len(coverage)}"
    )

    # --------------------------------------------------------
    # 2. Time-series frequency
    # --------------------------------------------------------

    frequency = check_time_frequency(
        CLEAN_FILE_PATH
    )

    print(
        "\n===== 2. TIME-SERIES FREQUENCY ====="
    )

    print(
        frequency.head(10)
    )

    # --------------------------------------------------------
    # 3. Gap analysis
    # --------------------------------------------------------

    intervals = analyze_gaps(
        CLEAN_FILE_PATH
    )

    print(
        "\n===== 3. TIME-SERIES GAP ANALYSIS ====="
    )

    print(
        intervals.head(10)
    )

    print(
        f"Total intervals analyzed: "
        f"{len(intervals)}"
    )

    # --------------------------------------------------------
    # 4. Gap classification
    # --------------------------------------------------------

    gaps = classify_gaps(
        CLEAN_FILE_PATH
    )

    print(
        "\n===== 4. GAP CLASSIFICATION ====="
    )

    print(
        gaps.head(10)
    )

    print(
        f"Total detected gaps: "
        f"{len(gaps)}"
    )

    # --------------------------------------------------------
    # 5. Final validation
    # --------------------------------------------------------

    final_validation(
        CLEAN_FILE_PATH
    )