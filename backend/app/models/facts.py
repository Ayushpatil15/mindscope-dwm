from datetime import datetime, timezone
from sqlalchemy import (
    Integer, Float, ForeignKey, DateTime, CheckConstraint, UniqueConstraint, ForeignKeyConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class FactSurveyResponse(Base):
    __tablename__ = "fact_survey_response"

    survey_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    respondent_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_respondent.respondent_key"), nullable=False)
    academic_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_academic.academic_key"), nullable=False)
    country_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_country.country_key"), nullable=False)
    platform_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_platform.platform_key"), nullable=False)
    purpose_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_purpose.purpose_key"), nullable=False)
    stress_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_stress.stress_key"), nullable=False)
    version_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset_versions.version_id"), nullable=False)
    
    avg_daily_usage_hours: Mapped[float] = mapped_column(Float, nullable=False)
    daily_unlocks: Mapped[int] = mapped_column(Integer, nullable=False)
    mental_health_score: Mapped[float] = mapped_column(Float, nullable=False)
    source_row_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("version_id", "source_row_id", name="uq_fact_survey_version_row"),
        CheckConstraint("avg_daily_usage_hours >= 0.0 AND avg_daily_usage_hours <= 24.0", name="chk_usage_hours"),
        CheckConstraint("daily_unlocks >= 0 AND daily_unlocks <= 500", name="chk_daily_unlocks"),
        CheckConstraint("mental_health_score >= 0.0 AND mental_health_score <= 10.0", name="chk_mental_health_score"),
    )


class FactLifestyle(Base):
    __tablename__ = "fact_lifestyle"

    lifestyle_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    respondent_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_respondent.respondent_key"), nullable=False)
    academic_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_academic.academic_key"), nullable=False)
    country_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_country.country_key"), nullable=False)
    platform_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_platform.platform_key"), nullable=False)
    version_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset_versions.version_id"), nullable=False)
    
    study_hours: Mapped[float] = mapped_column(Float, nullable=False)
    physical_activity_hours: Mapped[float] = mapped_column(Float, nullable=False)
    sleep_hours_per_night: Mapped[float] = mapped_column(Float, nullable=False)
    source_row_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("version_id", "source_row_id", name="uq_fact_lifestyle_version_row"),
        ForeignKeyConstraint(
            ["version_id", "source_row_id"],
            ["fact_survey_response.version_id", "fact_survey_response.source_row_id"],
            name="fk_fact_lifestyle_common_grain"
        ),
        CheckConstraint("study_hours >= 0.0 AND study_hours <= 24.0", name="chk_study_hours"),
        CheckConstraint("physical_activity_hours >= 0.0 AND physical_activity_hours <= 24.0", name="chk_activity_hours"),
        CheckConstraint("sleep_hours_per_night >= 0.0 AND sleep_hours_per_night <= 24.0", name="chk_sleep_hours"),
    )

