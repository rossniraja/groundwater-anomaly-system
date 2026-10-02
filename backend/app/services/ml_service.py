import os
import pandas as pd


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

STATIONS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "stations_latest.csv"
)


def get_stations_data():
    if not os.path.exists(STATIONS_FILE):
        raise FileNotFoundError(
            f"Stations file not found: {STATIONS_FILE}"
        )

    return pd.read_csv(
        STATIONS_FILE,
        low_memory=False
    )