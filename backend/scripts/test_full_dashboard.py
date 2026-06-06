"""Prueba E2E desechable: login + navegación de los cuatro módulos contra el
SUV en vivo. Reutiliza el mismo wiring que main.py. No forma parte del runtime.

Uso:
    python3 scripts/test_full_dashboard.py <usuario> <clave>

El captcha por OCR puede fallar; reintentamos la autenticación con sesiones
nuevas hasta AUTH_RETRIES veces antes de rendirnos.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.application.use_cases.authenticate_student_use_case import (
    AuthenticateStudentUseCase,
)
from src.application.use_cases.extract_full_dashboard_use_case import (
    ExtractFullDashboardUseCase,
)
from src.infrastructure.ocr.tesseract_adapter import TesseractAdapter
from src.infrastructure.playwright.playwright_adapter import PlaywrightAdapter
from src.infrastructure.playwright.session_manager import SessionManager
from src.infrastructure.playwright.suv_attendance_extractor import SuvAttendanceExtractor
from src.infrastructure.playwright.suv_authenticator import SuvAuthenticator
from src.infrastructure.catalog.json_catalog_adapter import JsonCatalogAdapter
from src.infrastructure.playwright.suv_enrollment_extractor import SuvEnrollmentExtractor
from src.infrastructure.playwright.suv_grade_extractor import SuvGradeExtractor
from src.infrastructure.playwright.suv_navigator import SuvNavigator
from src.infrastructure.playwright.suv_profile_extractor import SuvProfileExtractor
from src.infrastructure.playwright.suv_record_extractor import SuvRecordExtractor

AUTH_RETRIES = 5


async def emit(event: str, payload: dict) -> None:
    extra = f" {payload}" if payload else ""
    print(f"  · {event}{extra}", flush=True)


async def authenticate(session_manager, auth_use_case, username, password):
    for attempt in range(1, AUTH_RETRIES + 1):
        print(f"\n[Auth intento global {attempt}/{AUTH_RETRIES}]", flush=True)
        session = await session_manager.create_session()
        try:
            result = await auth_use_case.execute(username, password, session, emit)
            if result is not None:
                return session
        except Exception as exc:  # noqa: BLE001 — diagnóstico, queremos verlo todo
            print(f"  ! auth lanzó: {exc}", flush=True)
        await session_manager.destroy_session(session.session_id)
    return None


async def main() -> None:
    if len(sys.argv) < 3:
        print("Uso: python3 scripts/test_full_dashboard.py <usuario> <clave>")
        sys.exit(1)
    username, password = sys.argv[1], sys.argv[2]

    playwright_adapter = PlaywrightAdapter()
    session_manager = SessionManager(playwright_adapter)
    auth_use_case = AuthenticateStudentUseCase(SuvAuthenticator(), TesseractAdapter())
    dashboard_use_case = ExtractFullDashboardUseCase(
        profile_port=SuvProfileExtractor(),
        record_port=SuvRecordExtractor(),
        attendance_port=SuvAttendanceExtractor(),
        enrollment_port=SuvEnrollmentExtractor(),
        grades_port=SuvGradeExtractor(),
        navigation_port=SuvNavigator(),
        catalog_port=JsonCatalogAdapter("data/horarios_catalogo.json"),
    )

    session = None
    try:
        session = await authenticate(session_manager, auth_use_case, username, password)
        if session is None:
            print("\n✗ No se pudo autenticar tras varios intentos (captcha).")
            return

        print("\n✓ Autenticado. Extrayendo dashboard...\n", flush=True)
        report = await dashboard_use_case.execute(session, emit)

        print("\n===== RESULTADOS =====")
        p = report.student_profile
        print(f"\n[PERFIL] {'OK' if p else 'NULL'}")
        if p:
            print(f"  {p.full_name} | {p.school} | ingreso {p.admission_year}")
            print(f"  inst={p.institutional_email} cel={p.phone}")
            print(f"  dni={p.document} nac={p.birth_date} sexo={p.sex} "
                  f"ecivil={p.marital_status}")
            print(f"  dom={p.address}")
            print(f"  curricula={p.curriculum} condicion={p.condition}")
            print(f"  foto={'sí (' + str(len(p.photo_data_url)) + ' chars)' if p.photo_data_url else 'no'}")

        r = report.academic_record
        print(f"\n[RECORD] {'OK' if r else 'NULL'}")
        if r:
            print(f"  cred={r.accumulated_credits} ponderado={r.weighted_average} "
                  f"cond={r.condition} cursos={len(r.courses)}")
            for c in r.courses[:8]:
                print(f"  [{c.period}] {c.course_name[:34]:34} final={c.final_grade}")

        e = report.enrollment
        print(f"\n[MATRÍCULA] {'OK' if e else 'NULL'}")
        if e:
            print(f"  período={e.period} créditos={e.total_credits} cursos={len(e.courses)}")
            for c in e.courses:
                print(f"  {c.course_name}: grupo={c.group} docente={c.teacher}")

        print(f"\n[ASISTENCIA] cursos={len(report.attendance)} "
              f"slots_horario={len(report.schedule)}")
        for a in report.attendance[:5]:
            print(f"  {a.course_name}: {a.attendance_percentage}% "
                  f"({a.total_sessions} ses) riesgo={a.is_at_risk}")

        print("\n[HORARIO]")
        for sl in report.schedule:
            print(f"  {sl.day} {sl.start_time}-{sl.end_time} {sl.course_name} "
                  f"(grupo {sl.group}, {sl.teacher})")

        g = report.grade_report
        print(f"\n[NOTAS] periodo={g.period} cursos={len(g.courses)}")
        for c in g.courses[:8]:
            print(f"  {c.course_name}: U1={c.u1} U2={c.u2} U3={c.u3} "
                  f"final={c.final_grade} promedio={c.average}")

        print(f"\n[MEJOR HORARIO] opciones={len(report.optimized_schedules)}")
        for i, opt in enumerate(report.optimized_schedules, 1):
            secs = ", ".join(
                f"{s.course[:16]}→{s.section}" + (f"/{s.subgroup}" if s.subgroup else "")
                for s in opt.selections
            )
            print(f"  #{i} score={opt.score} días={opt.days} "
                  f"libres={opt.gap_minutes}min extremos={opt.extreme_sessions} | {secs}")
    finally:
        if session is not None:
            await session_manager.destroy_session(session.session_id)
        await session_manager.destroy_all()


if __name__ == "__main__":
    asyncio.run(main())
