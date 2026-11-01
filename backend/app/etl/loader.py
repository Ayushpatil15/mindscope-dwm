from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.app.models.versioning import DatasetVersion
from backend.app.models.staging import StgSurveyResponse, ETLRejection
from backend.app.models.dimensions import (
    DimGender, DimAcademic, DimCountry, DimPlatform, DimPurpose, DimStress, DimRespondent
)
from backend.app.models.facts import FactSurveyResponse, FactLifestyle
from .validator import validate_staged_record


ACADEMIC_TIERS = {
    "High School": 1,
    "Undergraduate": 2,
    "Graduate": 3,
}

STRESS_RANKS = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Very High": 4,
}

PLATFORM_CATEGORIES = {
    "YouTube": "Video",
    "TikTok": "Video",
    "WhatsApp": "Messaging",
    "Snapchat": "Messaging",
    "Telegram": "Messaging",
    "LINE": "Messaging",
    "KakaoTalk": "Messaging",
    "WeChat": "Messaging",
    "LinkedIn": "Professional",
    "Instagram": "Social",
    "Twitter": "Social",
    "Facebook": "Social",
    "VKontakte": "Social",
    "Reddit": "Social",
}


def load_staging_to_warehouse(
    session: Session,
    batch_id: str,
    run_id: int,
    source_filename: str,
    sha256_checksum: str
) -> Tuple[int, int, int]:
    """
    Executes Transaction 2:
    - Validates staged rows
    - Records rejections
    - Upserts dimensions
    - Bulk loads fact_survey_response & fact_lifestyle
    - Creates inactive DatasetVersion (is_active=False)
    Returns: (version_id, loaded_count, rejected_count)
    """
    stg_records = session.scalars(
        select(StgSurveyResponse)
        .where(StgSurveyResponse.batch_id == batch_id)
        .order_by(StgSurveyResponse.source_row_num)
    ).all()

    valid_rows: List[Dict[str, Any]] = []
    rejections: List[ETLRejection] = []

    for stg in stg_records:
        cleaned, rej = validate_staged_record(stg, run_id)
        if rej:
            rejections.append(rej)
        else:
            valid_rows.append(cleaned)

    if rejections:
        session.bulk_save_objects(rejections)
        session.flush()

    # 1. Dimension resolution with in-memory caching
    gender_cache = {g.gender_name: g.gender_key for g in session.scalars(select(DimGender)).all()}
    academic_cache = {a.academic_level: a.academic_key for a in session.scalars(select(DimAcademic)).all()}
    country_cache = {c.country_name: c.country_key for c in session.scalars(select(DimCountry)).all()}
    platform_cache = {p.platform_name: p.platform_key for p in session.scalars(select(DimPlatform)).all()}
    purpose_cache = {pu.purpose_name: pu.purpose_key for pu in session.scalars(select(DimPurpose)).all()}
    stress_cache = {s.stress_level: s.stress_key for s in session.scalars(select(DimStress)).all()}

    # Upsert missing non-respondent dimensions
    for r in valid_rows:
        if r["gender"] not in gender_cache:
            g_obj = DimGender(gender_name=r["gender"])
            session.add(g_obj)
            session.flush()
            gender_cache[r["gender"]] = g_obj.gender_key

        if r["academic_level"] not in academic_cache:
            a_obj = DimAcademic(
                academic_level=r["academic_level"],
                tier_level=ACADEMIC_TIERS.get(r["academic_level"], 2)
            )
            session.add(a_obj)
            session.flush()
            academic_cache[r["academic_level"]] = a_obj.academic_key

        if r["country"] not in country_cache:
            c_obj = DimCountry(country_name=r["country"], region="Global")
            session.add(c_obj)
            session.flush()
            country_cache[r["country"]] = c_obj.country_key

        if r["platform"] not in platform_cache:
            cat = PLATFORM_CATEGORIES.get(r["platform"], "Other")
            p_obj = DimPlatform(platform_name=r["platform"], platform_category=cat)
            session.add(p_obj)
            session.flush()
            platform_cache[r["platform"]] = p_obj.platform_key

        if r["purpose"] not in purpose_cache:
            pu_obj = DimPurpose(purpose_name=r["purpose"])
            session.add(pu_obj)
            session.flush()
            purpose_cache[r["purpose"]] = pu_obj.purpose_key

        if r["stress_level"] not in stress_cache:
            s_obj = DimStress(
                stress_level=r["stress_level"],
                stress_rank=STRESS_RANKS.get(r["stress_level"], 2)
            )
            session.add(s_obj)
            session.flush()
            stress_cache[r["stress_level"]] = s_obj.stress_key

    # 2. DimRespondent caching & upsert
    respondent_cache = {
        resp.source_respondent_id: resp.respondent_key
        for resp in session.scalars(select(DimRespondent)).all()
    }

    for r in valid_rows:
        src_id = r["source_row_num"]
        if src_id not in respondent_cache:
            resp_obj = DimRespondent(
                source_respondent_id=src_id,
                age=r["age"],
                gender_key=gender_cache[r["gender"]],
                academic_key=academic_cache[r["academic_level"]],
            )
            session.add(resp_obj)
            session.flush()
            respondent_cache[src_id] = resp_obj.respondent_key

    # 3. Determine next version number
    max_ver = session.scalar(select(func.max(DatasetVersion.version_number))) or 0
    next_ver = max_ver + 1

    dataset_ver = DatasetVersion(
        version_number=next_ver,
        batch_id=batch_id,
        source_filename=source_filename,
        row_count=len(valid_rows),
        sha256_checksum=sha256_checksum,
        is_active=False
    )
    session.add(dataset_ver)
    session.flush()
    ver_id = dataset_ver.version_id

    # 4. Prepare bulk fact rows maintaining 1-to-1 grain
    survey_facts = []
    lifestyle_facts = []
    now = datetime.now(timezone.utc)

    for r in valid_rows:
        src_row = r["source_row_num"]
        resp_k = respondent_cache[src_row]
        acad_k = academic_cache[r["academic_level"]]
        ctry_k = country_cache[r["country"]]
        plat_k = platform_cache[r["platform"]]
        purp_k = purpose_cache[r["purpose"]]
        strs_k = stress_cache[r["stress_level"]]

        survey_facts.append(
            FactSurveyResponse(
                respondent_key=resp_k,
                academic_key=acad_k,
                country_key=ctry_k,
                platform_key=plat_k,
                purpose_key=purp_k,
                stress_key=strs_k,
                version_id=ver_id,
                avg_daily_usage_hours=r["avg_daily_usage_hours"],
                daily_unlocks=r["daily_unlocks"],
                mental_health_score=r["mental_health_score"],
                source_row_id=src_row,
                created_at=now,
            )
        )

        lifestyle_facts.append(
            FactLifestyle(
                respondent_key=resp_k,
                academic_key=acad_k,
                country_key=ctry_k,
                platform_key=plat_k,
                version_id=ver_id,
                study_hours=r["study_hours"],
                physical_activity_hours=r["physical_activity_hours"],
                sleep_hours_per_night=r["sleep_hours_per_night"],
                source_row_id=src_row,
                created_at=now,
            )
        )

    # Insert survey facts first so lifestyle foreign keys resolve
    session.bulk_save_objects(survey_facts)
    session.flush()
    session.bulk_save_objects(lifestyle_facts)
    session.flush()

    return ver_id, len(valid_rows), len(rejections)

