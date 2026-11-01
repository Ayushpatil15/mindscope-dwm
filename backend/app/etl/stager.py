from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.models.staging import StgSurveyResponse, ETLRun


def stage_raw_records(
    session: Session,
    batch_id: str,
    source_filename: str,
    raw_rows: List[Dict[str, str]]
) -> Tuple[int, int]:
    """
    Executes Transaction 1: Staging raw extracted records and creating an ETLRun record.
    Returns (run_id, staged_count).
    """
    run = ETLRun(
        batch_id=batch_id,
        source_file=source_filename,
        status="RUNNING",
        rows_extracted=len(raw_rows),
        rows_staged=len(raw_rows),
        rows_loaded=0,
        rows_rejected=0
    )
    session.add(run)
    session.flush()  # Populates run.run_id

    stg_objects = []
    for idx, row in enumerate(raw_rows, start=1):
        stg_objects.append(
            StgSurveyResponse(
                batch_id=batch_id,
                source_row_num=idx,
                raw_age=row.get("Age"),
                raw_gender=row.get("Gender"),
                raw_country=row.get("Country"),
                raw_academic_level=row.get("Academic_Level"),
                raw_most_used_platform=row.get("Most_Used_Platform"),
                raw_purpose_of_use=row.get("Purpose_Of_Use"),
                raw_avg_daily_usage_hours=row.get("Avg_Daily_Usage_Hours"),
                raw_daily_unlocks=row.get("Daily_Unlocks"),
                raw_study_hours=row.get("Study_Hours"),
                raw_physical_activity_hours=row.get("Physical_Activity_Hours"),
                raw_sleep_hours_per_night=row.get("Sleep_Hours_Per_Night"),
                raw_stress_level=row.get("Stress_Level"),
                raw_mental_health_score=row.get("Mental_Health_Score")
            )
        )

    session.bulk_save_objects(stg_objects)
    session.commit()

    return run.run_id, len(stg_objects)

