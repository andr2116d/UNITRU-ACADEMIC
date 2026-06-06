<div align="center">

<img src="frontend/public/logo.svg" alt="UNITRU Academic" width="320" />

# 🎓 UNITRU Academic

**Tu vida académica del SUV, en una interfaz que sí da gusto usar.**

Dashboard personal para estudiantes de la **Universidad Nacional de Trujillo (UNT)**. Automatiza el acceso al Sistema Universitario Virtual (SUV) mediante un navegador headless, extrae toda tu información académica en una sola sesión y la presenta limpia, rápida y clara.

![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?logo=playwright&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

</div>

---

## ✨ Funcionalidades

| | Módulo | Descripción |
|:--:|---|---|
| 🔐 | **Autenticación** | Login automático con resolución de captcha por OCR local (Tesseract). Hasta 3 intentos por sesión. |
| 📝 | **Notas** | Tarjetas por curso con unidades (U1–U6), promedio parcial, P. Final e indicador de inhibición. |
| 🔮 | **Predictor de notas** | Dadas las unidades ya calificadas, genera **todas** las combinaciones de notas pendientes que permiten aprobar con promedio ≥ 14. |
| 🗓️ | **Horario semanal** | Grilla de lunes a viernes derivada de los registros de asistencia. Muestra docente, grupo y aula cuando están disponibles. |
| 🧩 | **Mejor horario** | Optimizador que encuentra el conjunto de secciones libre de conflictos con mejor puntaje (huecos, distribución de días, extremos). |
| ✅ | **Asistencia** | Lista de cursos con porcentaje de asistencia, barra de progreso y alerta **"EN RIESGO"**. |
| 📚 | **Récord académico** | Historial completo por períodos (notas definitivas, créditos, promedio ponderado). |
| 📊 | **Analíticas** | Gráficas y tabla con rendimiento período a período: tasa de aprobación, promedios, cursos repetidos. |
| 👤 | **Perfil** | Datos personales completos extraídos del SUV, incluyendo foto. |
| 📤 | **Exportar CSV** | Descarga de notas del ciclo actual directamente en el navegador. |

---

## 🛠️ Stack

| Capa | Tecnología |
|---|---|
| 🎨 **Frontend** | Next.js 16 · React 19 · TypeScript 5 · Tailwind CSS 4 |
| 📈 **Gráficas** | Recharts 3 |
| ⚙️ **Backend** | Python 3.12 · FastAPI · WebSocket |
| 🕷️ **Scraping** | Playwright (Chromium headless) |
| 👁️ **OCR** | Tesseract CLI |
| 🐳 **Contenedores** | Docker · Docker Compose |
| 🚀 **Deploy** | Railway (dos servicios independientes) |

---

## 🏗️ Arquitectura

Monorepo con dos servicios que se comunican únicamente por WebSocket.

```
┌─────────────────────────────────────────────────────────┐
│                      Navegador                          │
│  Next.js 16 (frontend)   ←── WebSocket ──→  FastAPI    │
│                                              (backend)  │
│                                               │         │
│                                          Playwright     │
│                                          (Chromium)     │
│                                               │         │
│                                          SUV UNITRU     │
└─────────────────────────────────────────────────────────┘
```

- **Backend** → 🧱 **Clean + Hexagonal Architecture** (dominio → aplicación → infraestructura).
- **Frontend** → 🧩 **Feature-Based Architecture** (una carpeta por funcionalidad).
- 🔒 Las credenciales **nunca se persisten**: existen sólo en la sesión WebSocket activa.

---

## 🚀 Inicio rápido con Docker

```bash
# Clona el repositorio
git clone <url-del-repo>
cd unitru-academic

# Levanta ambos servicios
docker compose up --build

# Abre en el navegador
open http://localhost:3000
```

> 💡 La primera build descarga Chromium y Tesseract (~500 MB). Las siguientes son instantáneas gracias al caché de capas.

---

## 💻 Desarrollo local

### ⚙️ Backend

> Requisitos: Python 3.12+, `brew install tesseract`

```bash
cd backend
pip install -r requirements.txt
playwright install chromium
uvicorn src.main:app --reload      # escucha en :8000
```

| Variable | Default | Descripción |
|---|---|---|
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Orígenes CORS permitidos (separados por coma) |
| `PORT` | `8000` | Puerto del servidor (Railway lo inyecta automáticamente) |

### 🎨 Frontend

> Requisitos: Node.js 18+

```bash
cd frontend
npm install
npm run dev      # escucha en :3000
```

| Variable | Default | Descripción |
|---|---|---|
| `NEXT_PUBLIC_BACKEND_WS_URL` | `ws://localhost:8000/ws` | URL del WebSocket del backend (se incrusta en build) |

---

## 🚂 Deploy en Railway

El proyecto contiene dos servicios (`backend/` y `frontend/`) con sus propios `Dockerfile` y `railway.json`, listos para desplegar.

👉 Ver **[RAILWAY.md](RAILWAY.md)** para instrucciones completas.

---

## 🔒 Seguridad y privacidad

- 🛡️ Las credenciales universitarias **nunca se almacenan**: existen sólo en memoria durante la sesión WebSocket activa y se descartan al cerrar la conexión.
- 🤖 El scraping usa un Chromium que suplanta las cabeceras de Chrome real, evitando bloqueos por detección de bots.
- 🔓 El certificado SSL del SUV es auto-firmado; el contexto de Playwright lo acepta explícitamente con `ignore_https_errors=True`.

---

## 🎯 ¿A quién va dirigido?

Estudiantes activos de la UNT que usan el SUV y buscan:

- ⚡ Ver sus notas y horario sin esperar a que el portal cargue.
- 🎯 Saber exactamente qué necesitan sacar en las próximas evaluaciones.
- 📖 Tener un historial académico legible y analizable de un vistazo.

---

<div align="center">
<sub>Hecho con 💛 para los estudiantes de la UNT</sub>
</div>
