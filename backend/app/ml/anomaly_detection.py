"""
Step 4: Anomaly Detection.

Loads the trained Isolation Forest model and uses it
to identify unusual groundwater readings.
"""

import os
import joblib
import pandas as pd


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

FEATURES_FILE_PATH = os.path.join(
    "backend",
    "data",
    "processed",
    "karnataka_telemetry_2026_part1_features.csv"
)

MODEL_FILE_PATH = os.path.join(
    "backend",
    "data",
    "models",
    "groundwater_isolation_forest.pkl"
)

ANOMALIES_FILE_PATH = os.path.join(
    "backend",
    "data",
    "processed",
    "karnataka_telemetry_2026_part1_anomalies.csv"
)


# --------------------------------------------------
# FEATURES USED BY THE MODEL
# --------------------------------------------------

FEATURE_COLUMNS = [
    "ground_water_level",
    "previous_water_level",
    "water_level_change",
    "rolling_mean",
    "rolling_std",
    "deviation_from_mean"
]


# --------------------------------------------------
# DETECT ANOMALIES
# --------------------------------------------------

def detect_anomalies(df: pd.DataFrame):

    # Keep rows where all required features exist
    model_data = df.dropna(
        subset=FEATURE_COLUMNS
    ).copy()

    print(
        "Rows available for anomaly detection:",
        len(model_data)
    )

    # --------------------------------------------------
    # LOAD TRAINED MODEL
    # --------------------------------------------------

    print("\n===== LOADING ISOLATION FOREST =====")

    model = joblib.load(
        MODEL_FILE_PATH
    )

    print("Model loaded successfully.")

    # --------------------------------------------------
    # PREDICT
    # --------------------------------------------------

    # Isolation Forest:
    #  1  = normal
    # -1  = anomaly

    model_data["anomaly_flag"] = model.predict(
        model_data[FEATURE_COLUMNS]
    )

    # Convert:
    # 0 = normal
    # 1 = anomaly

    model_data["is_anomaly"] = (
        model_data["anomaly_flag"] == -1
    ).astype(int)

    # --------------------------------------------------
    # ANOMALY SCORE
    # --------------------------------------------------

    model_data["anomaly_score"] = (
        model.decision_function(
            model_data[FEATURE_COLUMNS]
        )
    )

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    total = len(model_data)

    anomalies = model_data[
        "is_anomaly"
    ].sum()

    normal = total - anomalies

    print("\n===== ANOMALY RESULTS =====")

    print("Total readings:", total)
    print("Normal readings:", normal)
    print("Anomalies:", anomalies)

    print(
        "Anomaly percentage:",
        round((anomalies / total) * 100, 2),
        "%"
    )

    return model_data


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print(
        f"Loading feature data from "
        f"{FEATURES_FILE_PATH} ..."
    )

    df = pd.read_csv(
        FEATURES_FILE_PATH,
        low_memory=False
    )

    print("Rows loaded:", len(df))

    df = detect_anomalies(df)

    # --------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------

    os.makedirs(
        os.path.dirname(ANOMALIES_FILE_PATH),
        exist_ok=True
    )

    df.to_csv(
        ANOMALIES_FILE_PATH,
        index=False
    )

    print(
        f"\nAnomaly results saved to: "
        f"{ANOMALIES_FILE_PATH}"
    )