from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from ..entities.course import Course


def course_average(course: Course) -> Optional[Decimal]:
    units = [u for u in (course.u1, course.u2, course.u3) if u is not None]
    if not units:
        return None
    average = sum(units) / Decimal(len(units))
    return average.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
