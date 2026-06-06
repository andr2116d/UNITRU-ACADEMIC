from dataclasses import dataclass, field
from typing import List, Optional

from .academic_analytics_dto import AcademicAnalyticsDto
from .academic_record_dto import AcademicRecordDto
from .attendance_dto import AttendanceSummaryDto, ScheduleSlotDto
from .enrollment_dto import EnrollmentDto
from .grade_report_dto import GradeReportDto
from .optimized_schedule_dto import OptimizedScheduleDto
from .student_profile_dto import StudentProfileDto


@dataclass
class DashboardReportDto:
    grade_report: GradeReportDto
    student_profile: Optional[StudentProfileDto] = None
    academic_record: Optional[AcademicRecordDto] = None
    attendance: List[AttendanceSummaryDto] = field(default_factory=list)
    schedule: List[ScheduleSlotDto] = field(default_factory=list)
    enrollment: Optional[EnrollmentDto] = None
    optimized_schedules: List[OptimizedScheduleDto] = field(default_factory=list)
    analytics: Optional[AcademicAnalyticsDto] = None
