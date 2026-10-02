import os
import pandas as pd


FORECAST_FILE = os.path.join(
    "backend",
    "data",
    "processed",
    "karnataka_telemetry_2026_part1_forecast.csv"
)

FINAL_FILE = os.path.join(
    "backend",
    "data",
    "processed",
    "karnataka_telemetry_2026_part1_ml_output.csv"
)


def create_ml_output(df):

    columns = [
        "station_code",
        "state",
        "district",
        "block_name",
        "latitude",
        "longitude",
        "monitoring_date",
        "ground_water_level",
        "water_level_change",
        "anomaly_flag",
        "is_anomaly",
        "anomaly_score",
        "risk_level",
        "forecast_level"
    ]

    return df[columns].copy()


if __name__ == "__main__":

    print("Loading forecast data...")

    df = pd.read_csv(
        FORECAST_FILE,
        low_memory=False
    )

    print("Rows loaded:", len(df))

    final_df = create_ml_output(df)

    os.makedirs(
        os.path.dirname(FINAL_FILE),
        exist_ok=True
    )

    final_df.to_csv(
        FINAL_FILE,
        index=False
    )

    print("\n===== FINAL ML OUTPUT =====")
    print("Rows:", len(final_df))
    print("Columns:", len(final_df.columns))

    print("\nRisk distribution:")
    print(final_df["risk_level"].value_counts())

    print(
        f"\nFinal ML output saved to:\n{FINAL_FILE}"
    )