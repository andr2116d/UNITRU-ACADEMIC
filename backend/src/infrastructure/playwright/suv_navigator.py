from ...application.ports.suv_navigation_port import SuvNavigationPort
from ...domain.entities.browser_session import BrowserSession
from . import sidebar_navigation

# "Notas" es un menu-toggle que despliega el submenú (no navega); el enlace
# real a la pantalla de notas es "Ver" (option=verNotas).
NOTAS_SUBMENU = "Notas"
VER_LINK = 'a[href*="option=verNotas"]'
# La tabla se considera cargada cuando tiene al menos una fila con celdas
GRADES_TABLE_ROW = "#tablaNotas tr td"


class SuvNavigator(SuvNavigationPort):
    async def navigate_to_grades(self, session: BrowserSession) -> None:
        await sidebar_navigation.dismiss_modal(session)
        await sidebar_navigation.ensure_sidebar_open(session)
        await sidebar_navigation.expand_submenu(session, NOTAS_SUBMENU)

    async def click_ver(self, session: BrowserSession) -> None:
        page = session.page
        await sidebar_navigation.dismiss_modal(session)
        await sidebar_navigation.click_menu_link(session, VER_LINK)

        # verNotasPeriodActual() llena #tablaNotas por AJAX; esperamos las filas.
        await sidebar_navigation.dismiss_modal(session)
        await page.wait_for_selector(GRADES_TABLE_ROW, timeout=20_000)
