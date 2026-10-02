from fastapi import APIRouter

router = APIRouter()


@router.get("/overview")
def get_overview():
    return {
        "totalStations": 1408,
        "safeStations": 1200,
        "watchStations": 150,
        "warningStations": 40,
        "criticalStations": 18
    }