from fastapi import APIRouter
from app.services.ml_service import get_stations_data

router = APIRouter()


@router.get("/alerts")
def get_alerts():
    df = get_stations_data()

    alerts = df[
        df["risk_level"].isin(["WARNING", "CRITICAL"])
    ].copy()

    alerts = alerts.astype(object).where(
        alerts.notna(),
        None
    )

    return alerts[
        [
            "station_code",
            "district",
            "block_name",
            "ground_water_level",
            "anomaly_score",
            "risk_level",
            "forecast_level"
        ]
    ].to_dict(orient="records")