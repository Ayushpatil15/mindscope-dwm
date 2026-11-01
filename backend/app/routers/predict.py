from fastapi import APIRouter, HTTPException
from backend.app.schemas.predict import PredictRequest, PredictResponse
from backend.app.services.analytics.predictor import MentalHealthPredictor

router = APIRouter(prefix="/predict", tags=["Predict"])


@router.post("/score", response_model=PredictResponse)
def predict_mental_health_score(req: PredictRequest):
    """
    Performs real-time student mental health score inference across the 200-tree Random Forest.
    Returns predicted score and valid ensemble tree spread (AC-22).
    """
    try:
        result = MentalHealthPredictor.predict(req.model_dump())
        return PredictResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(exc)}")

