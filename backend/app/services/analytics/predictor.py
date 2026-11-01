import numpy as np
import pandas as pd
from typing import Dict, Any
from backend.app.core.cache import CacheManager
import backend.labs as labs


class MentalHealthPredictor:
    """
    Wraps existing Random Forest model from backend.labs with valid ensemble tree spread disclosure (AC-22).
    """

    @classmethod
    def predict(cls, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Normalize input field keys (handle snake_case and PascalCase)
        norm_map = {
            "age": "Age",
            "gender": "Gender",
            "country": "Country",
            "academic_level": "Academic_Level",
            "most_used_platform": "Most_Used_Platform",
            "purpose_of_use": "Purpose_Of_Use",
            "avg_daily_usage_hours": "Avg_Daily_Usage_Hours",
            "daily_unlocks": "Daily_Unlocks",
            "study_hours": "Study_Hours",
            "physical_activity_hours": "Physical_Activity_Hours",
            "sleep_hours_per_night": "Sleep_Hours_Per_Night",
            "stress_level": "Stress_Level",
        }
        
        normalized: Dict[str, Any] = {}
        for k, v in inputs.items():
            mapped_k = norm_map.get(k.lower(), k)
            normalized[mapped_k] = v

        # Fallback defaults for any missing inputs
        defaults = {
            "Age": 21,
            "Gender": "Male",
            "Country": "India",
            "Academic_Level": "Undergraduate",
            "Most_Used_Platform": "Instagram",
            "Purpose_Of_Use": "Entertainment",
            "Avg_Daily_Usage_Hours": 5.0,
            "Daily_Unlocks": 170,
            "Study_Hours": 3.0,
            "Physical_Activity_Hours": 1.5,
            "Sleep_Hours_Per_Night": 7.0,
            "Stress_Level": "Medium"
        }
        for k, def_v in defaults.items():
            if k not in normalized or normalized[k] is None:
                normalized[k] = def_v

        # Execute Random Forest prediction via labs engine
        res = labs.rf_predict(normalized)
        score = res["score"]
        low = res["low"]
        high = res["high"]

        # Wellbeing interpretation
        if score < 5.0:
            interpretation = "Projected in Low student wellbeing band. Consider reducing daily usage and prioritizing sleep."
        elif score < 7.0:
            interpretation = "Projected in Moderate student wellbeing band."
        else:
            interpretation = "Projected in High student wellbeing band. Healthy digital and lifestyle balance observed."

        return {
            "predicted_score": score,
            "ensemble_tree_spread": {
                "tree_percentile_10": low,
                "tree_percentile_90": high,
                "metric_description": (
                    "Ensemble disagreement range across 200 decision trees (10th to 90th percentile). "
                    "Note: This represents tree prediction spread and is not a calibrated statistical prediction interval."
                )
            },
            "interpretation": interpretation
        }

