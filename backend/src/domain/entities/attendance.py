from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional


@dataclass
class SessionRecord:
    date: str
    day_name: str
    start_time: str
    end_time: str
    classroom: Optional[str]
    is_cancelled: bool
    attendance_status: str


@dataclass
class AttendanceSummary:
    course_id: str
    course_name: str
    teacher: Optional[str]
    total_sessions: int
    attended: int
    absent: int
    justified: int
    attendance_percentage: Decimal
    is_at_risk: bool
    sessions: List[SessionRecord] = field(default_factory=list)


@dataclass
class CourseAttendance:
    """Sesiones crudas de un curso tal como las extrae el adaptador, antes de
    calcular resumen/horario. El cálculo vive en domain/services/schedule_builder."""

    course_id: str
    course_name: str
    sessions: List[SessionRecord] = field(default_factory=list)


@dataclass
class ScheduleSlot:
    day: str
    start_time: str
    end_time: str
    course_name: str
    classroom: Optional[str]
    teacher: Optional[str]
    # Grupo/docente provienen de la Ficha de Matrícula (cruce por nombre de
    # curso); el día/hora siguen viniendo de la asistencia real del alumno.
    group: Optional[str] = None
