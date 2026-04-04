from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import forecast, health

app = FastAPI(
    title="Prévision cours de l'or",
    version="1.0.0",
    description="API de prévision du prix de l'or avec Chronos & TimeSeriesTransformer"
)

# CORS (optionnel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(forecast.router, prefix="/forecast", tags=["Forecast"])


@app.get("/")
def root():
    return {"message": "Gold Forecasting API is running"}
    
