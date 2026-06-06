from decimal import Decimal
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect

from ...application.use_cases.authenticate_student_use_case import (
    AuthenticateStudentUseCase,
)
from ...application.use_cases.extract_full_dashboard_use_case import (
    ExtractFullDashboardUseCase,
)
from ...domain.exceptions.suv_errors import (
    AuthenticationError,
    CaptchaError,
    ExtractionError,
    NavigationError,
    SuvTimeoutError,
    SuvUnavailableError,
)
from ...infrastructure.playwright.session_manager import SessionManager
from .event_emitter import EventEmitter

_ERROR_MESSAGES = {
    CaptchaError: "No se pudo resolver el captcha. Intenta nuevamente.",
    AuthenticationError: "No se pudo iniciar sesión. Revisa tu usuario y contraseña.",
    NavigationError: "Hubo un problema navegando en el SUV. Intenta nuevamente.",
    ExtractionError: "No se pudieron extraer las notas. Intenta nuevamente.",
    SuvTimeoutError: "El SUV tardó demasiado en responder. Intenta más tarde.",
    SuvUnavailableError: "El SUV no está disponible en este momento.",
}


class WebSocketHandler:
    def __init__(
        self,
        session_manager: SessionManager,
        authenticate_use_case: AuthenticateStudentUseCase,
        dashboard_use_case: ExtractFullDashboardUseCase,
    ) -> None:
        self._session_manager = session_manager
        self._authenticate_use_case = authenticate_use_case
        self._dashboard_use_case = dashboard_use_case

    async def handle(self, websocket: WebSocket) -> None:
        await websocket.accept()
        emitter = EventEmitter(websocket)
        session = await self._session_manager.create_session()

        try:
            data = await websocket.receive_json()
            username: Optional[str] = data.get("username")
            password: Optional[str] = data.get("password")

            if not username or not password:
                await emitter.emit(
                    "error", {"message": "Faltan usuario o contraseña."}
                )
                return

            await self._authenticate_use_case.execute(
                username=username,
                password=password,
                session=session,
                emit=emitter.emit,
            )

            dashboard = await self._dashboard_use_case.execute(
                session=session,
                emit=emitter.emit,
            )

            await emitter.emit("dashboard_ready", self._serialize(dashboard))

        except WebSocketDisconnect:
            pass
        except Exception as exc:
            await self._emit_error(emitter, exc)
        finally:
            await self._session_manager.destroy_session(session.session_id)

    async def _emit_error(self, emitter: EventEmitter, exc: Exception) -> None:
        message = _ERROR_MESSAGES.get(
            type(exc), "Ocurrió un error inesperado. Intenta nuevamente."
        )
        try:
            await emitter.emit(
                "error", {"message": message, "category": type(exc).__name__}
            )
        except Exception:
            pass

    def _serialize(self, dto) -> dict:
        def grade(value: Optional[Decimal]) -> Optional[str]:
            return str(value) if value is not None else None

        def serialize_prediction(pred) -> Optional[dict]:
            if pred is None:
                return None
            return {
                "course_id": pred.course_id,
                "course_name": pred.course_name,
                "total_units": pred.total_units,
                "known": pred.known,
                "pending": pred.pending,
                "required_pending_sum": pred.required_pending_sum,
                "min_per_pending": pred.min_per_pending,
                "is_possible": pred.is_possible,
                "already_passes": pred.already_passes,
                "combinations": pred.combinations,
            }

        grades = {
            "period": dto.grade_report.period,
            "payment_order": dto.grade_report.payment_order,
            "enrollment_type": dto.grade_report.enrollment_type,
            "courses": [
                {
                    "course_id": c.course_id,
                    "course_name": c.course_name,
                    "attempt": c.attempt,
                    "u1": grade(c.u1),
                    "u2": grade(c.u2),
                    "u3": grade(c.u3),
                    "u4": grade(c.u4),
                    "u5": grade(c.u5),
                    "u6": grade(c.u6),
                    "sust": grade(c.sust),
                    "np": grade(c.np),
                    "apla": grade(c.apla),
                    "final_grade": grade(c.final_grade),
                    "inh": c.inh,
                    "average": grade(c.average),
                    "prediction": serialize_prediction(c.prediction),
                }
                for c in dto.grade_report.courses
            ],
        }

        profile = None
        if dto.student_profile:
            p = dto.student_profile
            profile = {
                "full_name": p.full_name,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "enrollment_number": p.enrollment_number,
                "faculty": p.faculty,
                "school": p.school,
                "campus": p.campus,
                "admission_year": p.admission_year,
                "institutional_email": p.institutional_email,
                "personal_email": p.personal_email,
                "phone": p.phone,
                "document": p.document,
                "birth_date": p.birth_date,
                "sex": p.sex,
                "marital_status": p.marital_status,
                "address": p.address,
                "curriculum": p.curriculum,
                "condition": p.condition,
                "photo_data_url": p.photo_data_url,
            }

        record = None
        if dto.academic_record:
            r = dto.academic_record
            record = {
                "student_name": r.student_name,
                "enrollment_number": r.enrollment_number,
                "condition": r.condition,
                "accumulated_credits": r.accumulated_credits,
                "weighted_average": r.weighted_average,
                "payment_status": r.payment_status,
                "payment_order": r.payment_order,
                "courses": [
                    {
                        "period": c.period,
                        "course_id": c.course_id,
                        "course_name": c.course_name,
                        "attempt": c.attempt,
                        "cycle": c.cycle,
                        "credits": c.credits,
                        "course_type": c.course_type,
                        "section": c.section,
                        "group": c.group,
                        "final_grade": c.final_grade,
                        "is_disabled": c.is_disabled,
                    }
                    for c in r.courses
                ],
            }

        attendance = [
            {
                "course_id": s.course_id,
                "course_name": s.course_name,
                "teacher": s.teacher,
                "total_sessions": s.total_sessions,
                "attended": s.attended,
                "absent": s.absent,
                "justified": s.justified,
                "attendance_percentage": s.attendance_percentage,
                "is_at_risk": s.is_at_risk,
            }
            for s in dto.attendance
        ]

        schedule = [
            {
                "day": sl.day,
                "start_time": sl.start_time,
                "end_time": sl.end_time,
                "course_name": sl.course_name,
                "classroom": sl.classroom,
                "teacher": sl.teacher,
                "group": sl.group,
            }
            for sl in dto.schedule
        ]

        enrollment = None
        if dto.enrollment:
            e = dto.enrollment
            enrollment = {
                "period": e.period,
                "total_credits": e.total_credits,
                "courses": [
                    {
                        "cycle": c.cycle,
                        "course_id": c.course_id,
                        "course_name": c.course_name,
                        "course_type": c.course_type,
                        "credits": c.credits,
                        "group": c.group,
                        "attempt": c.attempt,
                        "teacher": c.teacher,
                    }
                    for c in e.courses
                ],
            }

        optimized_schedules = [
            {
                "score": opt.score,
                "days": opt.days,
                "gap_minutes": opt.gap_minutes,
                "extreme_sessions": opt.extreme_sessions,
                "selections": [
                    {
                        "course": sel.course,
                        "cycle": sel.cycle,
                        "section": sel.section,
                        "subgroup": sel.subgroup,
                    }
                    for sel in opt.selections
                ],
                "sessions": [
                    {
                        "course": s.course,
                        "tipo": s.tipo,
                        "day": s.day,
                        "start_time": s.start_time,
                        "end_time": s.end_time,
                        "room": s.room,
                        "subgroup": s.subgroup,
                        "teacher": s.teacher,
                        "section": s.section,
                    }
                    for s in opt.sessions
                ],
            }
            for opt in dto.optimized_schedules
        ]

        analytics = None
        if dto.analytics:
            a = dto.analytics
            analytics = {
                "period_stats": [
                    {
                        "period": p.period,
                        "courses_taken": p.courses_taken,
                        "courses_passed": p.courses_passed,
                        "courses_failed": p.courses_failed,
                        "pass_rate": p.pass_rate,
                        "weighted_average": p.weighted_average,
                    }
                    for p in a.period_stats
                ],
                "total_courses": a.total_courses,
                "total_passed": a.total_passed,
                "total_failed": a.total_failed,
                "overall_pass_rate": a.overall_pass_rate,
                "retried_course_names": a.retried_course_names,
                "best_period": a.best_period,
                "worst_period": a.worst_period,
            }

        return {
            "grade_report": grades,
            "student_profile": profile,
            "academic_record": record,
            "attendance": attendance,
            "schedule": schedule,
            "enrollment": enrollment,
            "optimized_schedules": optimized_schedules,
            "analytics": analytics,
        }
