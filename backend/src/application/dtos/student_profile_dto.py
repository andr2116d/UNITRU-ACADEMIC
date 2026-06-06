from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentProfileDto:
    full_name: str
    first_name: str
    last_name: str
    enrollment_number: str
    faculty: str
    school: str
    campus: str
    admission_year: Optional[int]
    institutional_email: Optional[str]
    personal_email: Optional[str]
    phone: Optional[str]
    document: Optional[str] = None
    birth_date: Optional[str] = None
    sex: Optional[str] = None
    marital_status: Optional[str] = None
    address: Optional[str] = None
    curriculum: Optional[str] = None
    condition: Optional[str] = None
    photo_data_url: Optional[str] = None
