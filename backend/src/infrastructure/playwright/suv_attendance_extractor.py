from typing import List

from ...application.ports.suv_attendance_extraction_port import SuvAttendanceExtractionPort
from ...domain.entities.attendance import CourseAttendance, SessionRecord
from ...domain.entities.browser_session import BrowserSession
from ...domain.services import schedule_builder
from . import sidebar_navigation

# Selectores verificados.
# El enlace real es option=reportes (module=asistencia), no reporteAsistencia.
ASISTENCIA_SUBMENU = "Asistencia"
REPORTES_LINK = 'a[href*="module=asistencia&option=reportes"]'
CURSO_SELECT = "#curso"
TABLA_ASISTENCIA = "#tablaAsistencia"
TABLA_ROW = "#tablaAsistencia tr td"


class SuvAttendanceExtractor(SuvAttendanceExtractionPort):
    async def extract_attendance(
        self, session: BrowserSession
    ) -> List[CourseAttendance]:
        page = session.page

        await self._navigate(session)

        # Obtener todos los cursos disponibles en el select
        options = await page.query_selector_all(f"{CURSO_SELECT} option")
        courses: List[CourseAttendance] = []

        for option in options:
            course_id = await option.get_attribute("value")
            course_name = (await option.inner_text()).strip()
            if not course_id:
                continue

            sessions = await self._extract_course_sessions(session, course_id)
            courses.append(
                CourseAttendance(
                    course_id=course_id,
                    course_name=course_name,
                    sessions=sessions,
                )
            )

        return courses

    async def _navigate(self, session: BrowserSession) -> None:
        page = session.page
        await sidebar_navigation.dismiss_modal(session)
        await sidebar_navigation.ensure_sidebar_open(session)
        await sidebar_navigation.expand_submenu(session, ASISTENCIA_SUBMENU)
        await sidebar_navigation.click_menu_link(session, REPORTES_LINK)

        # cargarPeriodoActual2() + cargarCursosMatriculados() llenan el select.
        # Las <option> nunca están "visibles" (viven dentro del select colapsado),
        # por eso esperamos a que estén en el DOM (attached), no visibles.
        await page.wait_for_selector(
            f"{CURSO_SELECT} option", state="attached", timeout=20_000
        )

    async def _extract_course_sessions(
        self, session: BrowserSession, course_id: str
    ) -> List[SessionRecord]:
        page = session.page

        # Seleccionar el curso y esperar que la tabla se actualice
        await page.select_option(CURSO_SELECT, value=course_id)
        try:
            await page.wait_for_selector(TABLA_ROW, timeout=10_000)
        except Exception:
            return []

        rows = await page.query_selector_all(f"{TABLA_ASISTENCIA} tr")
        sessions: List[SessionRecord] = []

        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) < 4:
                continue

            fecha = (await cells[0].inner_text()).strip()
            hora_inicio = (await cells[1].inner_text()).strip()
            hora_fin = (await cells[2].inner_text()).strip()
            estado = (await cells[3].inner_text()).strip()

            if not fecha or not hora_inicio:
                continue

            day_name = schedule_builder.day_name_from_date(fecha)
            is_cancelled = "anulad" in estado.lower()

            sessions.append(
                SessionRecord(
                    date=fecha,
                    day_name=day_name,
                    start_time=hora_inicio,
                    end_time=hora_fin,
                    classroom=None,
                    is_cancelled=is_cancelled,
                    attendance_status=estado,
                )
            )

        return sessions
