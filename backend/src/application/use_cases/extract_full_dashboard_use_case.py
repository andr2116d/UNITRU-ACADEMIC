import logging
from typing import Awaitable, Callable, List, Optional

from ...domain.entities.attendance import AttendanceSummary, ScheduleSlot
from ...domain.entities.browser_session import BrowserSession
from ...domain.entities.dashboard_report import DashboardReport
from ...domain.services import (
    academic_analytics,
    grade_analytics,
    grade_predictor,
    schedule_builder,
    schedule_optimizer,
)
from ..dtos.academic_analytics_dto import AcademicAnalyticsDto, PeriodStatDto
from ..dtos.academic_record_dto import AcademicRecordDto, CourseHistoryDto
from ..dtos.attendance_dto import AttendanceSummaryDto, ScheduleSlotDto, SessionRecordDto
from ..dtos.course_dto import CourseDto
from ..dtos.course_prediction_dto import CoursePredictionDto
from ..dtos.dashboard_report_dto import DashboardReportDto
from ..dtos.enrollment_dto import EnrolledCourseDto, EnrollmentDto
from ..dtos.grade_report_dto import GradeReportDto
from ..dtos.optimized_schedule_dto import (
    OptimizedScheduleDto,
    OptimizedSelectionDto,
    OptimizedSessionDto,
)
from ..dtos.student_profile_dto import StudentProfileDto
from ..ports.schedule_catalog_port import ScheduleCatalogPort
from ..ports.suv_attendance_extraction_port import SuvAttendanceExtractionPort
from ..ports.suv_enrollment_extraction_port import SuvEnrollmentExtractionPort
from ..ports.suv_grade_extraction_port import SuvGradeExtractionPort
from ..ports.suv_navigation_port import SuvNavigationPort
from ..ports.suv_profile_extraction_port import SuvProfileExtractionPort
from ..ports.suv_record_extraction_port import SuvRecordExtractionPort

EventEmitter = Callable[[str, dict], Awaitable[None]]
_log = logging.getLogger(__name__)


