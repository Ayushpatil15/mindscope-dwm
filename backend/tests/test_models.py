import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from backend.app.models.versioning import DatasetVersion
from backend.app.models.dimensions import (
    DimGender, DimAcademic, DimCountry, DimPlatform, DimPurpose, DimStress, DimRespondent
)
from backend.app.models.facts import FactSurveyResponse, FactLifestyle


def test_schema_tables_and_view_exist(test_session):
    """Verify that all dimensional tables, fact tables, and views are created."""
    tables = [
        "dataset_versions",
        "stg_survey_responses",
        "etl_runs",
        "etl_rejections",
        "dim_gender",
        "dim_academic",
        "dim_country",
        "dim_platform",
        "dim_purpose",
        "dim_stress",
        "dim_respondent",
        "fact_survey_response",
        "fact_lifestyle"
    ]
    for tbl in tables:
        res = test_session.execute(
            text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tbl}'")
        ).scalar()
        assert res == tbl, f"Table {tbl} was not created"

    view_res = test_session.execute(
        text("SELECT name FROM sqlite_master WHERE type='view' AND name='v_star_schema_denormalized'")
    ).scalar()
    assert view_res == "v_star_schema_denormalized"


def test_foreign_key_enforcement_ac_02(test_session):
    """AC-02: Verify SQLite foreign key enforcement prevents orphan records."""
    # Attempt to insert FactSurveyResponse referencing non-existent dimension keys
    orphan_fact = FactSurveyResponse(
        respondent_key=999,
        academic_key=999,
        country_key=999,
        platform_key=999,
        purpose_key=999,
        stress_key=999,
        version_id=999,
        avg_daily_usage_hours=4.5,
        daily_unlocks=120,
        mental_health_score=7.0,
        source_row_id=1
    )
    test_session.add(orphan_fact)
    with pytest.raises(IntegrityError):
        test_session.commit()
    test_session.rollback()


def test_check_constraints_ac_11(test_session):
    """AC-11: Verify check constraints on ranges and categorical domains."""
    # Setup baseline version and dimensions
    v = DatasetVersion(
        version_id=1,
        version_number=1,
        batch_id="batch_001",
        source_filename="test.csv",
        sha256_checksum="dummy_checksum_1234567890",
        is_active=True,
        row_count=1
    )
    g = DimGender(gender_name="Male")
    a = DimAcademic(academic_level="Undergraduate", tier_level=2)
    c = DimCountry(country_name="India", region="Asia")
    p = DimPlatform(platform_name="Instagram", platform_category="Social")
    pu = DimPurpose(purpose_name="Entertainment")
    s = DimStress(stress_level="Medium", stress_rank=2)
    test_session.add_all([v, g, a, c, p, pu, s])
    test_session.commit()

    r = DimRespondent(source_respondent_id=1, age=21, gender_key=g.gender_key, academic_key=a.academic_key)
    test_session.add(r)
    test_session.commit()

    # Test mental_health_score > 10.0
    bad_fact1 = FactSurveyResponse(
        respondent_key=r.respondent_key,
        academic_key=a.academic_key,
        country_key=c.country_key,
        platform_key=p.platform_key,
        purpose_key=pu.purpose_key,
        stress_key=s.stress_key,
        version_id=v.version_id,
        avg_daily_usage_hours=4.5,
        daily_unlocks=120,
        mental_health_score=11.5,  # Exceeds 10.0
        source_row_id=1
    )
    test_session.add(bad_fact1)
    with pytest.raises(IntegrityError):
        test_session.commit()
    test_session.rollback()

    # Test daily_usage_hours > 24.0
    bad_fact2 = FactSurveyResponse(
        respondent_key=r.respondent_key,
        academic_key=a.academic_key,
        country_key=c.country_key,
        platform_key=p.platform_key,
        purpose_key=pu.purpose_key,
        stress_key=s.stress_key,
        version_id=v.version_id,
        avg_daily_usage_hours=25.0,  # Exceeds 24.0
        daily_unlocks=120,
        mental_health_score=7.0,
        source_row_id=1
    )
    test_session.add(bad_fact2)
    with pytest.raises(IntegrityError):
        test_session.commit()
    test_session.rollback()


