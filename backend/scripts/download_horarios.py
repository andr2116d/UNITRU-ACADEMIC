"""Descarga cada hoja del Google Sheets de horarios oficiales como CSV.

El enlace/los gids pueden cambiar, así que recibe la URL (o el ID) del
spreadsheet como argumento y enumera las hojas dinámicamente: lee los nombres
desde el export XLSX (un zip) y baja cada hoja por nombre vía el endpoint gviz.
Solo usa stdlib. La hoja debe ser visible con el enlace (anyone-with-link).

Uso:
    python3 scripts/download_horarios.py <url_o_id_del_sheet> [carpeta_destino]

Por defecto guarda en backend/data/horarios_csv/.
"""
import io
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

EXPORT_XLSX = "https://docs.google.com/spreadsheets/d/{id}/export?format=xlsx"
GVIZ_CSV = "https://docs.google.com/spreadsheets/d/{id}/gviz/tq?tqx=out:csv&sheet={sheet}"


def extract_spreadsheet_id(url_or_id: str) -> str:
    # Tolera URLs con /u/<n>/ (cuenta de Google): .../spreadsheets/u/2/d/<ID>/...
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url_or_id)
    return match.group(1) if match else url_or_id.strip()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def download_workbook(spreadsheet_id: str, out_dir: Path) -> list[str]:
    # El CSV pierde las celdas combinadas verticales (bloques de varias horas
    # quedan solo en la primera fila). El XLSX conserva los rangos `mergeCells`,
    # así que lo guardamos completo para recuperar las duraciones en el parser.
    data = fetch(EXPORT_XLSX.format(id=spreadsheet_id))
    (out_dir / "horarios.xlsx").write_bytes(data)
    workbook = zipfile.ZipFile(io.BytesIO(data)).read("xl/workbook.xml").decode("utf-8")
    return re.findall(r'<sheet[^>]*name="([^"]+)"', workbook)


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"\s+", " ", name).strip()
    cleaned = re.sub(r"[^\w\- ]", "_", cleaned)
    return f"{cleaned}.csv"


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    spreadsheet_id = extract_spreadsheet_id(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/horarios_csv")
    out_dir.mkdir(parents=True, exist_ok=True)

    names = download_workbook(spreadsheet_id, out_dir)
    print(f"Spreadsheet {spreadsheet_id}: {len(names)} hojas (+ horarios.xlsx)")

    for name in names:
        url = GVIZ_CSV.format(id=spreadsheet_id, sheet=urllib.parse.quote(name))
        try:
            csv_bytes = fetch(url)
        except Exception as exc:  # noqa: BLE001 — script de datos, queremos verlo
            print(f"  ✗ {name!r}: {exc}")
            continue
        path = out_dir / safe_filename(name)
        path.write_bytes(csv_bytes)
        print(f"  ✓ {name!r} → {path.name} ({len(csv_bytes)} bytes)")
        time.sleep(0.4)  # cortesía con el endpoint

    print(f"\nListo. CSVs en {out_dir.resolve()}")


if __name__ == "__main__":
    main()
