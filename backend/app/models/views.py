from sqlalchemy import text
from sqlalchemy.engine import Engine

VIEW_STAR_DENORMALIZED_DDL = """
CREATE VIEW IF NOT EXISTS v_star_schema_denormalized AS
SELECT 
    f.survey_key,
    r.source_respondent_id AS student_id,
    r.age,
    g.gender_name AS gender,
    c.country_name AS country,
    a.academic_level,
    p.platform_name AS most_used_platform,
    p.platform_name AS platform,
    pu.purpose_name AS purpose_of_use,
    pu.purpose_name AS purpose,
    st.stress_level,
    f.avg_daily_usage_hours,
    f.daily_unlocks,
    f.mental_health_score,
    l.study_hours,
    l.physical_activity_hours,
    l.sleep_hours_per_night,
    f.version_id
FROM fact_survey_response f
JOIN dim_respondent r ON f.respondent_key = r.respondent_key
JOIN dim_gender g ON r.gender_key = g.gender_key
JOIN dim_academic a ON f.academic_key = a.academic_key
JOIN dim_country c ON f.country_key = c.country_key
JOIN dim_platform p ON f.platform_key = p.platform_key
JOIN dim_purpose pu ON f.purpose_key = pu.purpose_key
JOIN dim_stress st ON f.stress_key = st.stress_key
JOIN fact_lifestyle l ON f.version_id = l.version_id AND f.source_row_id = l.source_row_id;
"""

def create_views(engine: Engine):
    """Executes DDL to create analytical views in SQLite."""
    with engine.begin() as conn:
        conn.execute(text(VIEW_STAR_DENORMALIZED_DDL))
