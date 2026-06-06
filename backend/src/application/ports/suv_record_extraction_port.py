from abc import ABC, abstractmethod

from ...domain.entities.academic_record import AcademicRecord
from ...domain.entities.browser_session import BrowserSession


class SuvRecordExtractionPort(ABC):
    @abstractmethod
    async def extract_academic_record(self, session: BrowserSession) -> AcademicRecord:
        ...
