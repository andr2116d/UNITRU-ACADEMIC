from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentProfile:
    full_name: str
    first_name: str
    last_name: str
    enrollment_number: str
    faculty: str
    school: str
    campus: str
    admission_year: Optional[int] = None
    institutional_email: Optional[str] = None
    personal_email: Optional[str] = None
    phone: Optional[str] = None
    document: Optional[str] = None
    birth_date: Optional[str] = None
    sex: Optional[str] = None
    marital_status: Optional[str] = None
    address: Optional[str] = None
    curriculum: Optional[str] = None
    condition: Optional[str] = None
    # Foto del alumno como data URL (base64); el frontend la muestra directo.
    photo_data_url: Optional[str] = None
