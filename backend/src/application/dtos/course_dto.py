from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from .course_prediction_dto import CoursePredictionDto


@dataclass
class CourseDto:
    course_id: str
    course_name: str
    attempt: int
    u1: Optional[Decimal]
    u2: Optional[Decimal]
    u3: Optional[Decimal]
    u4: Optional[Decimal]
    u5: Optional[Decimal]
    u6: Optional[Decimal]
    sust: Optional[Decimal]
    np: Optional[Decimal]
    apla: Optional[Decimal]
    final_grade: Optional[Decimal]
    inh: bool
    # Promedio de las unidades publicadas (parcial mientras el ciclo va en curso).
    average: Optional[Decimal] = None
    prediction: Optional[CoursePredictionDto] = None
