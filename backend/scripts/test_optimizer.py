"""Prueba del optimizador de horarios sobre el catálogo JSON.

Uso:
    python3 scripts/test_optimizer.py [curso1] [curso2] ...

Sin argumentos usa los 3 cursos del alumno de prueba (Ciclo III).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.application.use_cases.optimize_schedule_use_case import OptimizeScheduleUseCase
from src.infrastructure.catalog.json_catalog_adapter import JsonCatalogAdapter

DEFAULT_COURSES = [
    "BALANCE DE MATERIA Y ENERGIA",
    "METODOS NUMERICOS PARA INGENIERIA QUIMICA",
    "RECURSOS NATURALES",
]

CICLO_III_COMPLETO = [
    "Química Orgánica I",
    "Físicoquímica I",
    "Balance de Materia y Energía",
    "Métodos Numéricos para Ingeniería Química",
    "Física General II",
    "Recursos Naturales",
]


def hhmm(total_min: int) -> str:
    return f"{total_min // 60:02d}:{total_min % 60:02d}"


def show(title, course_names, use_case):
    schedules, missing = use_case.execute(course_names, top_n=3)
    print(f"\n========== {title} ==========")
    if missing:
        print("  (sin oferta en el catálogo:", ", ".join(missing), ")")
    if not schedules:
        print("  No hay combinación sin choques.")
        return
    for rank, sched in enumerate(schedules, 1):
        secs = ", ".join(
            f"{s.course[:18]}→{s.cycle}-{s.section}" + (f"/{s.subgroup}" if s.subgroup else "")
            for s in sched.selections
        )
        print(f"\n  #{rank} puntaje={sched.score} | {sched.days} días | "
              f"{sched.gap_minutes//60}h{sched.gap_minutes%60:02d} libres | {sched.extreme_sessions} extremos")
        print(f"     secciones: {secs}")
        for s in sorted(sched.sessions, key=lambda x: (x.day, x.start_min)):
            print(f"       {s.day:9} {hhmm(s.start_min)}-{hhmm(s.end_min)} "
                  f"{s.course[:34]:34} {s.tipo or '':22} {('('+s.section+')')}")


def main() -> None:
    adapter = JsonCatalogAdapter("data/horarios_catalogo.json")
    use_case = OptimizeScheduleUseCase(adapter)

    if len(sys.argv) > 1:
        show("CURSOS DADOS", sys.argv[1:], use_case)
        return

    show("ALUMNO DE PRUEBA (3 cursos, Ciclo III)", DEFAULT_COURSES, use_case)
    show("CICLO III COMPLETO (6 cursos, combinando A/B)", CICLO_III_COMPLETO, use_case)


if __name__ == "__main__":
    main()
