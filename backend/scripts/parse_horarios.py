"""Convierte el XLSX de horarios oficiales en un catálogo JSON estructurado.

Cada hoja del libro es un ciclo + sección (A/B/C...). De cada una extrae la
metadata (ciclo, grupo, periodo), la lista de cursos (docente, T/P/L) y las
sesiones de la grilla (día, hora, tipo, aula, sub-grupo). Las duraciones de los
bloques de varias horas se recuperan de los rangos `mergeCells` del XLSX (el CSV
las pierde). Solo usa stdlib.

Uso:
    python3 scripts/parse_horarios.py [data/horarios_csv/horarios.xlsx] [salida.json]
"""
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from pathlib import Path

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

DAYS = {
    "lunes": "Lunes", "martes": "Martes", "miercoles": "Miércoles",
    "jueves": "Jueves", "viernes": "Viernes", "sabado": "Sábado",
}


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text).strip().lower()


def parse_ref(ref: str):
    m = re.match(r"([A-Z]+)(\d+)", ref)
    col = 0
    for ch in m.group(1):
        col = col * 26 + (ord(ch) - 64)
    return int(m.group(2)), col


def shared_strings(z: zipfile.ZipFile):
    try:
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(t.text or "" for t in si.iter(NS + "t")) for si in root.iter(NS + "si")]


def sheet_files(z: zipfile.ZipFile):
    wb = z.read("xl/workbook.xml").decode("utf-8")
    pairs = re.findall(r'<sheet[^>]*name="([^"]+)"[^>]*r:id="(rId\d+)"', wb)
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")
    relmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels))
    out = []
    for name, rid in pairs:
        target = relmap[rid].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        out.append((name, target))
    return out


def read_grid(z, sst, target):
    ws = ET.fromstring(z.read(target))
    cells = {}
    for c in ws.iter(NS + "c"):
        ref, t = c.get("r"), c.get("t")
        v, inline = c.find(NS + "v"), c.find(NS + "is")
        if t == "s" and v is not None:
            val = sst[int(v.text)]
        elif inline is not None:
            val = "".join(x.text or "" for x in inline.iter(NS + "t"))
        elif v is not None:
            val = v.text
        else:
            continue
        val = (val or "").strip()
        if val:
            cells[parse_ref(ref)] = val
    merges = {}
    for m in ws.iter(NS + "mergeCell"):
        a, b = m.get("ref").split(":")
        (r1, c1), (r2, c2) = parse_ref(a), parse_ref(b)
        merges[(r1, c1)] = r2 - r1 + 1
    return cells, merges


# ---- parsing de una hoja --------------------------------------------------

def find_label(cells, keyword):
    # Las etiquetas (Ciclo, Grupo, Periodo...) están en col B y el valor en col D.
    for (r, c), v in cells.items():
        if c == 2 and keyword in norm(v):
            return cells.get((r, 4), "").lstrip(": ").strip()
    return ""


def course_list(cells):
    header_row = next(
        (r for (r, c), v in cells.items() if norm(v) == "nro."), None
    )
    if header_row is None:
        return []
    cols = {norm(cells.get((header_row, c), "")): c for c in range(1, 20)}
    cn, cd, cc = cols.get("nro."), cols.get("docente"), cols.get("curso")
    ct, cp, cl = cols.get("t"), cols.get("p"), cols.get("l")
    courses = []
    r = header_row + 1
    while True:
        nro = cells.get((r, cn), "")
        curso = cells.get((r, cc), "")
        if not nro and not curso:
            break
        if curso:
            courses.append({
                "curso": curso,
                "docente": cells.get((r, cd)) or None,
                "t": _int(cells.get((r, ct))),
                "p": _int(cells.get((r, cp))),
                "l": _int(cells.get((r, cl))),
            })
        r += 1
        if r > header_row + 30:
            break
    return courses


def day_columns(cells):
    hora_row = next((r for (r, c), v in cells.items() if c == 2 and norm(v) == "hora"), None)
    if hora_row is None:
        return None, {}
    mapping = {}
    for c in range(1, 20):
        v = cells.get((hora_row, c), "")
        key = norm(v)
        if key in DAYS:
            mapping[c] = DAYS[key]
    return hora_row, mapping


def time_rows(cells, start_row):
    # Devuelve {fila: hora_inicio_min}. Hay dos formatos en el libro:
    #   - 12h con ":MM" y marcador "TARDE" (ej. Ciclo III: 07:00, ..., 02:00 pm)
    #   - 24h sin ":MM" (ej. Ciclo VI: 07-08, ..., 14-15, ..., 19-20)
    # Si aparece alguna hora >= 13 el formato es 24h y no desplazamos por TARDE.
    raw = []
    pm = False
    for r in range(start_row, start_row + 60):
        v = cells.get((r, 2))
        if not v:
            continue
        n = norm(v)
        if n.startswith("tarde") or n.startswith("noche"):
            pm = True
            continue
        if n.startswith("manana"):
            pm = False
            continue
        m = re.match(r"(\d{1,2})(?::(\d{2}))?\s*[-–]", v)
        if not m:
            continue
        raw.append([r, int(m.group(1)), int(m.group(2) or 0), pm])

    is_24h = any(h >= 13 for _, h, _, _ in raw)
    rows = {}
    for r, h, mm, after_tarde in raw:
        if not is_24h and after_tarde and h < 12:
            h += 12
        rows[r] = h * 60 + mm
    return rows


