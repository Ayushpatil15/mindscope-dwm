from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class StgSurveyResponse(Base):
    __tablename__ = "stg_survey_responses"

    stg_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(String(100), nullable=False)
    source_row_num: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_age: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_gender: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_country: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_academic_level: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_most_used_platform: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_purpose_of_use: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_avg_daily_usage_hours: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_daily_unlocks: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_study_hours: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_physical_activity_hours: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_sleep_hours_per_night: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_stress_level: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_mental_health_score: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingestion_timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("batch_id", "source_row_num", name="uq_batch_source_row"),
    )


class ETLRun(Base):
    __tablename__ = "etl_runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source_file: Mapped[str] = mapped_column(String(255), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="RUNNING", nullable=False)
    rows_extracted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rows_staged: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rows_loaded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    rejections: Mapped[list["ETLRejection"]] = relationship("ETLRejection", back_populates="run", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('RUNNING', 'COMPLETED', 'FAILED')", name="chk_etl_run_status"),
    )


class ETLRejection(Base):
    __tablename__ = "etl_rejections"

    rejection_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("etl_runs.run_id", ondelete="CASCADE"), nullable=False)
    source_row_num: Mapped[int] = mapped_column(Integer, nullable=False)
    column_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    invalid_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=False)
    raw_record_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejected_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    run: Mapped["ETLRun"] = relationship("ETLRun", back_populates="rejections")

