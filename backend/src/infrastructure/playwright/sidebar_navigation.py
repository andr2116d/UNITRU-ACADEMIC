from ...domain.entities.browser_session import BrowserSession

# Helpers compartidos para navegar el menú lateral AdminBSB del SUV.
# Cada extractor llama a _navigate() de forma independiente; el primero abre el
# sidebar y expande su submenú, los siguientes heredan el sidebar ya abierto.

# El sidebar arranca cerrado (body.ls-closed) y deja el menú fuera del viewport;
# ni el clic forzado funciona sobre un elemento off-canvas.
SIDEBAR_CLOSED = "body.ls-closed"
SIDEBAR_TOGGLE = "a.bars"

# Modal informativo ("Tener en Cuenta") que puede interceptar clics.
MODAL = "#myModal"
MODAL_CLOSE = '#myModal button[data-dismiss="modal"]'


def _submenu_toggle(toggle_text: str) -> str:
    # Cada sección del menú es un a.menu-toggle que despliega su propio ul.ml-menu.
    return f'a.menu-toggle:has(span:text-is("{toggle_text}"))'


def _submenu_list(toggle_text: str) -> str:
    return (
        f'li:has(> a.menu-toggle:has(span:text-is("{toggle_text}"))) ul.ml-menu'
    )


async def dismiss_modal(session: BrowserSession) -> None:
    page = session.page
    try:
        modal = page.locator(MODAL)
        if await modal.is_visible(timeout=1_000):
            await page.locator(MODAL_CLOSE).first.click(timeout=3_000)
            await modal.wait_for(state="hidden", timeout=5_000)
    except Exception:
        # Si no hay modal, seguir sin bloquear el flujo.
        pass


async def ensure_sidebar_open(session: BrowserSession) -> None:
    page = session.page
    if await page.locator(SIDEBAR_CLOSED).count() == 0:
        return

    bars = page.locator(SIDEBAR_TOGGLE).first
    try:
        await bars.click(timeout=5_000)
    except Exception:
        await bars.click(force=True, timeout=5_000)

    try:
        await page.wait_for_selector("body:not(.ls-closed)", timeout=5_000)
    except Exception:
        # Esperar la animación si la clase no cambia como se espera.
        await page.wait_for_timeout(800)


async def expand_submenu(session: BrowserSession, toggle_text: str) -> None:
    page = session.page
    toggle = page.locator(_submenu_toggle(toggle_text)).first
    await toggle.wait_for(state="visible", timeout=15_000)
    await _click_resilient(toggle)

    # Esperar a que el submenú se despliegue (animación slideDown).
    await page.locator(_submenu_list(toggle_text)).wait_for(
        state="visible", timeout=10_000
    )


async def click_menu_link(session: BrowserSession, link_selector: str) -> None:
    page = session.page
    link = page.locator(link_selector).first
    await link.wait_for(state="visible", timeout=10_000)
    await _click_resilient(link)


async def _click_resilient(locator) -> None:
    # El menú lateral tiene scroll propio (slimScroll) y los ítems de más abajo
    # quedan fuera del viewport: ni scroll_into_view ni el clic forzado los
    # alcanzan. El clic por JS dispara el mismo handler que un clic real
    # (los toggles y enlaces del SUV son anchors con onclick / href).
    try:
        await locator.scroll_into_view_if_needed(timeout=5_000)
    except Exception:
        pass
    try:
        await locator.click(timeout=8_000)
        return
    except Exception:
        pass
    try:
        await locator.click(force=True, timeout=8_000)
        return
    except Exception:
        pass
    await locator.evaluate("el => el.click()")
