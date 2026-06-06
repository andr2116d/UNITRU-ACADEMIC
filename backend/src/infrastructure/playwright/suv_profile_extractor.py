import base64
from typing import Optional

from ...application.ports.suv_profile_extraction_port import SuvProfileExtractionPort
from ...domain.entities.browser_session import BrowserSession
from ...domain.entities.student_profile import StudentProfile
from . import sidebar_navigation

# "Datos Personales" cuelga del submenú "Detalle Usuario", no de "Perfil".
PROFILE_SUBMENU = "Detalle Usuario"
PROFILE_LINK = 'a[href*="option=datosPersonales"]'
LOAD_SIGNAL = "#apePaterno"
# La foto real vive en #vistaPrevia; llamarFoto2() le pone el src por AJAX
# (fotos/1_<DNI>.JPG). #imagenAlumno es el input file, no la imagen.
PHOTO_IMG = "#vistaPrevia"


class SuvProfileExtractor(SuvProfileExtractionPort):
    async def extract_student_profile(self, session: BrowserSession) -> StudentProfile:
        page = session.page

        await self._navigate(session)

        first_name = await self._input_value(page, "#nombres")
        last_pat = await self._input_value(page, "#apePaterno")
        last_mat = await self._input_value(page, "#apeMaterno")
        personal_email = await self._input_value(page, "#email")
        institutional_email = await self._input_value(page, "#email_inst")
        phone = await self._input_value(page, "#celular")
        campus = await self._input_value(page, "#sede")
        faculty = await self._input_value(page, "#facultad")
        school = await self._input_value(page, "#escuela")
        admission_year_raw = await self._input_value(page, "#anioI")
        enrollment_number = await self._input_value(page, "#codigo")
        document = await self._input_value(page, "#documento")
        birth_date = await self._input_value(page, "#fecNacimiento")
        address = await self._input_value(page, "#domicilio")
        curriculum = await self._input_value(page, "#curricula")
        condition = await self._input_value(page, "#condicion")
        # sexo/estadoCivil son <select>: queremos la etiqueta, no el value (1/0).
        sex = await self._selected_text(page, "#sexo")
        marital_status = await self._selected_text(page, "#estadoCivil")
        photo_data_url = await self._fetch_photo(session)

        last_name = " ".join(filter(None, [last_pat, last_mat]))
        full_name = f"{last_name}, {first_name}" if first_name else last_name

        admission_year: Optional[int] = None
        if admission_year_raw and admission_year_raw.isdigit():
            admission_year = int(admission_year_raw)

        return StudentProfile(
            full_name=full_name or "",
            first_name=first_name or "",
            last_name=last_name,
            enrollment_number=enrollment_number or "",
            faculty=faculty or "",
            school=school or "",
            campus=campus or "",
            admission_year=admission_year,
            institutional_email=institutional_email,
            personal_email=personal_email,
            phone=phone,
            document=document,
            birth_date=birth_date,
            sex=sex,
            marital_status=marital_status,
            address=address,
            curriculum=curriculum,
            condition=condition,
            photo_data_url=photo_data_url,
        )

    async def _navigate(self, session: BrowserSession) -> None:
        page = session.page
        await sidebar_navigation.dismiss_modal(session)
        await sidebar_navigation.ensure_sidebar_open(session)
        await sidebar_navigation.expand_submenu(session, PROFILE_SUBMENU)
        await sidebar_navigation.click_menu_link(session, PROFILE_LINK)

        # cargarDataAlumno() + cargarDatosAcademicos() llenan los inputs por AJAX
        await page.wait_for_selector(LOAD_SIGNAL, timeout=15_000)
        # Esperar que el valor ya no esté vacío
        await page.wait_for_function(
            "document.querySelector('#apePaterno')?.value?.trim() !== ''",
            timeout=10_000,
        )

    async def _input_value(self, page, selector: str) -> Optional[str]:
        el = await page.query_selector(selector)
        if not el:
            return None
        # El SUV llena estos inputs por JS (element.value = ...), que actualiza
        # la propiedad del DOM pero no el atributo HTML; get_attribute("value")
        # devolvería vacío. input_value() lee el valor real en pantalla.
        try:
            value = await el.input_value()
        except Exception:
            value = await el.get_attribute("value")
        return value.strip() if value and value.strip() else None

    async def _selected_text(self, page, selector: str) -> Optional[str]:
        # Para <select> queremos el texto de la opción elegida (MASCULINO),
        # no su value (1).
        try:
            text = await page.eval_on_selector(
                selector,
                "el => el.options[el.selectedIndex] ? el.options[el.selectedIndex].text : ''",
            )
        except Exception:
            return None
        return text.strip() if text and text.strip() else None

    async def _fetch_photo(self, session: BrowserSession) -> Optional[str]:
        # llamarFoto2() pone el src de #vistaPrevia por AJAX. Descargamos los
        # bytes con la sesión autenticada (el frontend no tiene cookies del SUV)
        # y los devolvemos como data URL. La foto es best-effort: cualquier
        # fallo deja el perfil sin foto, no rompe la extracción.
        page = session.page
        try:
            await page.wait_for_function(
                "document.querySelector('#vistaPrevia')?.src?.includes('/fotos/')",
                timeout=6_000,
            )
        except Exception:
            pass

        try:
            src = await page.eval_on_selector(
                PHOTO_IMG, "el => el.src || ''"
            )
        except Exception:
            return None

        # Placeholder cuando el alumno no tiene foto válida (prueba.JPG).
        if not src or "/fotos/" not in src:
            return None

        try:
            response = await page.context.request.get(src)
            if not response.ok:
                return None
            body = await response.body()
            if not body:
                return None
            encoded = base64.b64encode(body).decode("ascii")
            return f"data:image/jpeg;base64,{encoded}"
        except Exception:
            return None
