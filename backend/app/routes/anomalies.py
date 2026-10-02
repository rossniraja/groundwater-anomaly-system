from fastapi import APIRouter
from app.services.ml_service import get_stations_data

router = APIRouter()


@router.get("/anomalies")
def get_anomalies():
    df = get_stations_data()

    anomalies = df[
        df["risk_level"].isin(["WATCH", "WARNING", "CRITICAL"])
    ].copy()

    anomalies = anomalies.astype(object).where(
        anomalies.notna(),
        None
    )

    return anomalies[
        [
            "station_code",
            "district",
            "block_name",
            "latitude",
            "longitude",
            "ground_water_level",
            "anomaly_score",
            "risk_level",
            "forecast_level"
        ]
    ].to_dict(orient="records")