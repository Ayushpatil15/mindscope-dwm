import json
from typing import List, Dict, Any, Tuple
from backend.app.models.staging import StgSurveyResponse, ETLRejection

VALID_GENDERS = {"Male", "Female", "Other", "Non-binary"}
VALID_ACADEMIC_LEVELS = {"High School", "Undergraduate", "Graduate"}
VALID_PURPOSES = {"Education", "Entertainment", "Networking", "News", "Other"}
VALID_STRESS_LEVELS = {"Low", "Medium", "High", "Very High"}


def validate_staged_record(
    stg: StgSurveyResponse,
    run_id: int
) -> Tuple[Dict[str, Any] | None, ETLRejection | None]:
    """
    Validates a single staged row against warehouse domain constraints.
    Returns (cleaned_dict, None) if valid, or (None, rejection_object) if invalid.
    """
    raw_dict = {
        "Age": stg.raw_age,
        "Gender": stg.raw_gender,
        "Country": stg.raw_country,
        "Academic_Level": stg.raw_academic_level,
        "Most_Used_Platform": stg.raw_most_used_platform,
        "Purpose_Of_Use": stg.raw_purpose_of_use,
        "Avg_Daily_Usage_Hours": stg.raw_avg_daily_usage_hours,
        "Daily_Unlocks": stg.raw_daily_unlocks,
        "Study_Hours": stg.raw_study_hours,
        "Physical_Activity_Hours": stg.raw_physical_activity_hours,
        "Sleep_Hours_Per_Night": stg.raw_sleep_hours_per_night,
        "Stress_Level": stg.raw_stress_level,
        "Mental_Health_Score": stg.raw_mental_health_score,
    }
    raw_json = json.dumps(raw_dict)

    def reject(col: str, val: Any, reason: str) -> Tuple[None, ETLRejection]:
        return None, ETLRejection(
            run_id=run_id,
            source_row_num=stg.source_row_num,
            column_name=col,
            invalid_value=str(val) if val is not None else "NULL",
            rejection_reason=reason,
            raw_record_json=raw_json
        )

    # 1. Age
    try:
        age = int(float(stg.raw_age))
        if not (10 <= age <= 100):
            return reject("Age", stg.raw_age, "Age must be between 10 and 100")
    except (ValueError, TypeError):
        return reject("Age", stg.raw_age, "Age must be a valid integer")

    # 2. Gender
    gender = (stg.raw_gender or "").strip()
    if gender not in VALID_GENDERS:
        return reject("Gender", stg.raw_gender, f"Gender must be one of {VALID_GENDERS}")

    # 3. Country
    country = (stg.raw_country or "").strip()
    if not country or len(country) > 100:
        return reject("Country", stg.raw_country, "Country must be non-empty and <= 100 chars")

    # 4. Academic_Level
    academic = (stg.raw_academic_level or "").strip()
    if academic not in VALID_ACADEMIC_LEVELS:
        return reject("Academic_Level", stg.raw_academic_level, f"Academic_Level must be one of {VALID_ACADEMIC_LEVELS}")

    # 5. Most_Used_Platform
    platform = (stg.raw_most_used_platform or "").strip()
    if not platform or len(platform) > 100:
        return reject("Most_Used_Platform", stg.raw_most_used_platform, "Platform must be non-empty and <= 100 chars")

    # 6. Purpose_Of_Use
    purpose = (stg.raw_purpose_of_use or "").strip()
    if purpose not in VALID_PURPOSES:
        return reject("Purpose_Of_Use", stg.raw_purpose_of_use, f"Purpose must be one of {VALID_PURPOSES}")

    # 7. Avg_Daily_Usage_Hours
    try:
        usage_hours = float(stg.raw_avg_daily_usage_hours)
        if not (0.0 <= usage_hours <= 24.0):
            return reject("Avg_Daily_Usage_Hours", stg.raw_avg_daily_usage_hours, "Usage hours must be in [0, 24]")
    except (ValueError, TypeError):
        return reject("Avg_Daily_Usage_Hours", stg.raw_avg_daily_usage_hours, "Usage hours must be a valid float")

    # 8. Daily_Unlocks
    try:
        unlocks = int(float(stg.raw_daily_unlocks))
        if not (0 <= unlocks <= 500):
            return reject("Daily_Unlocks", stg.raw_daily_unlocks, "Daily unlocks must be in [0, 500]")
    except (ValueError, TypeError):
        return reject("Daily_Unlocks", stg.raw_daily_unlocks, "Daily unlocks must be a valid integer")

    # 9. Study_Hours
    try:
        study = float(stg.raw_study_hours)
        if not (0.0 <= study <= 24.0):
            return reject("Study_Hours", stg.raw_study_hours, "Study hours must be in [0, 24]")
    except (ValueError, TypeError):
        return reject("Study_Hours", stg.raw_study_hours, "Study hours must be a valid float")

    # 10. Physical_Activity_Hours (allow zero-clamping for minor sensor/entry noise down to -1.0)
    try:
        activity_raw = float(stg.raw_physical_activity_hours)
        if not (-1.0 <= activity_raw <= 24.0):
            return reject("Physical_Activity_Hours", stg.raw_physical_activity_hours, "Activity hours must be in [0, 24]")
        activity = max(0.0, activity_raw)
    except (ValueError, TypeError):
        return reject("Physical_Activity_Hours", stg.raw_physical_activity_hours, "Activity hours must be a valid float")

    # 11. Sleep_Hours_Per_Night
    try:
        sleep = float(stg.raw_sleep_hours_per_night)
        if not (0.0 <= sleep <= 24.0):
            return reject("Sleep_Hours_Per_Night", stg.raw_sleep_hours_per_night, "Sleep hours must be in [0, 24]")
    except (ValueError, TypeError):
        return reject("Sleep_Hours_Per_Night", stg.raw_sleep_hours_per_night, "Sleep hours must be a valid float")

    # 12. Stress_Level
    stress = (stg.raw_stress_level or "").strip()
    if stress not in VALID_STRESS_LEVELS:
        return reject("Stress_Level", stg.raw_stress_level, f"Stress_Level must be one of {VALID_STRESS_LEVELS}")

    # 13. Mental_Health_Score
    try:
        mh_score = float(stg.raw_mental_health_score)
        if not (0.0 <= mh_score <= 10.0):
            return reject("Mental_Health_Score", stg.raw_mental_health_score, "Mental health score must be in [0, 10]")
    except (ValueError, TypeError):
        return reject("Mental_Health_Score", stg.raw_mental_health_score, "Mental health score must be a valid float")

    cleaned = {
        "source_row_num": stg.source_row_num,
        "age": age,
        "gender": gender,
        "country": country,
        "academic_level": academic,
        "platform": platform,
        "purpose": purpose,
        "avg_daily_usage_hours": usage_hours,
        "daily_unlocks": unlocks,
        "study_hours": study,
        "physical_activity_hours": activity,
        "sleep_hours_per_night": sleep,
        "stress_level": stress,
        "mental_health_score": mh_score,
    }
    return cleaned, None
