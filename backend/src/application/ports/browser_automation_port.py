from abc import ABC, abstractmethod

from ...domain.entities.browser_session import BrowserSession


class BrowserAutomationPort(ABC):
    @abstractmethod
    async def create_session(self) -> BrowserSession:
        ...

    @abstractmethod
    async def destroy_session(self, session: BrowserSession) -> None:
        ...