def test_dim_respondent_semantics_ac_19(test_session):
    """AC-19: Verify dim_respondent semantics, surrogate keys, and lineage."""
    g = DimGender(gender_name="Female")
    a = DimAcademic(academic_level="Graduate", tier_level=3)
    test_session.add_all([g, a])
    test_session.commit()

    # Create respondent with source_respondent_id
    resp1 = DimRespondent(source_respondent_id=101, age=24, gender_key=g.gender_key, academic_key=a.academic_key)
    test_session.add(resp1)
    test_session.commit()

    assert resp1.respondent_key is not None
    assert resp1.source_respondent_id == 101

    # Unique constraint on source_respondent_id prevents duplicate survey respondent mapping
    resp2 = DimRespondent(source_respondent_id=101, age=24, gender_key=g.gender_key, academic_key=a.academic_key)
    test_session.add(resp2)
    with pytest.raises(IntegrityError):
        test_session.commit()
    test_session.rollback()


def test_common_grain_enforcement_ac_21(test_session):
    """AC-21: Verify 1-to-1 common grain between fact_survey_response and fact_lifestyle."""
    v = DatasetVersion(
        version_id=1,
        version_number=1,
        batch_id="batch_001",
        source_filename="test.csv",
        sha256_checksum="dummy_checksum_1234567890",
        is_active=True,
        row_count=1
    )
    g = DimGender(gender_name="Other")
    a = DimAcademic(academic_level="High School", tier_level=1)
    c = DimCountry(country_name="USA", region="Americas")
    p = DimPlatform(platform_name="YouTube", platform_category="Video")
    pu = DimPurpose(purpose_name="Education")
    s = DimStress(stress_level="Low", stress_rank=1)
    test_session.add_all([v, g, a, c, p, pu, s])
    test_session.commit()

    r = DimRespondent(source_respondent_id=1, age=17, gender_key=g.gender_key, academic_key=a.academic_key)
    test_session.add(r)
    test_session.commit()

    # Insert valid FactSurveyResponse
    fact_resp = FactSurveyResponse(
        respondent_key=r.respondent_key,
        academic_key=a.academic_key,
        country_key=c.country_key,
        platform_key=p.platform_key,
        purpose_key=pu.purpose_key,
        stress_key=s.stress_key,
        version_id=v.version_id,
        avg_daily_usage_hours=3.0,
        daily_unlocks=80,
        mental_health_score=8.0,
        source_row_id=1
    )
    test_session.add(fact_resp)
    test_session.commit()

    # Insert valid FactLifestyle with matching (version_id, source_row_id)
    fact_life = FactLifestyle(
        respondent_key=r.respondent_key,
        academic_key=a.academic_key,
        country_key=c.country_key,
        platform_key=p.platform_key,
        version_id=v.version_id,
        study_hours=4.0,
        physical_activity_hours=1.5,
        sleep_hours_per_night=7.5,
        source_row_id=1
    )
    test_session.add(fact_life)
    test_session.commit()

    # Attempt to insert FactLifestyle with orphan (version_id, source_row_id) = (1, 999)
    orphan_life = FactLifestyle(
        respondent_key=r.respondent_key,
        academic_key=a.academic_key,
        country_key=c.country_key,
        platform_key=p.platform_key,
        version_id=v.version_id,
        study_hours=4.0,
        physical_activity_hours=1.5,
        sleep_hours_per_night=7.5,
        source_row_id=999
    )
    test_session.add(orphan_life)
    with pytest.raises(IntegrityError):
        test_session.commit()
    test_session.rollback()
