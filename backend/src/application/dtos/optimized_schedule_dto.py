from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OptimizedSessionDto:
    course: str
    tipo: Optional[str]
    day: str
    start_time: str
    end_time: str
    room: Optional[str]
    subgroup: Optional[str]
    teacher: Optional[str]
    section: Optional[str]


@dataclass
class OptimizedSelectionDto:
    course: str
    cycle: Optional[str]
    section: Optional[str]
    subgroup: Optional[str]


@dataclass
class OptimizedScheduleDto:
    score: float
    days: int
    gap_minutes: int
    extreme_sessions: int
    selections: List[OptimizedSelectionDto] = field(default_factory=list)
    sessions: List[OptimizedSessionDto] = field(default_factory=list)
