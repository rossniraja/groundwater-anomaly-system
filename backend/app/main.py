from fastapi import FastAPI

app = FastAPI(
    title="Groundwater Anomaly Detection System",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Groundwater Anomaly Detection API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }