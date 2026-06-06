from dataclasses import dataclass, field
from typing import List, Optional

from .schedule_catalog import CatalogSession


@dataclass
class CourseSelection:
    """Una opción concreta de un curso: de qué sección (y sub-grupo de lab) se
    tomaría, con sus sesiones."""

    course: str
    cycle: Optional[str]
    section: Optional[str]
    subgroup: Optional[str]
    sessions: List[CatalogSession] = field(default_factory=list)


@dataclass
class OptimizedSchedule:
    """Un horario candidato: una selección por curso, sin choques, con su puntaje
    (menor = mejor) y el desglose de las métricas que lo justifican."""

    selections: List[CourseSelection]
    score: float
    gap_minutes: int
    days: int
    extreme_sessions: int

    @property
    def sessions(self) -> List[CatalogSession]:
        return [s for sel in self.selections for s in sel.sessions]
