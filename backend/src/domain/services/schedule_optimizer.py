from collections import defaultdict
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..entities.optimized_schedule import CourseSelection, OptimizedSchedule
from ..entities.schedule_catalog import CatalogSession, ScheduleCatalog


@dataclass
class OptimizerWeights:
    # Penalizaciones (menor puntaje total = mejor horario).
    gap_per_hour: float = 1.0      # horas libres entre clases el mismo día
    per_day: float = 3.0           # cada día que hay que ir al campus
    per_extreme: float = 2.0       # clases muy temprano / muy tarde

    early_before_min: int = 8 * 60     # antes de 08:00
    late_after_min: int = 19 * 60      # después de 19:00


def optimize(
    course_names: List[str],
    catalog: ScheduleCatalog,
    top_n: int = 5,
    weights: Optional[OptimizerWeights] = None,
) -> Tuple[List[OptimizedSchedule], List[str]]:
    weights = weights or OptimizerWeights()

    courses: List[Tuple[str, List[CourseSelection]]] = []
    missing: List[str] = []
    for name in course_names:
        sessions = catalog.for_course(name)
        if not sessions:
            missing.append(name)
            continue
        courses.append((name, _candidates(name, sessions)))

    results: List[OptimizedSchedule] = []
    chosen: List[CourseSelection] = []

    def backtrack(index: int, taken: List[CatalogSession]) -> None:
        if index == len(courses):
            if chosen:
                results.append(_score(list(chosen), weights))
            return
        for candidate in courses[index][1]:
            if any(_overlap(s, t) for s in candidate.sessions for t in taken):
                continue
            chosen.append(candidate)
            backtrack(index + 1, taken + candidate.sessions)
            chosen.pop()

    backtrack(0, [])
    results.sort(key=lambda r: r.score)
    return _dedupe(results)[:top_n], missing


def _candidates(course: str, sessions: List[CatalogSession]) -> List[CourseSelection]:
    # Una opción por (sección × sub-grupo de laboratorio). Las sesiones sin
    # sub-grupo (teoría/práctica común) van siempre; de las que sí tienen
    # sub-grupo (G1/G2/G3) se elige una.
    by_section = defaultdict(list)
    for s in sessions:
        by_section[(s.cycle, s.section)].append(s)

    candidates: List[CourseSelection] = []
    for (cycle, section), group in by_section.items():
        fixed = [s for s in group if not s.subgroup]
        subgroups = defaultdict(list)
        for s in group:
            if s.subgroup:
                subgroups[s.subgroup].append(s)
        if not subgroups:
            candidates.append(CourseSelection(course, cycle, section, None, fixed))
        else:
            for label, sub_sessions in subgroups.items():
                candidates.append(
                    CourseSelection(course, cycle, section, label, fixed + sub_sessions)
                )
    return candidates


def _overlap(a: CatalogSession, b: CatalogSession) -> bool:
    return a.day == b.day and a.start_min < b.end_min and b.start_min < a.end_min


def _score(selections: List[CourseSelection], weights: OptimizerWeights) -> OptimizedSchedule:
    sessions = [s for sel in selections for s in sel.sessions]

    by_day = defaultdict(list)
    for s in sessions:
        by_day[s.day].append(s)

    gap_minutes = 0
    for day_sessions in by_day.values():
        ordered = sorted(day_sessions, key=lambda s: s.start_min)
        for prev, nxt in zip(ordered, ordered[1:]):
            gap_minutes += max(0, nxt.start_min - prev.end_min)

    days = len(by_day)
    extremes = sum(
        1 for s in sessions
        if s.start_min < weights.early_before_min or s.end_min > weights.late_after_min
    )

    score = (
        (gap_minutes / 60) * weights.gap_per_hour
        + days * weights.per_day
        + extremes * weights.per_extreme
    )
    return OptimizedSchedule(
        selections=selections,
        score=round(score, 2),
        gap_minutes=gap_minutes,
        days=days,
        extreme_sessions=extremes,
    )


def _dedupe(results: List[OptimizedSchedule]) -> List[OptimizedSchedule]:
    # Distintos sub-grupos pueden dar exactamente el mismo puntaje y disposición;
    # nos quedamos con horarios visualmente distintos (por sus bloques).
    seen = set()
    unique = []
    for r in results:
        key = tuple(sorted((s.day, s.start_min, s.end_min, s.course) for s in r.sessions))
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    return unique
