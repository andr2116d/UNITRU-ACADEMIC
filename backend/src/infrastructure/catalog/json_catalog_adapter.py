import json
from pathlib import Path

from ...application.ports.schedule_catalog_port import ScheduleCatalogPort
from ...domain.entities.schedule_catalog import CatalogSession, ScheduleCatalog


def _to_minutes(hhmm: str) -> int:
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


class JsonCatalogAdapter(ScheduleCatalogPort):
    """Carga el catálogo desde el JSON generado por scripts/parse_horarios.py.

    Cuando se mueva a 'el frontend envía el enlace', un GoogleSheetsCatalogAdapter
    implementará el mismo puerto descargando + parseando desde la URL en vivo."""

    def __init__(self, path: str) -> None:
        self._path = Path(path)

    def load(self) -> ScheduleCatalog:
        data = json.loads(self._path.read_text(encoding="utf-8"))
        sessions = []
        for section in data.get("secciones", []):
            for ses in section.get("sesiones", []):
                sessions.append(
                    CatalogSession(
                        course=ses["curso"],
                        cycle=section.get("ciclo"),
                        section=section.get("seccion"),
                        group=section.get("grupo"),
                        tipo=ses.get("tipo"),
                        day=ses["dia"],
                        start_min=_to_minutes(ses["inicio"]),
                        end_min=_to_minutes(ses["fin"]),
                        room=ses.get("aula"),
                        subgroup=ses.get("subgrupo"),
                        teacher=ses.get("docente"),
                    )
                )
        return ScheduleCatalog(sessions=sessions)
