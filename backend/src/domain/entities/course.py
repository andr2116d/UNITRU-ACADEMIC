from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Course:
    course_id: str
    course_name: str
    attempt: int
    u1: Optional[Decimal] = None
    u2: Optional[Decimal] = None
    u3: Optional[Decimal] = None
    u4: Optional[Decimal] = None
    u5: Optional[Decimal] = None
    u6: Optional[Decimal] = None
    sust: Optional[Decimal] = None
    np: Optional[Decimal] = None
    apla: Optional[Decimal] = None
    final_grade: Optional[Decimal] = None
    inh: bool = False
