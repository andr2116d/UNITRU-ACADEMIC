from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EnrolledCourseDto:
    cycle: str
    course_id: str
    course_name: str
    course_type: str
    credits: int
    group: str
    attempt: int
    teacher: Optional[str]


@dataclass
class EnrollmentDto:
    period: str
    courses: List[EnrolledCourseDto] = field(default_factory=list)
    total_credits: int = 0
