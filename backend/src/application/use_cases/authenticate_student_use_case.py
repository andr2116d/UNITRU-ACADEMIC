from typing import Awaitable, Callable

from ...domain.entities.browser_session import BrowserSession
from ...domain.exceptions.suv_errors import AuthenticationError, CaptchaError
from ..ports.captcha_solver_port import CaptchaSolverPort
from ..ports.suv_authentication_port import SuvAuthenticationPort

MAX_CAPTCHA_ATTEMPTS = 3

EventEmitter = Callable[[str, dict], Awaitable[None]]


class AuthenticateStudentUseCase:
    def __init__(
        self,
        suv_auth: SuvAuthenticationPort,
        captcha_solver: CaptchaSolverPort,
    ) -> None:
        self._suv_auth = suv_auth
        self._captcha_solver = captcha_solver

    async def execute(
        self,
        username: str,
        password: str,
        session: BrowserSession,
        emit: EventEmitter,
    ) -> BrowserSession:
        await emit("opening_suv", {})
        await self._suv_auth.open_suv(session)

        await emit("loading_login", {})

        for attempt in range(1, MAX_CAPTCHA_ATTEMPTS + 1):
            await emit("downloading_captcha", {"attempt": attempt})
            captcha_bytes = await self._suv_auth.get_captcha_image(session)

            await emit("solving_captcha", {"attempt": attempt})
            try:
                captcha_solution = await self._captcha_solver.solve(captcha_bytes)
                await emit("submitting_login", {})
                success = await self._suv_auth.submit_login(
                    session, username, password, captcha_solution
                )
            except CaptchaError:
                # Un fallo de OCR es un intento fallido más, no un error fatal;
                # hay que recargar y pedir otro captcha.
                success = False

            if success:
                await emit("selecting_student", {})
                await self._suv_auth.select_student_profile(session)
                await emit("authentication_success", {})
                session.touch()
                return session

            if attempt < MAX_CAPTCHA_ATTEMPTS:
                await self._suv_auth.reload_login_page(session)

        await emit("authentication_failed", {"reason": "max_captcha_attempts"})
        raise AuthenticationError(
            "Authentication failed after maximum captcha attempts"
        )
