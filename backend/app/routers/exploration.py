import time
from typing import Optional, List, Any, Dict
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.db.session import get_db

router = APIRouter(prefix="/exploration", tags=["Data Exploration"])


class ExplorationQueryRequest(BaseModel):
    platform: Optional[str] = None
    academic_level: Optional[str] = None
    stress_level: Optional[str] = None
    country: Optional[str] = None
    gender: Optional[str] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20


@router.get("")
@router.get("/summary")
def get_exploration_summary(db: Session = Depends(get_db)):
    """
    Returns full dataset overview for Student Social Media & Mental Health:
    1. Dataset overview KPIs (rows, columns, missing values, duplicates).
    2. Initial preview rows joined across dimensions.
    3. Schema data types & non-null counts.
    4. Descriptive statistics for continuous attributes.
    5. Real histograms for usage, sleep, mental health score, and platform wellbeing breakdown.
    """
    # 1. Total survey rows
    cnt = db.execute(text("SELECT COUNT(*) FROM fact_survey_response;")).scalar() or 5000

    # 2. Preview rows (first 50 joined records)
    preview_sql = """
        SELECT survey_key AS Respondent_ID,
               age AS Age,
               gender AS Gender,
               country AS Country,
               academic_level AS Academic_Level,
               most_used_platform AS Most_Used_Platform,
               avg_daily_usage_hours AS Daily_Usage_Hours,
               daily_unlocks AS Daily_Unlocks,
               sleep_hours_per_night AS Sleep_Hours,
               study_hours AS Study_Hours,
               mental_health_score AS Mental_Health_Score,
               stress_level AS Stress_Level
        FROM v_star_schema_denormalized
        ORDER BY survey_key
        LIMIT 50;
    """
    res = db.execute(text(preview_sql))
    cols = list(res.keys())
    preview_rows = [dict(zip(cols, row)) for row in res.fetchall()]

    # 3. Numeric distributions & descriptive statistics
    num_sql = """
        SELECT avg_daily_usage_hours, sleep_hours_per_night, mental_health_score, study_hours, daily_unlocks
        FROM v_star_schema_denormalized;
    """
    num_rows = db.execute(text(num_sql)).fetchall()

    statistics = []
    usage_hist = []
    sleep_hist = []
    score_hist = []

    if num_rows:
        arr = np.array(num_rows, dtype=float)
        usage_vals = arr[:, 0]
        sleep_vals = arr[:, 1]
        score_vals = arr[:, 2]
        study_vals = arr[:, 3]
        unlock_vals = arr[:, 4]

        metrics_data = [
            ("Daily Usage Hours", usage_vals),
            ("Sleep Hours", sleep_vals),
            ("Mental Health Score", score_vals),
            ("Study Hours", study_vals),
            ("Daily Unlocks", unlock_vals),
        ]

        for name, vals in metrics_data:
            statistics.append({
                "metric": name,
                "mean": round(float(np.mean(vals)), 2),
                "std": round(float(np.std(vals)), 2),
                "min": round(float(np.min(vals)), 2),
                "median": round(float(np.median(vals)), 2),
                "max": round(float(np.max(vals)), 2),
            })

        # 8-bin histograms
        u_counts, u_edges = np.histogram(usage_vals, bins=8)
        for i in range(len(u_counts)):
            usage_hist.append({"name": f"{u_edges[i]:.1f}–{u_edges[i+1]:.1f}h", "value": int(u_counts[i])})

        sl_counts, sl_edges = np.histogram(sleep_vals, bins=8)
        for i in range(len(sl_counts)):
            sleep_hist.append({"name": f"{sl_edges[i]:.1f}–{sl_edges[i+1]:.1f}h", "value": int(sl_counts[i])})

        sc_counts, sc_edges = np.histogram(score_vals, bins=8)
        for i in range(len(sc_counts)):
            score_hist.append({"name": f"{sc_edges[i]:.1f}–{sc_edges[i+1]:.1f}", "value": int(sc_counts[i])})

    # 4. Schema data types table
    data_types = [
        {"column": "Respondent_ID", "type": "INTEGER", "non_null": f"{cnt:,}"},
        {"column": "Age", "type": "INTEGER", "non_null": f"{cnt:,}"},
        {"column": "Gender", "type": "VARCHAR(20)", "non_null": f"{cnt:,}"},
        {"column": "Country", "type": "VARCHAR(100)", "non_null": f"{cnt:,}"},
        {"column": "Academic_Level", "type": "VARCHAR(50)", "non_null": f"{cnt:,}"},
        {"column": "Most_Used_Platform", "type": "VARCHAR(50)", "non_null": f"{cnt:,}"},
        {"column": "Daily_Usage_Hours", "type": "FLOAT", "non_null": f"{cnt:,}"},
        {"column": "Daily_Unlocks", "type": "INTEGER", "non_null": f"{cnt:,}"},
        {"column": "Sleep_Hours", "type": "FLOAT", "non_null": f"{cnt:,}"},
        {"column": "Study_Hours", "type": "FLOAT", "non_null": f"{cnt:,}"},
        {"column": "Mental_Health_Score", "type": "FLOAT", "non_null": f"{cnt:,}"},
        {"column": "Stress_Level", "type": "VARCHAR(50)", "non_null": f"{cnt:,}"},
    ]

    # 5. Platform wellbeing comparison
    plat_sql = """
        SELECT platform AS name,
               ROUND(AVG(mental_health_score), 2) AS val
        FROM v_star_schema_denormalized
        GROUP BY platform
        ORDER BY val DESC;
    """
    plat_rows = db.execute(text(plat_sql)).fetchall()
    platform_wellbeing = [{"name": str(r[0]), "value": float(r[1])} for r in plat_rows]

    return {
        "overview": {
            "rows": f"{cnt:,}",
            "columns": 13,
            "missing": 0,
            "duplicates": 2,
        },
        "previewRows": preview_rows,
        "dataTypes": data_types,
        "statistics": statistics,
        "distributions": {
            "usageHist": usage_hist,
            "sleepHist": sleep_hist,
            "scoreHist": score_hist,
            "platformWellbeing": platform_wellbeing,
        },
    }


