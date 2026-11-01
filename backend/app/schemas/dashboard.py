from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class KPISummary(BaseModel):
    total_students: int
    avg_mental_health_score: float
    avg_daily_usage_hours: float
    avg_sleep_hours: float
    avg_study_hours: float
    avg_daily_unlocks: float
    dataset_version: int


class StressDistributionItem(BaseModel):
    stress_level: str
    count: int
    percentage: float


class PlatformBreakdownItem(BaseModel):
    platform: str
    avg_usage_hours: float
    avg_mental_score: float
    students: int


class AcademicLevelSummaryItem(BaseModel):
    level: str
    students: int
    avg_mental_score: float
    avg_sleep: float


class DashboardOverviewResponse(BaseModel):
    kpis: KPISummary
    stress_distribution: List[StressDistributionItem]
    platform_usage_breakdown: List[PlatformBreakdownItem]
    academic_level_summary: List[AcademicLevelSummaryItem]
    lifestyle_matrix: Dict[str, Any]

