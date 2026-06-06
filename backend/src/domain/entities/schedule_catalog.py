import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional


def normalize_course(name: str) -> str:
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text).strip().lower()


@dataclass(frozen=True)
class CatalogSession:
    """Una sesión del catálogo oficial (una hoja del Google Sheets)."""

    course: str
    cycle: Optional[str]
    section: Optional[str]
    group: Optional[str]
    tipo: Optional[str]
    day: str
    start_min: int
    end_min: int
    room: Optional[str]
    subgroup: Optional[str]
    teacher: Optional[str]


@dataclass
class ScheduleCatalog:
    sessions: List[CatalogSession] = field(default_factory=list)

    def for_course(self, course_name: str) -> List[CatalogSession]:
        target = normalize_course(course_name)
        return [s for s in self.sessions if normalize_course(s.course) == target]

    def course_names(self) -> List[str]:
        seen = {}
        for s in self.sessions:
            seen.setdefault(normalize_course(s.course), s.course)
        return list(seen.values())