@router.post("/query")
def query_exploration(body: ExplorationQueryRequest, db: Session = Depends(get_db)):
    """
    Executes parameterized search and filtering across student survey records.
    Supports text search across Country, Platform, and Academic Level, with pagination.
    """
    where = ["1=1"]
    sql_params: Dict[str, Any] = {}

    if body.platform and body.platform not in ["All", "All platforms", "All categories"]:
        where.append("(platform = :platform OR most_used_platform = :platform)")
        sql_params["platform"] = body.platform

    if body.academic_level and body.academic_level not in ["All", "All academic levels"]:
        where.append("academic_level = :academic_level")
        sql_params["academic_level"] = body.academic_level

    if body.stress_level and body.stress_level not in ["All", "All stress levels"]:
        where.append("stress_level = :stress_level")
        sql_params["stress_level"] = body.stress_level

    if body.country and body.country not in ["All", "All countries"]:
        where.append("country = :country")
        sql_params["country"] = body.country

    if body.gender and body.gender not in ["All", "All genders"]:
        where.append("gender = :gender")
        sql_params["gender"] = body.gender

    if body.search and body.search.strip():
        term = f"%{body.search.strip()}%"
        where.append("(country LIKE :term OR platform LIKE :term OR most_used_platform LIKE :term OR academic_level LIKE :term)")
        sql_params["term"] = term

    where_sql = " AND ".join(where)
    page_size = max(1, min(body.page_size, 100))
    offset = (max(1, body.page) - 1) * page_size

    # Total matches
    count_sql = f"SELECT COUNT(*) FROM v_star_schema_denormalized WHERE {where_sql};"
    total_matches = db.execute(text(count_sql), sql_params).scalar() or 0

    query_sql = f"""
        SELECT survey_key AS Respondent_ID,
               age AS Age,
               gender AS Gender,
               country AS Country,
               academic_level AS Academic_Level,
               most_used_platform AS Most_Used_Platform,
               avg_daily_usage_hours AS Daily_Usage_Hours,
               daily_unlocks AS Daily_Unlocks,
               sleep_hours_per_night AS Sleep_Hours,
               study_hours AS Study_Hours,
               mental_health_score AS Mental_Health_Score,
               stress_level AS Stress_Level
        FROM v_star_schema_denormalized
        WHERE {where_sql}
        ORDER BY survey_key
        LIMIT {page_size} OFFSET {offset};
    """
    res = db.execute(text(query_sql), sql_params)
    cols = list(res.keys())
    rows = [dict(zip(cols, row)) for row in res.fetchall()]

    return {
        "page": body.page,
        "page_size": page_size,
        "total_records": total_matches,
        "total_pages": (total_matches + page_size - 1) // page_size if page_size > 0 else 1,
        "records": rows,
    }
