from dataclasses import dataclass, field
from typing import List, Optional

from .academic_record import AcademicRecord
from .attendance import AttendanceSummary, ScheduleSlot
from .enrollment import Enrollment
from .grade_report import GradeReport
from .student_profile import StudentProfile


@dataclass
class DashboardReport:
    grade_report: GradeReport
    student_profile: Optional[StudentProfile] = None
    academic_record: Optional[AcademicRecord] = None
    attendance: List[AttendanceSummary] = field(default_factory=list)
    schedule: List[ScheduleSlot] = field(default_factory=list)
    enrollment: Optional[Enrollment] = None
