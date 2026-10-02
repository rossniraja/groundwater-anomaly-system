from fastapi import APIRouter
from app.services.ml_service import get_stations_data

router = APIRouter()


@router.get("/forecast")
def get_forecast():

    df = get_stations_data()

    forecast = df[
        df["forecast_level"].notna()
    ].copy()

    forecast = forecast.astype(object).where(
        forecast.notna(),
        None
    )

    return forecast[
        [
            "station_code",
            "district",
            "block_name",
            "monitoring_date",
            "ground_water_level",
            "forecast_level",
            "risk_level"
        ]
    ].to_dict(orient="records")
    