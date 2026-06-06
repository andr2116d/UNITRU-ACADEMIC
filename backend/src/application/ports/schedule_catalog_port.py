from abc import ABC, abstractmethod

from ...domain.entities.schedule_catalog import ScheduleCatalog


class ScheduleCatalogPort(ABC):
    """Fuente del catálogo oficial de horarios. Hoy: un JSON local generado del
    Google Sheets. A futuro: un adaptador que reciba el enlace desde el frontend
    y lo descargue/parsee en backend (misma interfaz)."""

    @abstractmethod
    def load(self) -> ScheduleCatalog:
        ...