def _int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def hhmm(total_min):
    return f"{total_min // 60:02d}:{total_min % 60:02d}"


TYPE_PATTERNS = [
    ("teoria y practica", "Teoría y Práctica"),
    ("simulacion", "Laboratorio de Simulación"),
    ("laborat", "Laboratorio"),
    ("practica", "Práctica"),
    ("pract", "Práctica"),
    ("teoria", "Teoría"),
    ("toeria", "Teoría"),   # erratas del SUV
]


def parse_cell(text, courses):
    # "Balance Materia y Energía\n(Teoría) (I-2)" → curso/tipo/aula/sub-grupo.
    flat = re.sub(r"\s+", " ", text).strip()
    candidate = flat.split("(")[0].strip()
    curso = match_course(candidate, courses)
    if curso is None:
        return None  # ACREDITACIÓN, celdas sueltas, etc.

    low = norm(flat)
    tipo = next((label for pat, label in TYPE_PATTERNS if pat in low), None)

    sub = re.search(r"\bg\s*-?\s*([123])\b", low)
    subgrupo = f"G{sub.group(1)}" if sub else None

    aula = re.search(r"\(?\s*([A-Za-z]\s*-\s*\d+)\s*\)?", flat)
    aula_val = re.sub(r"\s+", "", aula.group(1)).upper() if aula else None
    # evitar capturar "G-1" como aula
    if aula_val and aula_val[0] in "G" and aula_val[1:].lstrip("-").isdigit():
        aula_val = None

    return {"curso": curso, "tipo": tipo, "aula": aula_val, "subgrupo": subgrupo}


STOP = {"ing", "para", "del", "las", "los"}


def match_course(candidate, courses):
    cand_tokens = [t for t in re.split(r"[^a-z0-9]+", norm(candidate)) if len(t) >= 3 and t not in STOP]
    if not cand_tokens:
        return None
    best, best_score = None, 0
    for c in courses:
        name_tokens = [t for t in re.split(r"[^a-z0-9]+", norm(c["curso"])) if len(t) >= 3]
        # Las abreviaturas de la grilla ("met", "num", "energ") son prefijos del
        # nombre completo; matcheamos por prefijo en cualquier dirección.
        score = sum(
            1 for t in cand_tokens
            if any(n.startswith(t) or t.startswith(n) for n in name_tokens)
        )
        if score > best_score:
            best, best_score = c["curso"], score
    return best if best_score >= 1 else None


def parse_sheet(cells, merges, sheet_name):
    grupo_raw = find_label(cells, "grupo")
    gm = re.search(r"(\d+)\s*\(?\s*([A-Za-z])", grupo_raw)
    section = {
        "hoja": sheet_name,
        "ciclo": find_label(cells, "ciclo") or None,
        "grupo": gm.group(1) if gm else None,
        "seccion": gm.group(2).upper() if gm else None,
        "anio": find_label(cells, "ano academic") or find_label(cells, "ano") or None,
        "semestre": find_label(cells, "semestre") or None,
        "periodo": find_label(cells, "periodo") or None,
        "cursos": course_list(cells),
        "sesiones": [],
    }

    hora_row, day_cols = day_columns(cells)
    if hora_row is None:
        return section
    rows = time_rows(cells, hora_row + 1)

    for r, start_min in rows.items():
        for col, day in day_cols.items():
            text = cells.get((r, col))
            if not text:
                continue
            span = merges.get((r, col), 1)
            parsed = parse_cell(text, section["cursos"])
            if parsed is None:
                continue
            docente = next(
                (c["docente"] for c in section["cursos"] if c["curso"] == parsed["curso"]),
                None,
            )
            section["sesiones"].append({
                "curso": parsed["curso"],
                "tipo": parsed["tipo"],
                "dia": day,
                "inicio": hhmm(start_min),
                "fin": hhmm(start_min + span * 60),
                "aula": parsed["aula"],
                "subgrupo": parsed["subgrupo"],
                "docente": docente,
            })
    return section


def main():
    xlsx = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/horarios_csv/horarios.xlsx")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/horarios_catalogo.json")

    z = zipfile.ZipFile(xlsx)
    sst = shared_strings(z)
    sections = []
    for name, target in sheet_files(z):
        cells, merges = read_grid(z, sst, target)
        sections.append(parse_sheet(cells, merges, name))

    catalog = {
        "fuente": str(xlsx.name),
        "generado": datetime.now().date().isoformat(),
        "secciones": sections,
    }
    out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Catálogo escrito en {out} ({len(sections)} secciones)")

    # Validación rápida: imprimir Ciclo III - B
    for s in sections:
        if s["ciclo"] == "III" and s["seccion"] == "B":
            print(f"\n=== Ciclo {s['ciclo']} - {s['seccion']} (grupo {s['grupo']}) "
                  f"| {len(s['cursos'])} cursos, {len(s['sesiones'])} sesiones ===")
            for ses in sorted(s["sesiones"], key=lambda x: (x["dia"], x["inicio"])):
                print(f"  {ses['dia']:9} {ses['inicio']}-{ses['fin']} "
                      f"{ses['curso'][:38]:38} {ses['tipo'] or '':22} "
                      f"aula={ses['aula']} sub={ses['subgrupo']}")


if __name__ == "__main__":
    main()
