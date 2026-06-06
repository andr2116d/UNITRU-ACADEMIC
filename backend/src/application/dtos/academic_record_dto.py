from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CourseHistoryDto:
    period: str
    course_id: str
    course_name: str
    attempt: int
    cycle: int
    credits: int
    course_type: str
    section: Optional[str]
    group: Optional[str]
    final_grade: Optional[str]
    is_disabled: bool


@dataclass
class AcademicRecordDto:
    student_name: str
    enrollment_number: str
    condition: str
    accumulated_credits: int
    weighted_average: str
    payment_status: Optional[str]
    payment_order: Optional[str]
    courses: List[CourseHistoryDto] = field(default_factory=list)
