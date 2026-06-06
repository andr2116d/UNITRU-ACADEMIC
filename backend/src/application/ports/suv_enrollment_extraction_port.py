from abc import ABC, abstractmethod

from ...domain.entities.browser_session import BrowserSession
from ...domain.entities.enrollment import Enrollment


class SuvEnrollmentExtractionPort(ABC):
    @abstractmethod
    async def extract_enrollment(self, session: BrowserSession) -> Enrollment:
        ...
