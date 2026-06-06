from decimal import Decimal, InvalidOperation
from typing import List, Optional

from ...application.ports.suv_grade_extraction_port import SuvGradeExtractionPort
from ...domain.entities.browser_session import BrowserSession
from ...domain.entities.course import Course
from ...domain.entities.grade_report import GradeReport
from ...domain.exceptions.suv_errors import GradesTableNotFoundError


class SuvGradeExtractor(SuvGradeExtractionPort):
    """Lee el DOM de la pantalla de notas y mapea a entidades de dominio.

    Solo extrae: no calcula promedios ni interpreta reglas académicas.
    """

    async def extract_grade_report(self, session: BrowserSession) -> GradeReport:
        page = session.page

        table = await page.query_selector("#tablaNotas")
        if not table:
            raise GradesTableNotFoundError("Grades table #tablaNotas not found")

        period = await self._get_input_value(page, "#periodo")
        payment_order = await self._get_input_value(page, "#ordenPago")
        enrollment_type = await self._get_input_value(page, "#tipomat")

        rows = await page.query_selector_all("#tablaNotas tr")
        courses = []
        for row in rows:
            course = await self._extract_course_from_row(row)
            if course:
                courses.append(course)

        return GradeReport(
            period=period,
            payment_order=payment_order,
            enrollment_type=enrollment_type,
            courses=courses,
        )

    async def _get_input_value(self, page, selector: str) -> Optional[str]:
        element = await page.query_selector(selector)
        if not element:
            return None
        # #periodo, #ordenPago y #tipomat los llena el JS asignando la propiedad
        # .value; el atributo HTML queda vacío, por eso leemos input_value().
        try:
            value = await element.input_value()
        except Exception:
            value = await element.get_attribute("value")
        return value.strip() if value and value.strip() else None

    async def _extract_course_from_row(self, row) -> Optional[Course]:
        cells = await row.query_selector_all("td")
        if len(cells) < 3:
            return None

        try:
            course_id = await self._cell_text(cells[0])
            course_name = await self._cell_text(cells[1])

            if not course_id or not course_name:
                return None

            attempt_text = await self._cell_text(cells[2])
            attempt = int(attempt_text) if attempt_text and attempt_text.isdigit() else 1

            # Orden de columnas: ID, Nombre, Vez, U1..U6, SUST, NP, APLA, P.FINAL, INH.
            return Course(
                course_id=course_id,
                course_name=course_name,
                attempt=attempt,
                u1=await self._grade_from_cell(cells, 3),
                u2=await self._grade_from_cell(cells, 4),
                u3=await self._grade_from_cell(cells, 5),
                u4=await self._grade_from_cell(cells, 6),
                u5=await self._grade_from_cell(cells, 7),
                u6=await self._grade_from_cell(cells, 8),
                sust=await self._grade_from_cell(cells, 9),
                np=await self._grade_from_cell(cells, 10),
                apla=await self._grade_from_cell(cells, 11),
                final_grade=await self._grade_from_cell(cells, 12),
                inh=await self._inh_from_cell(cells, 13),
            )
        except Exception:
            # Una fila inconsistente (p. ej. filas de "sin datos" del SUV) se
            # omite en vez de tumbar toda la extracción. El resto de cursos
            # válidos sí se devuelven.
            return None

    async def _cell_text(self, cell) -> Optional[str]:
        text = await cell.inner_text()
        return text.strip() if text and text.strip() else None

    async def _grade_from_cell(
        self, cells: List, index: int
    ) -> Optional[Decimal]:
        if index >= len(cells):
            return None

        cell = cells[index]

        # El SUV pinta cada nota dentro de un <input>. Vacío = no publicada → None.
        input_el = await cell.query_selector("input")
        if input_el:
            # Las notas viven en la propiedad .value del input (el JS las pinta),
            # no en el atributo; input_value() refleja lo que se ve en pantalla.
            try:
                value = await input_el.input_value()
            except Exception:
                value = await input_el.get_attribute("value")
            if value and value.strip():
                try:
                    return Decimal(value.strip())
                except InvalidOperation:
                    return None
            return None

        text = await cell.inner_text()
        if text and text.strip():
            try:
                return Decimal(text.strip())
            except InvalidOperation:
                return None
        return None

    async def _inh_from_cell(self, cells: List, index: int) -> bool:
        if index >= len(cells):
            return False
        cell = cells[index]
        checkbox = await cell.query_selector('input[type="checkbox"]')
        if checkbox:
            return await checkbox.is_checked()
        return False
