from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional


@dataclass
class CourseHistory:
    period: str
    course_id: str
    course_name: str
    attempt: int
    cycle: int
    credits: int
    course_type: str
    section: Optional[str]
    group: Optional[str]
    final_grade: Optional[Decimal]
    is_disabled: bool


@dataclass
class AcademicRecord:
    student_name: str
    enrollment_number: str
    condition: str
    accumulated_credits: int
    weighted_average: Decimal
    payment_status: Optional[str]
    payment_order: Optional[str]
    courses: List[CourseHistory] = field(default_factory=list)
