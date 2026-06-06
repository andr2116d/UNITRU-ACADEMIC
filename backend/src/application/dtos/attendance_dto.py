from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SessionRecordDto:
    date: str
    day_name: str
    start_time: str
    end_time: str
    classroom: Optional[str]
    is_cancelled: bool
    attendance_status: str


@dataclass
class AttendanceSummaryDto:
    course_id: str
    course_name: str
    teacher: Optional[str]
    total_sessions: int
    attended: int
    absent: int
    justified: int
    attendance_percentage: str
    is_at_risk: bool
    sessions: List[SessionRecordDto] = field(default_factory=list)


@dataclass
class ScheduleSlotDto:
    day: str
    start_time: str
    end_time: str
    course_name: str
    classroom: Optional[str]
    teacher: Optional[str]
    group: Optional[str] = None
