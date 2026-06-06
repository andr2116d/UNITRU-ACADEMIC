from abc import ABC, abstractmethod

from ...domain.entities.browser_session import BrowserSession


class SuvNavigationPort(ABC):
    @abstractmethod
    async def navigate_to_grades(self, session: BrowserSession) -> None:
        ...

    @abstractmethod
    async def click_ver(self, session: BrowserSession) -> None:
        ...
