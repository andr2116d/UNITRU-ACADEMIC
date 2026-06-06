from abc import ABC, abstractmethod
from typing import List

from ...domain.entities.attendance import CourseAttendance
from ...domain.entities.browser_session import BrowserSession


class SuvAttendanceExtractionPort(ABC):
    @abstractmethod
    async def extract_attendance(
        self, session: BrowserSession
    ) -> List[CourseAttendance]:
        # Devuelve las sesiones crudas por curso. El cálculo de resumen y horario
        # vive en domain/services/schedule_builder, no en el adaptador.
        ...
