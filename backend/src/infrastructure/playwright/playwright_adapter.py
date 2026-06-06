from typing import Any, Dict

from playwright.async_api import async_playwright

from ...application.ports.browser_automation_port import BrowserAutomationPort
from ...domain.entities.browser_session import BrowserSession

# El SUV rechaza navegadores headless evidentes; presentamos un Chrome real.
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class PlaywrightAdapter(BrowserAutomationPort):
    def __init__(self) -> None:
        self._playwrights: Dict[str, Any] = {}

    async def create_session(self) -> BrowserSession:
        session = BrowserSession()
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        # El certificado del SUV no lo firma una CA que Chromium reconozca, así
        # que goto() falla con ERR_CERT_AUTHORITY_INVALID. Un usuario real pasa
        # la advertencia; nosotros la ignoramos para poder continuar.
        context = await browser.new_context(
            user_agent=_USER_AGENT,
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True,
        )
        # Ocultar navigator.webdriver, una de las señales con que el SUV
        # detecta automatización.
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = await context.new_page()

        session.browser = browser
        session.browser_context = context
        session.page = page
        self._playwrights[session.session_id] = playwright

        return session

    async def destroy_session(self, session: BrowserSession) -> None:
        # Orden obligatorio: Page → BrowserContext → Browser.
        # Cada cierre va aislado para que un fallo no impida liberar el resto.
        await self._safe_close(session.page)
        await self._safe_close(session.browser_context)
        await self._safe_close(session.browser)

        playwright = self._playwrights.pop(session.session_id, None)
        if playwright is not None:
            await self._safe_stop(playwright)

    async def _safe_close(self, resource: Any) -> None:
        if resource is None:
            return
        try:
            await resource.close()
        except Exception:
            pass

    async def _safe_stop(self, playwright: Any) -> None:
        try:
            await playwright.stop()
        except Exception:
            pass
