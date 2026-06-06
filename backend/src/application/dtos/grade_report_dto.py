from dataclasses import dataclass, field
from typing import List, Optional

from .course_dto import CourseDto


@dataclass
class GradeReportDto:
    period: Optional[str]
    payment_order: Optional[str]
    enrollment_type: Optional[str]
    courses: List[CourseDto] = field(default_factory=list)