class ExtractFullDashboardUseCase:
    """Orquesta los cuatro extractores en secuencia.

    Si un extractor no-grades falla, continúa con el siguiente y deja el
    campo en None. Si grades falla, propaga la excepción.
    """

    def __init__(
        self,
        profile_port: SuvProfileExtractionPort,
        record_port: SuvRecordExtractionPort,
        attendance_port: SuvAttendanceExtractionPort,
        enrollment_port: SuvEnrollmentExtractionPort,
        grades_port: SuvGradeExtractionPort,
        navigation_port: SuvNavigationPort,
        catalog_port: Optional[ScheduleCatalogPort] = None,
    ) -> None:
        self._profile_port = profile_port
        self._record_port = record_port
        self._attendance_port = attendance_port
        self._enrollment_port = enrollment_port
        self._grades_port = grades_port
        self._navigation_port = navigation_port
        self._catalog_port = catalog_port

    async def execute(
        self,
        session: BrowserSession,
        emit: EventEmitter,
    ) -> DashboardReportDto:
        # 1. Perfil
        await emit("extracting_profile", {})
        profile_dto: Optional[StudentProfileDto] = None
        try:
            profile = await self._profile_port.extract_student_profile(session)
            profile_dto = self._map_profile(profile)
            await emit("profile_extraction_success", {})
        except Exception as exc:
            _log.warning("Perfil no disponible: %s", exc)
            await emit("profile_extraction_failed", {"reason": str(exc)})

        # 2. Record académico
        await emit("extracting_record", {})
        record_dto: Optional[AcademicRecordDto] = None
        analytics_dto: Optional[AcademicAnalyticsDto] = None
        try:
            record = await self._record_port.extract_academic_record(session)
            record_dto = self._map_record(record)
            analytics_domain = academic_analytics.compute(record)
            analytics_dto = self._map_analytics(analytics_domain)
            await emit("record_extraction_success", {})
        except Exception as exc:
            _log.warning("Record no disponible: %s", exc)
            await emit("record_extraction_failed", {"reason": str(exc)})

        # 3. Matrícula (Ficha) — grupo y docente autoritativos por curso
        await emit("extracting_enrollment", {})
        enrollment = None
        enrollment_dto: Optional[EnrollmentDto] = None
        try:
            enrollment = await self._enrollment_port.extract_enrollment(session)
            enrollment_dto = self._map_enrollment(enrollment)
            await emit(
                "enrollment_extraction_success",
                {"course_count": len(enrollment.courses)},
            )
        except Exception as exc:
            _log.warning("Matrícula no disponible: %s", exc)
            await emit("enrollment_extraction_failed", {"reason": str(exc)})

        # 4. Asistencia + horario (el horario se enriquece con el grupo de la Ficha)
        await emit("extracting_attendance", {})
        attendance_dtos: List[AttendanceSummaryDto] = []
        schedule_dtos: List[ScheduleSlotDto] = []
        try:
            courses = await self._attendance_port.extract_attendance(session)
            summaries = schedule_builder.build_summaries(courses)
            slots = schedule_builder.build_schedule(summaries, enrollment)
            attendance_dtos = [self._map_attendance(s) for s in summaries]
            schedule_dtos = [self._map_slot(sl) for sl in slots]
            await emit("attendance_extraction_success", {"course_count": len(summaries)})
        except Exception as exc:
            _log.warning("Asistencia no disponible: %s", exc)
            await emit("attendance_extraction_failed", {"reason": str(exc)})

        # 5. Notas — obligatorio; si falla se propaga
        await emit("extracting_grades", {})
        await self._navigation_port.navigate_to_grades(session)
        await self._navigation_port.click_ver(session)
        grade_report = await self._grades_port.extract_grade_report(session)
        grades_dto = self._map_grades(grade_report)
        await emit("grade_extraction_success", {"course_count": len(grades_dto.courses)})

        # 6. Mejor horario — combina secciones del catálogo (no fatal)
        optimized_dtos: List[OptimizedScheduleDto] = []
        if self._catalog_port and enrollment and enrollment.courses:
            try:
                await emit("optimizing_schedule", {})
                catalog = self._catalog_port.load()
                course_names = [c.course_name for c in enrollment.courses]
                schedules, _missing = schedule_optimizer.optimize(
                    course_names, catalog, top_n=3
                )
                optimized_dtos = [self._map_optimized(s) for s in schedules]
                await emit("schedule_optimized", {"options": len(optimized_dtos)})
            except Exception as exc:
                _log.warning("Optimización de horario no disponible: %s", exc)
                await emit("schedule_optimization_failed", {"reason": str(exc)})

        session.touch()
        return DashboardReportDto(
            grade_report=grades_dto,
            student_profile=profile_dto,
            academic_record=record_dto,
            attendance=attendance_dtos,
            schedule=schedule_dtos,
            enrollment=enrollment_dto,
            optimized_schedules=optimized_dtos,
            analytics=analytics_dto,
        )

    def _map_profile(self, profile) -> StudentProfileDto:
        return StudentProfileDto(
            full_name=profile.full_name,
            first_name=profile.first_name,
            last_name=profile.last_name,
            enrollment_number=profile.enrollment_number,
            faculty=profile.faculty,
            school=profile.school,
            campus=profile.campus,
            admission_year=profile.admission_year,
            institutional_email=profile.institutional_email,
            personal_email=profile.personal_email,
            phone=profile.phone,
            document=profile.document,
            birth_date=profile.birth_date,
            sex=profile.sex,
            marital_status=profile.marital_status,
            address=profile.address,
            curriculum=profile.curriculum,
            condition=profile.condition,
            photo_data_url=profile.photo_data_url,
        )

    def _map_record(self, record) -> AcademicRecordDto:
        courses = [
            CourseHistoryDto(
                period=c.period,
                course_id=c.course_id,
                course_name=c.course_name,
                attempt=c.attempt,
                cycle=c.cycle,
                credits=c.credits,
                course_type=c.course_type,
                section=c.section,
                group=c.group,
                final_grade=str(c.final_grade) if c.final_grade is not None else None,
                is_disabled=c.is_disabled,
            )
            for c in record.courses
        ]
        return AcademicRecordDto(
            student_name=record.student_name,
            enrollment_number=record.enrollment_number,
            condition=record.condition,
            accumulated_credits=record.accumulated_credits,
            weighted_average=str(record.weighted_average),
            payment_status=record.payment_status,
            payment_order=record.payment_order,
            courses=courses,
        )

    def _map_attendance(self, summary: AttendanceSummary) -> AttendanceSummaryDto:
        sessions = [
            SessionRecordDto(
                date=s.date,
                day_name=s.day_name,
                start_time=s.start_time,
                end_time=s.end_time,
                classroom=s.classroom,
                is_cancelled=s.is_cancelled,
                attendance_status=s.attendance_status,
            )
            for s in summary.sessions
        ]
        return AttendanceSummaryDto(
            course_id=summary.course_id,
            course_name=summary.course_name,
            teacher=summary.teacher,
            total_sessions=summary.total_sessions,
            attended=summary.attended,
            absent=summary.absent,
            justified=summary.justified,
            attendance_percentage=str(summary.attendance_percentage),
            is_at_risk=summary.is_at_risk,
            sessions=sessions,
        )

    def _map_slot(self, slot: ScheduleSlot) -> ScheduleSlotDto:
        return ScheduleSlotDto(
            day=slot.day,
            start_time=slot.start_time,
            end_time=slot.end_time,
            course_name=slot.course_name,
            classroom=slot.classroom,
            teacher=slot.teacher,
            group=slot.group,
        )

    def _map_optimized(self, schedule) -> OptimizedScheduleDto:
        def hhmm(total_min: int) -> str:
            return f"{total_min // 60:02d}:{total_min % 60:02d}"

        return OptimizedScheduleDto(
            score=schedule.score,
            days=schedule.days,
            gap_minutes=schedule.gap_minutes,
            extreme_sessions=schedule.extreme_sessions,
            selections=[
                OptimizedSelectionDto(
                    course=sel.course,
                    cycle=sel.cycle,
                    section=sel.section,
                    subgroup=sel.subgroup,
                )
                for sel in schedule.selections
            ],
            sessions=[
                OptimizedSessionDto(
                    course=s.course,
                    tipo=s.tipo,
                    day=s.day,
                    start_time=hhmm(s.start_min),
                    end_time=hhmm(s.end_min),
                    room=s.room,
                    subgroup=s.subgroup,
                    teacher=s.teacher,
                    section=s.section,
                )
                for s in schedule.sessions
            ],
        )

    def _map_enrollment(self, enrollment) -> EnrollmentDto:
        return EnrollmentDto(
            period=enrollment.period,
            total_credits=enrollment.total_credits,
            courses=[
                EnrolledCourseDto(
                    cycle=c.cycle,
                    course_id=c.course_id,
                    course_name=c.course_name,
                    course_type=c.course_type,
                    credits=c.credits,
                    group=c.group,
                    attempt=c.attempt,
                    teacher=c.teacher,
                )
                for c in enrollment.courses
            ],
        )

    def _map_grades(self, grade_report) -> GradeReportDto:
        courses = [
            CourseDto(
                course_id=c.course_id,
                course_name=c.course_name,
                attempt=c.attempt,
                u1=c.u1,
                u2=c.u2,
                u3=c.u3,
                u4=c.u4,
                u5=c.u5,
                u6=c.u6,
                sust=c.sust,
                np=c.np,
                apla=c.apla,
                final_grade=c.final_grade,
                inh=c.inh,
                average=grade_analytics.course_average(c),
                prediction=self._map_prediction(grade_predictor.predict_course(c)),
            )
            for c in grade_report.courses
        ]
        return GradeReportDto(
            period=grade_report.period,
            payment_order=grade_report.payment_order,
            enrollment_type=grade_report.enrollment_type,
            courses=courses,
        )

    def _map_prediction(self, pred) -> Optional[CoursePredictionDto]:
        if pred is None:
            return None
        return CoursePredictionDto(
            course_id=pred.course_id,
            course_name=pred.course_name,
            total_units=pred.total_units,
            known={k: str(v) for k, v in pred.known.items()},
            pending=pred.pending,
            required_pending_sum=str(pred.required_pending_sum),
            min_per_pending=str(pred.min_per_pending),
            is_possible=pred.is_possible,
            already_passes=pred.already_passes,
            combinations=pred.combinations,
        )

    def _map_analytics(self, analytics) -> AcademicAnalyticsDto:
        return AcademicAnalyticsDto(
            period_stats=[
                PeriodStatDto(
                    period=p.period,
                    courses_taken=p.courses_taken,
                    courses_passed=p.courses_passed,
                    courses_failed=p.courses_failed,
                    pass_rate=str(p.pass_rate),
                    weighted_average=str(p.weighted_average),
                )
                for p in analytics.period_stats
            ],
            total_courses=analytics.total_courses,
            total_passed=analytics.total_passed,
            total_failed=analytics.total_failed,
            overall_pass_rate=str(analytics.overall_pass_rate),
            retried_course_names=analytics.retried_course_names,
            best_period=analytics.best_period,
            worst_period=analytics.worst_period,
        )
