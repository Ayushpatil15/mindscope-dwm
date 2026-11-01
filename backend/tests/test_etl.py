import pytest
from pathlib import Path
from sqlalchemy import text, select
from sqlalchemy.orm import sessionmaker

from backend.app.models.versioning import DatasetVersion
from backend.app.models.staging import StgSurveyResponse, ETLRun, ETLRejection
from backend.app.models.facts import FactSurveyResponse, FactLifestyle
from backend.app.etl.pipeline import run_etl_pipeline


CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "Student_Social_Media_And_Mental_Health_Impact.csv"


def test_duplicate_preservation_ac_17_and_ac_10(test_engine):
    """AC-10 & AC-17: Test full ETL pipeline extracts, stages, and loads all 5,000 records without loss."""
    session_factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    result = run_etl_pipeline(CSV_PATH, session_factory)
    assert result["status"] == "COMPLETED"
    assert result["rows_extracted"] == 5000
    assert result["rows_staged"] == 5000
    assert result["rows_loaded"] == 5000
    assert result["rows_rejected"] == 0

    with session_factory() as session:
        stg_cnt = session.scalar(select(text("COUNT(*) FROM stg_survey_responses")))
        fact_survey_cnt = session.scalar(select(text("COUNT(*) FROM fact_survey_response")))
        fact_life_cnt = session.scalar(select(text("COUNT(*) FROM fact_lifestyle")))
        active_version = session.scalar(
            select(DatasetVersion).where(DatasetVersion.is_active == True)  # noqa: E712
        )

        assert stg_cnt == 5000
        assert fact_survey_cnt == 5000
        assert fact_life_cnt == 5000
        assert active_version is not None
        assert active_version.row_count == 5000

        # Check identical rows preserved: rows 886 and 2405 have identical attributes
        r886 = session.scalar(
            select(FactSurveyResponse).where(FactSurveyResponse.source_row_id == 886)
        )
        r2405 = session.scalar(
            select(FactSurveyResponse).where(FactSurveyResponse.source_row_id == 2405)
        )
        assert r886 is not None
        assert r2405 is not None
        assert r886.survey_key != r2405.survey_key


def test_staging_completeness_ac_12(test_engine):
    """AC-12: Staging table stores raw unparsed strings for all 5,000 rows."""
    session_factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    run_etl_pipeline(CSV_PATH, session_factory)

    with session_factory() as session:
        stg_count = session.scalar(select(text("COUNT(*) FROM stg_survey_responses")))
        assert stg_count == 5000

        stg_row = session.scalar(
            select(StgSurveyResponse).where(StgSurveyResponse.source_row_num == 1)
        )
        assert stg_row is not None
        assert isinstance(stg_row.raw_age, str)
        assert isinstance(stg_row.raw_avg_daily_usage_hours, str)
        assert isinstance(stg_row.raw_mental_health_score, str)


def test_transaction_boundary_isolation_ac_18(test_engine, monkeypatch):
    """AC-18: Staging and audit logging persist even when warehouse loading fails."""
    session_factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    def mock_broken_load(*args, **kwargs):
        raise RuntimeError("Simulated failure during warehouse fact load")

    monkeypatch.setattr("backend.app.etl.pipeline.load_staging_to_warehouse", mock_broken_load)

    with pytest.raises(RuntimeError, match="Simulated failure"):
        run_etl_pipeline(CSV_PATH, session_factory)

    with session_factory() as session:
        failed_run = session.scalars(
            select(ETLRun).where(ETLRun.status == "FAILED")
        ).first()
        assert failed_run is not None
        assert "Simulated failure" in failed_run.error_message
        assert failed_run.rows_staged == 5000
        assert failed_run.completed_at is not None

        # Staged rows must remain preserved!
        stg_count = session.scalar(select(text("COUNT(*) FROM stg_survey_responses")))
        assert stg_count == 5000

        # Fact table must have 0 rows due to rollback
        fact_count = session.scalar(select(text("COUNT(*) FROM fact_survey_response")))
        assert fact_count == 0


def test_dataset_versioning_and_atomic_activation_ac_23(test_engine):
    """AC-23: Dataset versions can be created and atomically activated."""
    session_factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    # Ingest version 1
    res1 = run_etl_pipeline(CSV_PATH, session_factory)
    assert res1["status"] == "COMPLETED"

    # Ingest version 2
    res2 = run_etl_pipeline(CSV_PATH, session_factory)
    assert res2["status"] == "COMPLETED"

    with session_factory() as session:
        active_versions = session.scalars(
            select(DatasetVersion).where(DatasetVersion.is_active == True)  # noqa: E712
        ).all()
        # Exactly one dataset version must be active at any given time
        assert len(active_versions) == 1
        assert active_versions[0].version_id == res2["version_id"]

        all_versions = session.scalars(select(DatasetVersion)).all()
        assert len(all_versions) == 2
        # Version 1 is deactivated
        v1 = session.scalar(select(DatasetVersion).where(DatasetVersion.version_id == res1["version_id"]))
        assert v1.is_active is False
