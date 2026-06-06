from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PeriodStatDto:
    period: str
    courses_taken: int
    courses_passed: int
    courses_failed: int
    pass_rate: str
    weighted_average: str


@dataclass
class AcademicAnalyticsDto:
    period_stats: list[PeriodStatDto] = field(default_factory=list)
    total_courses: int = 0
    total_passed: int = 0
    total_failed: int = 0
    overall_pass_rate: str = "0"
    retried_course_names: list[str] = field(default_factory=list)
    best_period: Optional[str] = None
    worst_period: Optional[str] = None
