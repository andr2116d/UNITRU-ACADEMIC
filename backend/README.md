<div align="center">

<img src="../frontend/public/favicon.svg" alt="UNITRU Academic" width="72" />

# ⚙️ Backend — UNITRU Academic

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?logo=playwright&logoColor=white)
![Tesseract](https://img.shields.io/badge/Tesseract-OCR-5C3EE8)

</div>

Servicio Python que automatiza el acceso al SUV de la UNT mediante Playwright, resuelve el captcha con OCR local y entrega toda la información académica a través de un WebSocket en una sola sesión.

---

## 🛠️ Stack

| Componente | Tecnología |
|---|---|
| Framework web | FastAPI |
| Servidor ASGI | Uvicorn |
| Automatización | Playwright (Chromium headless) |
| OCR | Tesseract (vía stdin, no pytesseract) |
| Procesamiento de imagen | Pillow |
| Runtime | Python 3.12 |

---

## 📦 Instalación

```bash
# Dependencias Python
pip install -r requirements.txt

# Binario del navegador headless
playwright install chromium

# OCR (macOS)
brew install tesseract

# OCR (Ubuntu/Debian)
apt-get install tesseract-ocr
```

### Iniciar el servidor

```bash
uvicorn src.main:app --reload
# WebSocket disponible en ws://localhost:8000/ws
```

---

## 🔧 Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Orígenes CORS permitidos (separados por coma) |
| `PORT` | `8000` | Puerto de escucha (Railway lo inyecta automáticamente) |

---

## 📁 Estructura del proyecto

```
backend/
├── src/
│   ├── main.py                        # Wiring de dependencias (DI manual)
│   ├── domain/
│   │   ├── entities/                  # Entidades puras de negocio
│   │   │   ├── course.py
│   │   │   ├── academic_record.py
│   │   │   ├── attendance.py
│   │   │   ├── dashboard_report.py
│   │   │   ├── enrollment.py
│   │   │   ├── grade_report.py
│   │   │   ├── student_profile.py
│   │   │   └── browser_session.py
│   │   └── services/                  # Lógica de dominio pura (sin I/O)
│   │       ├── grade_predictor.py     # Combinaciones de notas para aprobar
│   │       ├── academic_analytics.py  # Estadísticas históricas por período
│   │       ├── grade_analytics.py     # Promedio por curso
│   │       ├── schedule_builder.py    # Horario desde registros de asistencia
│   │       └── schedule_optimizer.py  # Mejor combinación de secciones
│   ├── application/
│   │   ├── ports/                     # Interfaces (puertos hexagonales)
│   │   ├── use_cases/
│   │   │   ├── authenticate_student_use_case.py
│   │   │   └── extract_full_dashboard_use_case.py
│   │   └── dtos/                      # Objetos de transferencia entre capas
│   ├── infrastructure/
│   │   ├── playwright/                # Adaptadores de automatización SUV
│   │   │   ├── session_manager.py
│   │   │   ├── sidebar_navigation.py
│   │   │   ├── suv_authenticator.py
│   │   │   ├── suv_grade_extractor.py
│   │   │   ├── suv_record_extractor.py
│   │   │   ├── suv_attendance_extractor.py
│   │   │   ├── suv_enrollment_extractor.py
│   │   │   └── suv_profile_extractor.py
│   │   ├── ocr/
│   │   │   └── tesseract_adapter.py   # Resolución de captcha por stdin
│   │   └── catalog/
│   │       └── json_catalog_adapter.py
│   └── presentation/
│       └── websocket/
│           └── websocket_handler.py   # Único endpoint: /ws
├── scripts/
│   ├── test_full_dashboard.py         # E2E contra el SUV real
│   ├── download_horarios.py           # Descarga catálogo desde Google Sheets
│   ├── parse_horarios.py              # XLSX → horarios_catalogo.json
│   ├── test_optimizer.py              # Prueba el optimizador de horarios
│   └── inspect_suv_login.py          # Inspecciona selectores del SUV
├── data/
│   └── horarios_catalogo.json         # Catálogo de horarios (generado por scripts)
├── Dockerfile
├── railway.json
└── requirements.txt
```

---

## 🏗️ Arquitectura en capas

El proyecto aplica **Clean Architecture + Arquitectura Hexagonal**. Las dependencias sólo apuntan hacia el dominio.

```
Presentation (WebSocket)
       ↓
Application (Use Cases + Ports)
       ↓
Domain (Entities + Services)
       ↑
Infrastructure (Playwright + OCR + Catalog)
```

### 🔄 Flujo de una sesión

1. El frontend abre un WebSocket en `/ws` y envía `{ username, password }`.
2. `SessionManager` crea una `BrowserSession` (Chromium) ligada al ciclo de vida del WebSocket.
3. `AuthenticateStudentUseCase` ejecuta: abre el SUV → descarga captcha → OCR → login → selecciona perfil "Alumno".
4. `ExtractFullDashboardUseCase` navega por todos los módulos en una sola sesión:
   - Perfil → Récord académico → Ficha de matrícula → Asistencia → Notas
5. El handler emite `dashboard_ready` con el payload completo.
6. Al cerrar la conexión, la sesión se destruye en orden: Page → BrowserContext → Browser.

### 🧠 Módulos de dominio destacados

| Servicio | Responsabilidad |
|---|---|
| `grade_predictor` | Genera todas las combinaciones (0–20) de notas en unidades pendientes con promedio ≥ 14 (ROUND_HALF_UP) |
| `academic_analytics` | Agrupa el historial por período y calcula tasas de aprobación, promedios y cursos repetidos |
| `schedule_builder` | Deduplica sesiones de asistencia por (día, hora, curso) para construir el horario semanal |
| `schedule_optimizer` | Combina secciones del catálogo buscando el mejor horario libre de conflictos |

---

## 🧪 Scripts de diagnóstico

Los scripts operan contra el SUV real; **nunca hardcodear credenciales**.

```bash
# Verifica selectores actuales del formulario de login
python3 scripts/inspect_suv_login.py

# E2E completo: login + extracción de los 4 módulos + imprime resultado
python3 scripts/test_full_dashboard.py <usuario> <contraseña>

# Descarga el catálogo de horarios desde Google Sheets
python3 scripts/download_horarios.py <url_google_sheets>

# Convierte el XLSX descargado a horarios_catalogo.json
python3 scripts/parse_horarios.py

# Prueba el optimizador con cursos específicos
python3 scripts/test_optimizer.py "Cálculo I" "Física I"
```

---

## ⚡ Notas de implementación

- **Captcha**: Tesseract se invoca via `subprocess` pasando la imagen por stdin (pytesseract falla en esta máquina porque Leptonica no puede leer el archivo temporal). Se aplica umbral bajo (`< 60`) para eliminar ruido gris, escalado 2–3×, y votación entre modos PSM 6 y 7.
- **SSL del SUV**: el certificado no es de confianza en Chromium; el contexto se crea con `ignore_https_errors=True`.
- **Anti-detección**: se suplanta el User-Agent de Chrome real y se oculta `navigator.webdriver`.
- **Notas**: se usan `Decimal` (nunca `float`) para representar notas. Las no publicadas son `None`, nunca `0` o `""`.
- **Sidebar del SUV**: comienza cerrada; hay que abrirla antes de hacer clic en cualquier ítem del menú. Toda la lógica de navegación está centralizada en `sidebar_navigation.py`.
