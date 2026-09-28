"""
Isolation Forest model.

Creates and saves the trained groundwater anomaly detection model.
"""

import os
import joblib
import pandas as pd

from sklearn.ensemble import IsolationForest


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
# CREATE MODEL
# --------------------------------------------------

def create_model():

    model = IsolationForest(
        n_estimators=200,
        contamination=0.01,
        random_state=42,
        n_jobs=-1
    )

    return model


# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------

def train_model(df: pd.DataFrame):

    model_data = df.dropna(
        subset=FEATURE_COLUMNS
    ).copy()

    print("Rows available for training:", len(model_data))

    model = create_model()

    model.fit(
        model_data[FEATURE_COLUMNS]
    )

    return model


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

def save_model(model):

    os.makedirs(
        os.path.dirname(MODEL_FILE_PATH),
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_FILE_PATH
    )

    print(
        f"Model saved to: {MODEL_FILE_PATH}"
    )


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

    model = train_model(df)

    save_model(model)

    print("\n===== MODEL TRAINING COMPLETE =====")