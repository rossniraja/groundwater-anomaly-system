"""
Step 5: Groundwater Risk Classification.

Uses anomaly detection results and groundwater
behavior to assign a risk level.
"""

import os
import pandas as pd


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

ANOMALIES_FILE_PATH = os.path.join(
    "backend",
    "data",
    "processed",
    "karnataka_telemetry_2026_part1_anomalies.csv"
)

RISK_FILE_PATH = os.path.join(
    "backend",
    "data",
    "processed",
    "karnataka_telemetry_2026_part1_risk.csv"
)


# --------------------------------------------------
# RISK CLASSIFICATION
# --------------------------------------------------

def classify_risk(row):

    # Normal reading
    if row["is_anomaly"] == 0:
        return "SAFE"

    # Anomalous reading
    z_score = abs(row["z_score"])
    anomaly_score = row["anomaly_score"]

    # Strong statistical deviation
    if z_score >= 3:
        return "CRITICAL"

    # Strong anomaly
    elif anomaly_score <= -0.10:
        return "WARNING"

    # Moderate anomaly
    else:
        return "WATCH"


# --------------------------------------------------
# APPLY RISK CLASSIFICATION
# --------------------------------------------------

def assign_risk(df):

    df = df.copy()

    df["risk_level"] = df.apply(
        classify_risk,
        axis=1
    )

    return df


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print(
        f"Loading anomaly data from "
        f"{ANOMALIES_FILE_PATH} ..."
    )

    df = pd.read_csv(
        ANOMALIES_FILE_PATH,
        low_memory=False
    )

    print("Rows loaded:", len(df))

    # Assign risk
    df = assign_risk(df)

    # Show distribution
    print("\n===== RISK DISTRIBUTION =====")

    print(
        df["risk_level"].value_counts()
    )

    # Save
    os.makedirs(
        os.path.dirname(RISK_FILE_PATH),
        exist_ok=True
    )

    df.to_csv(
        RISK_FILE_PATH,
        index=False
    )

    print(
        f"\nRisk results saved to: "
        f"{RISK_FILE_PATH}"
    )