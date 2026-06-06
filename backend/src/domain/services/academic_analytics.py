from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from ..entities.academic_record import AcademicRecord, CourseHistory

PASSING_GRADE = Decimal("14")


@dataclass
class PeriodStat:
    period: str
    courses_taken: int
    courses_passed: int
    courses_failed: int
    pass_rate: Decimal
    weighted_average: Decimal


@dataclass
class AcademicAnalytics:
    period_stats: list[PeriodStat] = field(default_factory=list)
    total_courses: int = 0
    total_passed: int = 0
    total_failed: int = 0
    overall_pass_rate: Decimal = Decimal("0")
    retried_course_names: list[str] = field(default_factory=list)
    best_period: Optional[str] = None
    worst_period: Optional[str] = None


def compute(record: AcademicRecord) -> AcademicAnalytics:
    # Solo cursos con nota final y no deshabilitados entran a las estadísticas.
    graded = [
        c for c in record.courses
        if c.final_grade is not None and not c.is_disabled
    ]

    by_period: dict[str, list[CourseHistory]] = defaultdict(list)
    for c in graded:
        by_period[c.period].append(c)

    period_stats: list[PeriodStat] = []
    for period in sorted(by_period.keys()):
        courses = by_period[period]
        passed = [c for c in courses if c.final_grade >= PASSING_GRADE]
        failed = [c for c in courses if c.final_grade < PASSING_GRADE]
        total = len(courses)

        avg = (
            sum(c.final_grade for c in courses) / Decimal(total)
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        rate = (
            Decimal(len(passed)) / Decimal(total) * Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        period_stats.append(PeriodStat(
            period=period,
            courses_taken=total,
            courses_passed=len(passed),
            courses_failed=len(failed),
            pass_rate=rate,
            weighted_average=avg,
        ))

    total_courses = len(graded)
    total_passed = sum(1 for c in graded if c.final_grade >= PASSING_GRADE)
    total_failed = total_courses - total_passed

    overall_rate = (
        (Decimal(total_passed) / Decimal(total_courses) * Decimal("100"))
        .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if total_courses > 0
        else Decimal("0")
    )

    retried: list[str] = sorted({
        c.course_name for c in record.courses if c.attempt > 1
    })

    best = max(period_stats, key=lambda p: p.weighted_average, default=None)
    worst = min(period_stats, key=lambda p: p.weighted_average, default=None)

    return AcademicAnalytics(
        period_stats=period_stats,
        total_courses=total_courses,
        total_passed=total_passed,
        total_failed=total_failed,
        overall_pass_rate=overall_rate,
        retried_course_names=retried,
        best_period=best.period if best else None,
        worst_period=worst.period if worst else None,
    )
