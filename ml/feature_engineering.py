"""
Step 3: Feature engineering.

Takes the cleaned data and calculates NEW columns that make anomalies
easier to detect — a raw number like 14.2 means nothing on its own,
these features give it context (is this normal for THIS station,
at THIS time of year, compared to ITS OWN recent readings?).

Column names here match clean.py's actual output exactly:
station_code, monitoring_date, ground_water_level — NOT
timestamp/water_level (that was a bug in the earlier draft).
"""

import pandas as pd
import os

CLEAN_FILE_PATH = os.path.join(
   "backend", "data", "processed", "karnataka_telemetry_2026_part1_clean.csv"
)
FEATURES_FILE_PATH = os.path.join(
    "backend","data", "processed", "karnataka_telemetry_2026_part1_features.csv"
)


def add_features(df: pd.DataFrame) -> pd.DataFrame:

    # --------------------------------------------------
    # 1. TIME FEATURES
    # --------------------------------------------------
    df["monitoring_date"] = pd.to_datetime(df["monitoring_date"])

    df["hour"] = df["monitoring_date"].dt.hour
    df["day"] = df["monitoring_date"].dt.day
    df["month"] = df["monitoring_date"].dt.month

    def get_season(month):
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Summer"
        elif month in [6, 7, 8, 9]:
            return "Monsoon"
        else:
            return "Post-Monsoon"

    df["season"] = df["month"].apply(get_season)

    # --------------------------------------------------
    # Make sure readings are in chronological order
    # (needed before any shift()/rolling() below)
    # --------------------------------------------------
    df = df.sort_values(["station_code", "monitoring_date"]).reset_index(drop=True)

    # --------------------------------------------------
    # 2. PREVIOUS READING
    # --------------------------------------------------
    df["previous_water_level"] = (
        df.groupby("station_code")["ground_water_level"].shift(1)
    )

    # --------------------------------------------------
    # 3. TIME SINCE PREVIOUS READING
    # --------------------------------------------------
    df["previous_timestamp"] = (
        df.groupby("station_code")["monitoring_date"].shift(1)
    )

    df["time_since_previous_hours"] = (
        (df["monitoring_date"] - df["previous_timestamp"]).dt.total_seconds() / 3600
    )

    # --------------------------------------------------
    # 4. WATER LEVEL CHANGE
    # --------------------------------------------------
    df["water_level_change"] = (
        df["ground_water_level"] - df["previous_water_level"]
    )

    # --------------------------------------------------
    # 5. ROLLING MEAN
    # shift(1) first so today's own reading is never
    # used to calculate today's own "normal" baseline.
    # --------------------------------------------------
    df["rolling_mean"] = (
        df.groupby("station_code")["ground_water_level"]
        .transform(lambda x: x.shift(1).rolling(window=3, min_periods=2).mean())
    )

    # --------------------------------------------------
    # 6. ROLLING STANDARD DEVIATION
    # --------------------------------------------------
    df["rolling_std"] = (
        df.groupby("station_code")["ground_water_level"]
        .transform(lambda x: x.shift(1).rolling(window=3, min_periods=2).std())
    )

    # --------------------------------------------------
    # 7. DEVIATION FROM ROLLING MEAN
    # --------------------------------------------------
    df["deviation_from_mean"] = (
        df["ground_water_level"] - df["rolling_mean"]
    )

    # --------------------------------------------------
    # 8. ABSOLUTE DEVIATION
    # --------------------------------------------------
    df["absolute_deviation"] = df["deviation_from_mean"].abs()

    # --------------------------------------------------
    # 9. CHECK ROLLING STANDARD DEVIATION
    # --------------------------------------------------

    print("\n===== ROLLING STD CHECK =====")

    print(df["rolling_std"].describe())

    print(
        "Zero std:",
        (df["rolling_std"] == 0).sum()
    )

    print(
        "Near-zero std:",
        (df["rolling_std"].abs() < 0.001).sum()
    )

    # --------------------------------------------------
    # 10. Z-SCORE
    # --------------------------------------------------

    # Ignore unreliable z-score when recent variation is too small
    df["z_score"] = (
        df["deviation_from_mean"] /
        df["rolling_std"].where(df["rolling_std"] >= 0.1)
)
    return df
if __name__ == "__main__":
    print(f"Loading cleaned data from {CLEAN_FILE_PATH} ...")
    df = pd.read_csv(CLEAN_FILE_PATH, low_memory=False)
    print(f"Rows loaded: {len(df)}")

    df = add_features(df)

    print("\n===== EXTREME Z-SCORE CHECK =====")
    print(
        df.loc[
            df["z_score"].abs().nlargest(10).index,
            [
                "station_code",
                "monitoring_date",
                "ground_water_level",
                "rolling_mean",
                "rolling_std",
                "deviation_from_mean",
                "z_score"
            ]
        ]
    )

    print("\nNew columns added:")
    for col in ["hour", "day", "month", "season", "previous_water_level",
                "time_since_previous_hours", "water_level_change",
                "rolling_mean", "rolling_std", "deviation_from_mean",
                "absolute_deviation", "z_score"]:
        print(f"- {col}")

    print("\nSample of z_score column (non-missing values):")
    print(df["z_score"].dropna().describe())

    os.makedirs(os.path.dirname(FEATURES_FILE_PATH), exist_ok=True)
    df.to_csv(FEATURES_FILE_PATH, index=False)
    print(f"\nSaved to: {FEATURES_FILE_PATH}")