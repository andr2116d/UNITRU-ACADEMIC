from abc import ABC, abstractmethod

from ...domain.entities.browser_session import BrowserSession


class SuvAuthenticationPort(ABC):
    @abstractmethod
    async def open_suv(self, session: BrowserSession) -> None:
        ...

    @abstractmethod
    async def get_captcha_image(self, session: BrowserSession) -> bytes:
        ...

    @abstractmethod
    async def submit_login(
        self,
        session: BrowserSession,
        username: str,
        password: str,
        captcha: str,
    ) -> bool:
        """Submits the login form. Returns True if authentication succeeded."""
        ...

    @abstractmethod
    async def select_student_profile(self, session: BrowserSession) -> None:
        ...

    @abstractmethod
    async def reload_login_page(self, session: BrowserSession) -> None:
        ...
