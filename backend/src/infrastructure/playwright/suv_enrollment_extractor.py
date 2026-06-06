from typing import List, Optional

from ...application.ports.suv_enrollment_extraction_port import SuvEnrollmentExtractionPort
from ...domain.entities.browser_session import BrowserSession
from ...domain.entities.enrollment import EnrolledCourse, Enrollment
from . import sidebar_navigation

# Selectores verificados en vivo contra el SUV (Ficha de Matrícula).
# El enlace real es option=fichaMat (module=historiales).
HISTORIALES_SUBMENU = "Historiales"
FICHA_LINK = 'a[href*="option=fichaMat"]'
PERIODO_SELECT = "#btnPeriodoMat"
CURSOS_TABLE = "#dtCursosMatriculados"
CURSOS_ROW = "#dtCursosMatriculados tbody tr td"

# Orden de columnas verificado: CICLO, ID CURSO, NOMBRE, TIPO, CRÉDITOS,
# GRUPO, VEZ, DOCENTE.
_COL_CYCLE = 0
_COL_ID = 1
_COL_NAME = 2
_COL_TYPE = 3
_COL_CREDITS = 4
_COL_GROUP = 5
_COL_ATTEMPT = 6
_COL_TEACHER = 7


class SuvEnrollmentExtractor(SuvEnrollmentExtractionPort):
    async def extract_enrollment(self, session: BrowserSession) -> Enrollment:
        page = session.page

        await self._navigate(session)

        period = await self._select_latest_period(session)
        if period is None:
            return Enrollment(period="", courses=[], total_credits=0)

        # La tabla solo se llena tras elegir período; si el período no tiene
        # matrícula, no aparecen filas (devolvemos vacío sin fallar).
        try:
            await page.wait_for_selector(CURSOS_ROW, state="attached", timeout=12_000)
        except Exception:
            return Enrollment(period=period, courses=[], total_credits=0)

        courses = await self._extract_courses(page)
        total = sum(c.credits for c in courses)
        return Enrollment(period=period, courses=courses, total_credits=total)

    async def _navigate(self, session: BrowserSession) -> None:
        await sidebar_navigation.dismiss_modal(session)
        await sidebar_navigation.ensure_sidebar_open(session)
        await sidebar_navigation.expand_submenu(session, HISTORIALES_SUBMENU)
        await sidebar_navigation.click_menu_link(session, FICHA_LINK)
        await session.page.wait_for_selector(PERIODO_SELECT, timeout=15_000)

    async def _select_latest_period(self, session: BrowserSession) -> Optional[str]:
        # Las opciones llegan en orden ascendente (…2025-I, 2026-I) con un "0"
        # = "SELECCIONAR PERIODO". Tomamos el período más reciente real.
        page = session.page

        # Los períodos se llenan por AJAX después de que el <select> existe;
        # esperar a que aparezca al menos una opción real (además del "0").
        try:
            await page.wait_for_function(
                "document.querySelectorAll('#btnPeriodoMat option').length > 1",
                timeout=10_000,
            )
        except Exception:
            return None

        options = await page.query_selector_all(f"{PERIODO_SELECT} option")
        values = []
        for option in options:
            value = await option.get_attribute("value")
            if value and value != "0":
                values.append(value)
        if not values:
            return None

        latest = values[-1]
        await page.select_option(PERIODO_SELECT, value=latest)
        return latest

    async def _extract_courses(self, page) -> List[EnrolledCourse]:
        rows = await page.query_selector_all(f"{CURSOS_TABLE} tbody tr")
        courses: List[EnrolledCourse] = []
        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) < 8:
                continue
            texts = [(await c.inner_text()).strip() for c in cells]

            course_id = texts[_COL_ID]
            course_name = texts[_COL_NAME]
            if not course_id or not course_name:
                continue

            courses.append(
                EnrolledCourse(
                    cycle=texts[_COL_CYCLE],
                    course_id=course_id,
                    course_name=course_name,
                    course_type=texts[_COL_TYPE],
                    credits=_as_int(texts[_COL_CREDITS]),
                    group=texts[_COL_GROUP],
                    attempt=_as_int(texts[_COL_ATTEMPT], default=1),
                    teacher=texts[_COL_TEACHER] or None,
                )
            )
        return courses


def _as_int(text: str, default: int = 0) -> int:
    return int(text) if text.isdigit() else default
