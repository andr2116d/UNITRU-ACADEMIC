import re
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Tuple

from ...application.ports.suv_record_extraction_port import SuvRecordExtractionPort
from ...domain.entities.academic_record import AcademicRecord, CourseHistory
from ...domain.entities.browser_session import BrowserSession
from . import sidebar_navigation

# El enlace real es option=recordAcad (module=historiales), no verRecordAcademico.
HISTORIALES_SUBMENU = "Historiales"
RECORD_LINK = 'a[href*="option=recordAcad"]'
RECORD_TABLE_ROW = "#tablaRecord tr td"

PERIOD_ROW_COLOR = "#00bcd4"


class SuvRecordExtractor(SuvRecordExtractionPort):
    async def extract_academic_record(self, session: BrowserSession) -> AcademicRecord:
        page = session.page

        await self._navigate(session)

        student_name = await self._span_text(page, "#nombreA")
        enrollment_number = await self._span_text(page, "#nroMat")
        condition = await self._span_text(page, "#condicion")
        credits_raw = await self._span_text(page, "#credAcu")
        weighted_raw = await self._span_text(page, "#ponderado")

        accumulated_credits = int(credits_raw) if credits_raw and credits_raw.isdigit() else 0
        try:
            weighted_average = Decimal(weighted_raw) if weighted_raw else Decimal("0")
        except InvalidOperation:
            weighted_average = Decimal("0")

        courses, payment_status, payment_order = await self._extract_table(page)

        return AcademicRecord(
            student_name=student_name or "",
            enrollment_number=enrollment_number or "",
            condition=condition or "",
            accumulated_credits=accumulated_credits,
            weighted_average=weighted_average,
            payment_status=payment_status,
            payment_order=payment_order,
            courses=courses,
        )

    async def _navigate(self, session: BrowserSession) -> None:
        page = session.page
        await sidebar_navigation.dismiss_modal(session)
        await sidebar_navigation.ensure_sidebar_open(session)
        await sidebar_navigation.expand_submenu(session, HISTORIALES_SUBMENU)
        await sidebar_navigation.click_menu_link(session, RECORD_LINK)

        # obtenerRecordAcademico() llena #tablaRecord por AJAX
        await page.wait_for_selector(RECORD_TABLE_ROW, timeout=20_000)
        # El ponderado se calcula después de cargar los cursos
        await page.wait_for_function(
            "document.querySelector('#ponderado')?.textContent?.trim() !== ''",
            timeout=15_000,
        )

    async def _extract_table(
        self, page
    ) -> Tuple[List[CourseHistory], Optional[str], Optional[str]]:
        rows = await page.query_selector_all("#tablaRecord tr")
        courses: List[CourseHistory] = []
        payment_status: Optional[str] = None
        payment_order: Optional[str] = None
        current_period = ""

        for row in rows:
            style = await row.get_attribute("style") or ""
            if PERIOD_ROW_COLOR in style:
                cells = await row.query_selector_all("td")
                if len(cells) >= 2:
                    current_period = (await cells[0].inner_text()).strip()
                    cadena = await cells[1].inner_text()
                    # Tomar el estado de pago del periodo más reciente (el último en el DOM)
                    status, order = self._parse_payment(cadena)
                    if status:
                        payment_status = status
                    if order:
                        payment_order = order
            else:
                course = await self._parse_course_row(row, current_period)
                if course:
                    courses.append(course)

        return courses, payment_status, payment_order

    def _parse_payment(self, cadena: str) -> Tuple[Optional[str], Optional[str]]:
        if "(PAGADA)" in cadena:
            status = "PAGADA"
        elif "(PENDIENTE)" in cadena:
            status = "PENDIENTE"
        else:
            status = None

        match = re.search(r"ORDEN PAGO:\s*(\d+)", cadena)
        order = match.group(1) if match else None

        return status, order

    async def _parse_course_row(
        self, row, period: str
    ) -> Optional[CourseHistory]:
        cells = await row.query_selector_all("td")
        if len(cells) < 13:
            return None

        try:
            course_id = (await cells[0].inner_text()).strip()
            course_name = (await cells[1].inner_text()).strip()

            if not course_id or not course_name:
                return None

            attempt_txt = (await cells[2].inner_text()).strip()
            cycle_txt = (await cells[3].inner_text()).strip()
            credits_txt = (await cells[4].inner_text()).strip()
            course_type = (await cells[5].inner_text()).strip()
            section = (await cells[6].inner_text()).strip() or None
            group = (await cells[7].inner_text()).strip() or None
            # La nota final del curso vive en la columna NPr (Nota Promedio, col 10):
            # es el promedio de las unidades. La columna "P. Final" (col 11) es el
            # aplazado (nap), normalmente vacío y solo con valor si rindió aplazado;
            # cuando existe, reemplaza al promedio (ver obtenerNota en recordAcad.js).
            npr_txt = (await cells[10].inner_text()).strip()
            nap_txt = (await cells[11].inner_text()).strip()
            inh_txt = (await cells[12].inner_text()).strip()

            attempt = int(attempt_txt) if attempt_txt.isdigit() else 1
            cycle = int(cycle_txt) if cycle_txt.isdigit() else 0
            credits = int(credits_txt) if credits_txt.isdigit() else 0
            is_disabled = inh_txt.upper() == "SI"

            # "NP" = aplazado sin nota → no cuenta; vacío = aún no registrado.
            chosen = nap_txt if nap_txt and nap_txt != "NP" else npr_txt
            if chosen and chosen != "NP":
                try:
                    final_grade = Decimal(chosen)
                except InvalidOperation:
                    final_grade = None
            else:
                final_grade = None

            return CourseHistory(
                period=period,
                course_id=course_id,
                course_name=course_name,
                attempt=attempt,
                cycle=cycle,
                credits=credits,
                course_type=course_type,
                section=section,
                group=group,
                final_grade=final_grade,
                is_disabled=is_disabled,
            )
        except Exception:
            return None

    async def _span_text(self, page, selector: str) -> Optional[str]:
        el = await page.query_selector(selector)
        if not el:
            return None
        text = await el.inner_text()
        return text.strip() if text and text.strip() else None
