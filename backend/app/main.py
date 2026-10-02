from fastapi import FastAPI
from app.routes import overview, stations, anomalies, forecast, alerts
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="NIVORA - Groundwater Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
       "*"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(overview.router)
app.include_router(stations.router)
app.include_router(anomalies.router)
app.include_router(forecast.router)
app.include_router(alerts.router)


@app.get("/")
def root():
    return {
        "message": "NIVORA Groundwater Intelligence API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }