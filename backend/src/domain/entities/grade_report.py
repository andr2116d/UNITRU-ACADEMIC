from dataclasses import dataclass, field
from typing import List, Optional

from .course import Course


@dataclass
class GradeReport:
    period: Optional[str] = None
    payment_order: Optional[str] = None
    enrollment_type: Optional[str] = None
    courses: List[Course] = field(default_factory=list)
