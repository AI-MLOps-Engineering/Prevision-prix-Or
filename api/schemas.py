from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ForecastRequest(BaseModel):
    history: List[float] = Field(..., description="Série temporelle historique")
    horizon: int = Field(..., gt=0, le=60, description="Horizon de prévision (jours)")


class ModelPrediction(BaseModel):
    name: str
    predictions: List[float]
    metrics: Dict[str, float] | None = None


class ForecastResponse(BaseModel):
    models: List[ModelPrediction]
    metadata: Dict[str, Any]
