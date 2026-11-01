from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    age: int = Field(default=21, ge=10, le=100)
    gender: str = Field(default="Male")
    country: str = Field(default="India")
    academic_level: str = Field(default="Undergraduate")
    most_used_platform: str = Field(default="Instagram")
    purpose_of_use: str = Field(default="Entertainment")
    avg_daily_usage_hours: float = Field(default=5.0, ge=0.0, le=24.0)
    daily_unlocks: int = Field(default=150, ge=0, le=500)
    study_hours: float = Field(default=3.0, ge=0.0, le=24.0)
    physical_activity_hours: float = Field(default=1.5, ge=0.0, le=24.0)
    sleep_hours_per_night: float = Field(default=7.0, ge=0.0, le=24.0)
    stress_level: str = Field(default="Medium")


class EnsembleTreeSpread(BaseModel):
    tree_percentile_10: float
    tree_percentile_90: float
    metric_description: str


class PredictResponse(BaseModel):
    predicted_score: float
    ensemble_tree_spread: EnsembleTreeSpread
    interpretation: str

