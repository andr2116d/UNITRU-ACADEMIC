from abc import ABC, abstractmethod

from ...domain.entities.browser_session import BrowserSession
from ...domain.entities.student_profile import StudentProfile


class SuvProfileExtractionPort(ABC):
    @abstractmethod
    async def extract_student_profile(self, session: BrowserSession) -> StudentProfile:
        ...
