from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from itertools import product
from typing import Optional

from ..entities.course import Course

PASSING_GRADE = Decimal("14")
_UNITS = ("u1", "u2", "u3")


@dataclass
class CoursePrediction:
    course_id: str
    course_name: str
    total_units: int
    known: dict[str, Decimal]
    pending: list[str]
    required_pending_sum: Decimal
    min_per_pending: Decimal
    is_possible: bool
    already_passes: bool
    combinations: list[dict[str, int]] = field(default_factory=list)


def _rounded_average(values: list[Decimal]) -> Decimal:
    raw = sum(values) / Decimal(len(values))
    return raw.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def predict_course(course: Course) -> Optional[CoursePrediction]:
    # No tiene sentido predecir cursos ya cerrados o inhibidos.
    if course.final_grade is not None or course.inh:
        return None

    known: dict[str, Decimal] = {
        k: getattr(course, k)
        for k in _UNITS
        if getattr(course, k) is not None
    }
    pending: list[str] = [k for k in _UNITS if getattr(course, k) is None]
    total = len(_UNITS)

    known_sum = sum(known.values(), Decimal("0"))

    # Un promedio pasa si al redondear al entero más cercano (ROUND_HALF_UP) resulta >= 14.
    # Equivalente: promedio crudo >= 13.5.
    threshold_sum = Decimal("13.5") * total
    required = max(Decimal("0"), threshold_sum - known_sum)

    already_passes = False
    if not pending:
        already_passes = _rounded_average(list(known.values())) >= PASSING_GRADE
        return CoursePrediction(
            course_id=course.course_id,
            course_name=course.course_name,
            total_units=total,
            known=known,
            pending=[],
            required_pending_sum=Decimal("0"),
            min_per_pending=Decimal("0"),
            is_possible=already_passes,
            already_passes=already_passes,
            combinations=[],
        )

    # ¿Es posible llegar a 14 aunque las pendientes sean todas 20?
    max_possible_sum = known_sum + Decimal(len(pending)) * Decimal("20")
    is_possible = _rounded_average(
        list(known.values()) + [Decimal("20")] * len(pending)
    ) >= PASSING_GRADE

    # Mínimo por unidad si todas las pendientes obtienen la misma nota.
    # Buscamos el menor entero x tal que el promedio de (known + [x]*pending) >= 14.
    min_per = Decimal("20")
    if is_possible:
        for x in range(21):
            all_units = list(known.values()) + [Decimal(x)] * len(pending)
            if _rounded_average(all_units) >= PASSING_GRADE:
                min_per = Decimal(x)
                break

    # Todas las combinaciones enteras (0-20) que resultan en promedio >= 14.
    combinations: list[dict[str, int]] = []
    for values in product(range(21), repeat=len(pending)):
        all_units = list(known.values()) + [Decimal(v) for v in values]
        if _rounded_average(all_units) >= PASSING_GRADE:
            combinations.append(dict(zip(pending, values)))

    return CoursePrediction(
        course_id=course.course_id,
        course_name=course.course_name,
        total_units=total,
        known=known,
        pending=pending,
        required_pending_sum=required.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        min_per_pending=min_per,
        is_possible=is_possible,
        already_passes=False,
        combinations=combinations,
    )
