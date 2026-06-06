from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CoursePredictionDto:
    course_id: str
    course_name: str
    total_units: int
    known: dict[str, str]
    pending: list[str]
    required_pending_sum: str
    min_per_pending: str
    is_possible: bool
    already_passes: bool
    combinations: list[dict[str, int]] = field(default_factory=list)
