from fastapi import APIRouter, HTTPException
from api.schemas import ForecastRequest, ForecastResponse, ModelPrediction

router = APIRouter()


@router.post("/", response_model=ForecastResponse)
def forecast(req: ForecastRequest):
    # Import paresseux : évite de charger torch/chronos au démarrage (tests CI, healthcheck).
    from ml.inference import predict_all

    try:
        result = predict_all(req.history, req.horizon)

        models = [
            ModelPrediction(
                name=m["name"],
                predictions=m["predictions"],
                metrics=m.get("metrics")
            )
            for m in result["models"]
        ]

        return ForecastResponse(
            models=models,
            metadata=result["metadata"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
