import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .application.use_cases.authenticate_student_use_case import (
    AuthenticateStudentUseCase,
)
from .application.use_cases.extract_full_dashboard_use_case import (
    ExtractFullDashboardUseCase,
)
from .infrastructure.catalog.json_catalog_adapter import JsonCatalogAdapter
from .infrastructure.ocr.tesseract_adapter import TesseractAdapter
from .infrastructure.playwright.playwright_adapter import PlaywrightAdapter
from .infrastructure.playwright.session_manager import SessionManager
from .infrastructure.playwright.suv_attendance_extractor import SuvAttendanceExtractor
from .infrastructure.playwright.suv_authenticator import SuvAuthenticator
from .infrastructure.playwright.suv_enrollment_extractor import SuvEnrollmentExtractor
from .infrastructure.playwright.suv_grade_extractor import SuvGradeExtractor
from .infrastructure.playwright.suv_navigator import SuvNavigator
from .infrastructure.playwright.suv_profile_extractor import SuvProfileExtractor
from .infrastructure.playwright.suv_record_extractor import SuvRecordExtractor
from .presentation.websocket.websocket_handler import WebSocketHandler

# Infrastructure
playwright_adapter = PlaywrightAdapter()
session_manager = SessionManager(playwright_adapter)

# Adapters
suv_authenticator = SuvAuthenticator()
suv_navigator = SuvNavigator()
suv_grade_extractor = SuvGradeExtractor()
suv_profile_extractor = SuvProfileExtractor()
suv_record_extractor = SuvRecordExtractor()
suv_attendance_extractor = SuvAttendanceExtractor()
suv_enrollment_extractor = SuvEnrollmentExtractor()
tesseract_adapter = TesseractAdapter()

# Catálogo de horarios oficiales (hoy un JSON generado del Google Sheets;
# a futuro un adaptador que reciba el enlace desde el frontend).
_catalog_path = Path(__file__).resolve().parents[1] / "data" / "horarios_catalogo.json"
schedule_catalog_adapter = JsonCatalogAdapter(str(_catalog_path))

# Use cases
authenticate_use_case = AuthenticateStudentUseCase(suv_authenticator, tesseract_adapter)
dashboard_use_case = ExtractFullDashboardUseCase(
    profile_port=suv_profile_extractor,
    record_port=suv_record_extractor,
    attendance_port=suv_attendance_extractor,
    enrollment_port=suv_enrollment_extractor,
    grades_port=suv_grade_extractor,
    navigation_port=suv_navigator,
    catalog_port=schedule_catalog_adapter,
)

# Handlers
websocket_handler = WebSocketHandler(
    session_manager,
    authenticate_use_case,
    dashboard_use_case,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await session_manager.destroy_all()


app = FastAPI(title="UNITRU Academic API", version="0.2.0", lifespan=lifespan)

# Orígenes permitidos configurables por entorno (coma-separados) para el despliegue;
# por defecto, el frontend local.
_allowed_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket_handler.handle(websocket)
