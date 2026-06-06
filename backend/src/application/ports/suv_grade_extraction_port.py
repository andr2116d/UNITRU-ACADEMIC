from abc import ABC, abstractmethod

from ...domain.entities.browser_session import BrowserSession
from ...domain.entities.grade_report import GradeReport


class SuvGradeExtractionPort(ABC):
    @abstractmethod
    async def extract_grade_report(self, session: BrowserSession) -> GradeReport:
        ...
