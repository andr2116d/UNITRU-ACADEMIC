from collections import defaultdict
from datetime import date as Date
from decimal import Decimal
from typing import Dict, List, Optional

from ..entities.attendance import (
    AttendanceSummary,
    CourseAttendance,
    ScheduleSlot,
    SessionRecord,
)
from ..entities.enrollment import Enrollment


_DIAS_ES = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}

_PRESENTE = ("P", "PRESENTE", "A")
_JUSTIFICADO = ("J", "JUSTIFICADO", "JU")


def day_name_from_date(fecha: str) -> str:
    # El SUV entrega las fechas como DD-MM-YYYY (formato peruano); también
    # toleramos YYYY-MM-DD por si alguna pantalla lo invierte.
    try:
        parts = fecha.replace("/", "-").split("-")
        if len(parts) != 3:
            return ""
        if len(parts[0]) == 4:
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        return _DIAS_ES.get(Date(year, month, day).weekday(), "")
    except (ValueError, TypeError):
        return ""


def build_summaries(courses: List[CourseAttendance]) -> List[AttendanceSummary]:
    # Un mismo curso puede tener un tracker vacío (sin sesiones) además del real;
    # lo omitimos para no ensuciar la lista de asistencia con un "100% (0 ses)".
    return [_build_summary(c) for c in courses if c.sessions]


def _is_present(session: SessionRecord) -> bool:
    if session.is_cancelled:
        return False
    status = session.attendance_status.upper()
    return status in _PRESENTE or status in _JUSTIFICADO


def _turn_sessions(sessions: List[SessionRecord]) -> List[SessionRecord]:
    # El turno real del alumno son los bloques (día, hora) donde tiene
    # asistencia registrada; el SUV mete en un mismo tracker sesiones de otros
    # grupos (todas 'S/A'). Si ningún bloque tiene asistencia, no podemos
    # distinguir el turno y devolvemos todo (curso de un solo turno o sin ir).
    blocks: Dict[tuple, List[SessionRecord]] = defaultdict(list)
    for s in sessions:
        blocks[(s.day_name, s.start_time, s.end_time)].append(s)

    turn_keys = {key for key, group in blocks.items() if any(_is_present(s) for s in group)}
    if not turn_keys:
        return sessions
    return [
        s for s in sessions
        if (s.day_name, s.start_time, s.end_time) in turn_keys
    ]


def _build_summary(course: CourseAttendance) -> AttendanceSummary:
    # Solo contamos el turno real del alumno (descarta los bloques de otros
    # grupos que el SUV mezcla en el mismo tracker).
    sessions = _turn_sessions(course.sessions)

    active = [s for s in sessions if not s.is_cancelled]
    total = len(active)

    attended = sum(1 for s in active if s.attendance_status.upper() in _PRESENTE)
    justified = sum(1 for s in active if s.attendance_status.upper() in _JUSTIFICADO)
    absent = total - attended - justified

    if total > 0:
        percentage = Decimal(str(round((attended + justified) / total * 100, 2)))
    else:
        percentage = Decimal("100")

    # Alerta cuando le quedan ≤ 10% de faltas antes del límite de inhabilitación (30%).
    risk_threshold = total * 0.30
    remaining = risk_threshold - absent
    is_at_risk = total > 0 and remaining <= (total * 0.10)

    return AttendanceSummary(
        course_id=course.course_id,
        course_name=course.course_name,
        teacher=None,
        total_sessions=total,
        attended=attended,
        absent=absent,
        justified=justified,
        attendance_percentage=percentage,
        is_at_risk=is_at_risk,
        sessions=sessions,
    )


def build_schedule(
    summaries: List[AttendanceSummary],
    enrollment: Optional[Enrollment] = None,
) -> List[ScheduleSlot]:
    seen: Dict[tuple, bool] = {}
    slots: List[ScheduleSlot] = []
    day_order = list(_DIAS_ES.values())

    for summary in summaries:
        for session in summary.sessions:
            if session.is_cancelled or not session.day_name:
                continue
            key = (
                session.day_name,
                session.start_time,
                session.end_time,
                summary.course_name,
            )
            if key in seen:
                continue
            seen[key] = True
            slots.append(
                ScheduleSlot(
                    day=session.day_name,
                    start_time=session.start_time,
                    end_time=session.end_time,
                    course_name=summary.course_name,
                    classroom=session.classroom,
                    teacher=summary.teacher,
                )
            )

    if enrollment:
        _enrich_with_enrollment(slots, enrollment)

    slots.sort(
        key=lambda s: (
            day_order.index(s.day) if s.day in day_order else 99,
            s.start_time,
        )
    )
    return slots


def _enrich_with_enrollment(slots: List[ScheduleSlot], enrollment: Enrollment) -> None:
    # El día/hora del horario salen de la asistencia real; la Ficha aporta el
    # grupo y el docente. Cruzamos por nombre de curso porque los IDs de
    # asistencia (trackers) no coinciden con los de la matrícula.
    by_name = {_normalize(c.course_name): c for c in enrollment.courses}
    for slot in slots:
        course = by_name.get(_normalize(slot.course_name))
        if course:
            slot.group = course.group
            if course.teacher:
                slot.teacher = course.teacher


def _normalize(name: str) -> str:
    return " ".join(name.upper().split())
