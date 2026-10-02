from fastapi import APIRouter
from app.services.ml_service import get_stations_data

router = APIRouter()


@router.get("/stations")
def get_stations():
    df = get_stations_data()

    df = df.astype(object).where(
        df.notna(),
        None
    )

    return df.to_dict(orient="records")