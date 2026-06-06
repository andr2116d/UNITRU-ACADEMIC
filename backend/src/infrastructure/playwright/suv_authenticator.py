import base64

from ...application.ports.suv_authentication_port import SuvAuthenticationPort
from ...domain.entities.browser_session import BrowserSession
from ...domain.exceptions.suv_errors import NavigationError

SUV_URL = "https://suv2.unitru.edu.pe/"

# Tiempo máximo para que el login cargue completamente
LOGIN_TIMEOUT = 60_000

# Selectores verificados contra el SUV real.
USERNAME_SELECTOR = 'input[name="username"]'
PASSWORD_SELECTOR = 'input[name="pass"]'
CAPTCHA_INPUT_SELECTOR = 'input[name="captcha"]'
CAPTCHA_IMAGE_SELECTOR = "#captcha-img"
# El botón es type=button y dispara JS; no es un submit real
LOGIN_BUTTON_SELECTOR = "#myButton"


class SuvAuthenticator(SuvAuthenticationPort):
    async def open_suv(self, session: BrowserSession) -> None:
        page = session.page

        await page.goto(SUV_URL, wait_until="domcontentloaded", timeout=LOGIN_TIMEOUT)

        try:
            await page.wait_for_selector(
                USERNAME_SELECTOR,
                state="visible",
                timeout=LOGIN_TIMEOUT,
            )
        except Exception:
            # Captura de diagnóstico — ayuda a entender qué muestra el SUV
            screenshot_b64 = await self._screenshot_b64(page)
            html_snippet = (await page.content())[:2000]
            raise NavigationError(
                f"Login form not found on SUV.\n"
                f"URL: {page.url}\n"
                f"HTML (first 2000 chars):\n{html_snippet}\n"
                f"Screenshot (base64 PNG):\n{screenshot_b64}"
            )

    async def get_captcha_image(self, session: BrowserSession) -> bytes:
        captcha_element = await session.page.wait_for_selector(
            CAPTCHA_IMAGE_SELECTOR, state="visible", timeout=LOGIN_TIMEOUT
        )
        return await captcha_element.screenshot()

    async def submit_login(
        self,
        session: BrowserSession,
        username: str,
        password: str,
        captcha: str,
    ) -> bool:
        page = session.page

        await page.fill(USERNAME_SELECTOR, username)
        await page.fill(PASSWORD_SELECTOR, password)
        await page.fill(CAPTCHA_INPUT_SELECTOR, captcha)

        await page.click(LOGIN_BUTTON_SELECTOR)

        try:
            await page.wait_for_load_state("networkidle", timeout=12_000)
            content = await page.content()
            return "SELECCIONAR PERFIL" in content and "Alumno" in content
        except Exception:
            return False

    async def select_student_profile(self, session: BrowserSession) -> None:
        await session.page.click("text=Alumno")
        await session.page.wait_for_load_state("networkidle", timeout=15_000)

    async def reload_login_page(self, session: BrowserSession) -> None:
        await session.page.reload(wait_until="domcontentloaded", timeout=LOGIN_TIMEOUT)
        await session.page.wait_for_selector(
            USERNAME_SELECTOR, state="visible", timeout=LOGIN_TIMEOUT
        )

    async def _screenshot_b64(self, page) -> str:
        try:
            data = await page.screenshot(type="png")
            return base64.b64encode(data).decode()
        except Exception:
            return "(screenshot unavailable)"
