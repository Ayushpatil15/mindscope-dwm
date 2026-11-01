from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.dashboard import DashboardOverviewResponse, KPISummary, StressDistributionItem, PlatformBreakdownItem, AcademicLevelSummaryItem

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/filters")
def get_dashboard_filters(db: Session = Depends(get_db)):
    """Returns available filter options for dropdown selectors."""
    platforms = [r[0] for r in db.execute(text("SELECT platform_name FROM dim_platform ORDER BY platform_name")).all()]
    countries = [r[0] for r in db.execute(text("SELECT country_name FROM dim_country ORDER BY country_name")).all()]
    levels = [r[0] for r in db.execute(text("SELECT academic_level FROM dim_academic ORDER BY tier_level")).all()]
    genders = [r[0] for r in db.execute(text("SELECT gender_name FROM dim_gender ORDER BY gender_name")).all()]
    stress_levels = ["Low", "Medium", "High", "Very High"]

    return {
        "platforms": platforms,
        "countries": countries,
        "academic_levels": levels,
        "genders": genders,
        "stress_levels": stress_levels
    }


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(
    country: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    academic_level: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    stress_level: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Returns aggregated KPIs and visualization data synchronized with global filters."""
    where_clauses = ["version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)"]
    params: Dict[str, Any] = {}

    if country and country != "All":
        where_clauses.append("country = :country")
        params["country"] = country
    if platform and platform != "All":
        where_clauses.append("platform = :platform")
        params["platform"] = platform
    if academic_level and academic_level != "All":
        where_clauses.append("academic_level = :academic_level")
        params["academic_level"] = academic_level
    if gender and gender != "All":
        where_clauses.append("gender = :gender")
        params["gender"] = gender
    if stress_level and stress_level != "All":
        where_clauses.append("stress_level = :stress_level")
        params["stress_level"] = stress_level

    where_sql = " AND ".join(where_clauses)

    # 1. Overall KPIs
    kpi_sql = f"""
    SELECT 
        COUNT(*) AS total_students,
        ROUND(COALESCE(AVG(mental_health_score), 0.0), 2) AS avg_mental_health_score,
        ROUND(COALESCE(AVG(avg_daily_usage_hours), 0.0), 2) AS avg_daily_usage_hours,
        ROUND(COALESCE(AVG(sleep_hours_per_night), 0.0), 2) AS avg_sleep_hours,
        ROUND(COALESCE(AVG(study_hours), 0.0), 2) AS avg_study_hours,
        ROUND(COALESCE(AVG(daily_unlocks), 0.0), 2) AS avg_daily_unlocks,
        COALESCE(MAX(version_id), 1) AS dataset_version
    FROM v_star_schema_denormalized
    WHERE {where_sql};
    """
    kpi_row = dict(db.execute(text(kpi_sql), params).mappings().one())
    total_students = kpi_row["total_students"] or 0

    # 2. Stress Distribution
    stress_sql = f"""
    SELECT 
        stress_level,
        COUNT(*) AS cnt
    FROM v_star_schema_denormalized
    WHERE {where_sql}
    GROUP BY stress_level
    ORDER BY cnt DESC;
    """
    stress_rows = db.execute(text(stress_sql), params).mappings().all()
    stress_dist = []
    for r in stress_rows:
        cnt = r["cnt"]
        pct = round((cnt / total_students * 100.0), 2) if total_students > 0 else 0.0
        stress_dist.append(StressDistributionItem(
            stress_level=r["stress_level"],
            count=cnt,
            percentage=pct
        ))

    # 3. Platform Breakdown
    platform_sql = f"""
    SELECT 
        platform,
        ROUND(AVG(avg_daily_usage_hours), 2) AS avg_usage,
        ROUND(AVG(mental_health_score), 2) AS avg_score,
        COUNT(*) AS cnt
    FROM v_star_schema_denormalized
    WHERE {where_sql}
    GROUP BY platform
    ORDER BY cnt DESC
    LIMIT 10;
    """
    platform_rows = db.execute(text(platform_sql), params).mappings().all()
    platform_items = [
        PlatformBreakdownItem(
            platform=r["platform"],
            avg_usage_hours=float(r["avg_usage"] or 0.0),
            avg_mental_score=float(r["avg_score"] or 0.0),
            students=r["cnt"]
        )
        for r in platform_rows
    ]

    # 4. Academic Level Summary
    academic_sql = f"""
    SELECT 
        academic_level,
        COUNT(*) AS cnt,
        ROUND(AVG(mental_health_score), 2) AS avg_score,
        ROUND(AVG(sleep_hours_per_night), 2) AS avg_sleep
    FROM v_star_schema_denormalized
    WHERE {where_sql}
    GROUP BY academic_level
    ORDER BY cnt DESC;
    """
    academic_rows = db.execute(text(academic_sql), params).mappings().all()
    academic_items = [
        AcademicLevelSummaryItem(
            level=r["academic_level"],
            students=r["cnt"],
            avg_mental_score=float(r["avg_score"] or 0.0),
            avg_sleep=float(r["avg_sleep"] or 0.0)
        )
        for r in academic_rows
    ]

    # 5. Lifestyle Matrix sample
    sample_sql = f"""
    SELECT 
        avg_daily_usage_hours,
        sleep_hours_per_night,
        study_hours,
        mental_health_score
    FROM v_star_schema_denormalized
    WHERE {where_sql}
    LIMIT 100;
    """
    sample_rows = db.execute(text(sample_sql), params).mappings().all()
    usage_vs_sleep = [[r["avg_daily_usage_hours"], r["sleep_hours_per_night"]] for r in sample_rows]
    study_vs_mh = [[r["study_hours"], r["mental_health_score"]] for r in sample_rows]

    return DashboardOverviewResponse(
        kpis=KPISummary(**kpi_row),
        stress_distribution=stress_dist,
        platform_usage_breakdown=platform_items,
        academic_level_summary=academic_items,
        lifestyle_matrix={
            "usage_vs_sleep": usage_vs_sleep,
            "study_vs_mental_score": study_vs_mh
        }
    )


@router.get("/insights")
def get_insights(db: Session = Depends(get_db)):
    """
    Computes data-derived empirical insights and actionable university counseling recommendations
    from live student survey records in the warehouse.
    """
    # 1. High screen time vs wellbeing
    q_screen = db.execute(text("""
        SELECT 
            ROUND(AVG(CASE WHEN avg_daily_usage_hours > 6.0 THEN mental_health_score END), 2) AS high_screen_score,
            ROUND(AVG(CASE WHEN avg_daily_usage_hours <= 3.5 THEN mental_health_score END), 2) AS low_screen_score,
            COUNT(CASE WHEN avg_daily_usage_hours > 6.0 THEN 1 END) AS high_screen_count
        FROM fact_survey_response
    """)).mappings().one()

    # 2. Sleep buffering effect
    q_sleep = db.execute(text("""
        SELECT 
            ROUND(AVG(CASE WHEN sleep_hours_per_night >= 7.5 THEN mental_health_score END), 2) AS good_sleep_score,
            ROUND(AVG(CASE WHEN sleep_hours_per_night < 6.0 THEN mental_health_score END), 2) AS poor_sleep_score
        FROM v_star_schema_denormalized
    """)).mappings().one()

    # 3. Undergraduate stress prevalence
    q_undergrad = db.execute(text("""
        SELECT 
            ROUND(COUNT(CASE WHEN a.academic_level = 'Undergraduate' THEN 1 END) * 100.0 / COUNT(*), 1) AS undergrad_pct,
            ROUND(COUNT(CASE WHEN a.academic_level = 'Undergraduate' AND s.stress_level = 'Very High' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(CASE WHEN s.stress_level = 'Very High' THEN 1 END), 0), 1) AS undergrad_vh_pct
        FROM fact_survey_response f
        JOIN dim_academic a ON f.academic_key = a.academic_key
        JOIN dim_stress s ON f.stress_key = s.stress_key
    """)).mappings().one()

    # 4. Top platform screen time
    q_plat = db.execute(text("""
        SELECT p.platform_name, ROUND(AVG(f.avg_daily_usage_hours), 2) AS avg_hrs, ROUND(AVG(f.daily_unlocks), 1) AS avg_unlocks
        FROM fact_survey_response f
        JOIN dim_platform p ON f.platform_key = p.platform_key
        GROUP BY p.platform_name
        ORDER BY avg_hrs DESC
        LIMIT 1
    """)).mappings().one()

    insights = [
        {
            "title": "Digital Screen Time vs. Wellbeing Disparity",
            "sentence": f"Students spending >6 hours/day on social media report an average mental wellbeing score of {q_screen['high_screen_score']}/10, compared to {q_screen['low_screen_score']}/10 for light users (<=3.5 hours).",
            "metric": f"{q_screen['high_screen_count']} High-Usage Students",
            "tone": "attention"
        },
        {
            "title": "Sleep Buffering Mitigates Stress Vulnerability",
            "sentence": f"Maintaining 7.5+ hours of nightly sleep preserves elevated psychological resilience (mean {q_sleep['good_sleep_score']}/10) compared to sleep-deprived cohorts (mean {q_sleep['poor_sleep_score']}/10).",
            "metric": f"+{round((q_sleep['good_sleep_score'] or 0) - (q_sleep['poor_sleep_score'] or 0), 2)} Score Delta",
            "tone": "positive"
        },
        {
            "title": "Undergraduate Stress Concentration",
            "sentence": f"Undergraduates represent {q_undergrad['undergrad_pct']}% of the survey population but account for {q_undergrad['undergrad_vh_pct']}% of all 'Very High' stress classification outcomes.",
            "metric": f"{q_undergrad['undergrad_vh_pct']}% of Peak Stress",
            "tone": "attention"
        },
        {
            "title": "Platform-Specific Screen Engagement",
            "sentence": f"{q_plat['platform_name']} users log the highest continuous digital engagement, averaging {q_plat['avg_hrs']} daily hours and {q_plat['avg_unlocks']} daily phone unlock interactions.",
            "metric": f"{q_plat['avg_hrs']}h Daily Usage",
            "tone": "neutral"
        }
    ]

    recommendations = [
        "Institute mandatory university digital wellness workshops targeting freshman and sophomore undergraduate cohorts.",
        "Promote circadian sleep hygiene guidelines (>=7.5 hours nightly) across academic residence halls during exam seasons.",
        "Deploy targeted notification-throttling nudges for mobile users logging in excess of 150 daily device unlocks.",
        "Incorporate cognitive stress-reduction counseling into high-intensity undergraduate degree curriculum tracks.",
        "Establish peer-led social media detachment groups to encourage substitution of screen hours with physical activity."
    ]

    return {
        "insights": insights,
        "recommendations": recommendations
    }


