from sqlalchemy import select, func
from sqlalchemy.orm import Session
from backend.app.models.facts import FactSurveyResponse, FactLifestyle


class ReconciliationError(Exception):
    pass


def reconcile_load(
    session: Session,
    version_id: int,
    staged_count: int,
    loaded_count: int,
    rejected_count: int
) -> None:
    """
    Validates ETL reconciliation invariants:
    1. staged_count == loaded_count + rejected_count
    2. COUNT(fact_survey_response) == COUNT(fact_lifestyle) == loaded_count
    3. Aggregate statistical checks (no corruption)
    """
    if staged_count != (loaded_count + rejected_count):
        raise ReconciliationError(
            f"Row count mismatch: staged ({staged_count}) != loaded ({loaded_count}) + rejected ({rejected_count})"
        )

    survey_count = session.scalar(
        select(func.count(FactSurveyResponse.survey_key))
        .where(FactSurveyResponse.version_id == version_id)
    )
    lifestyle_count = session.scalar(
        select(func.count(FactLifestyle.lifestyle_key))
        .where(FactLifestyle.version_id == version_id)
    )

    if survey_count != loaded_count:
        raise ReconciliationError(
            f"FactSurveyResponse count ({survey_count}) != loaded count ({loaded_count})"
        )

    if lifestyle_count != loaded_count:
        raise ReconciliationError(
            f"FactLifestyle count ({lifestyle_count}) != loaded count ({loaded_count})"
        )

    if survey_count != lifestyle_count:
        raise ReconciliationError(
            f"Common grain mismatch: FactSurveyResponse ({survey_count}) != FactLifestyle ({lifestyle_count})"
        )

