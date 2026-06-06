<div align="center">

<img src="public/favicon.svg" alt="UNITRU Academic" width="72" />

# 🎨 Frontend — UNITRU Academic

![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-4-06B6D4?logo=tailwindcss&logoColor=white)
![Recharts](https://img.shields.io/badge/Recharts-3-FF6384)

</div>

Interfaz web que recibe los datos académicos extraídos del SUV a través de un WebSocket y los presenta en un dashboard con múltiples vistas, gráficas y herramientas de análisis.

---

## 🛠️ Stack

| Componente | Tecnología |
|---|---|
| Framework | Next.js 16.2 (App Router) |
| UI Library | React 19 |
| Tipado | TypeScript 5 |
| Estilos | Tailwind CSS 4 |
| Iconos | lucide-react 1.17 |
| Gráficas | Recharts 3.8 |

> **Nota**: Esta versión de Next.js (16.x) tiene cambios de ruptura respecto a versiones anteriores. Consulta `node_modules/next/dist/docs/` antes de modificar código relacionado con el framework.

---

## 📁 Estructura de carpetas

```
frontend/
├── app/
│   ├── layout.tsx          # RootLayout: fuentes, metadata, favicon
│   ├── page.tsx            # Máquina de estados: idle → login → loading → done/error
│   ├── globals.css         # Reset + variables Tailwind
│   └── icon.svg            # Favicon SVG (detectado automáticamente por Next.js)
├── features/               # Una carpeta por funcionalidad de negocio
│   ├── authentication/     # LoginForm, AuthenticationProgress
│   ├── landing/            # HeroScreen (pantalla de bienvenida)
│   ├── home/               # HomeView (métricas + horario de hoy + cursos en riesgo)
│   ├── grades/             # GradeCards + PredictionSection (predictor de notas)
│   ├── schedule/           # ScheduleGrid (horario semanal)
│   ├── schedule_optimizer/ # OptimizerView (mejores horarios combinados)
│   ├── attendance/         # AttendanceList (% de asistencia + alerta de riesgo)
│   ├── record/             # RecordTable (historial académico colapsable por período)
│   ├── analytics/          # AnalyticsView (gráficas de rendimiento histórico)
│   ├── profile/            # ProfileCard (datos personales + foto)
│   ├── dashboard/          # DashboardLayout, DashboardTabs, SidebarNav
│   └── error/              # ErrorScreen
├── infrastructure/
│   └── websocket/
│       └── websocket_client.ts   # connectAndFetch() — único punto de contacto con el backend
├── public/
│   ├── favicon.svg         # Ícono SVG (escudo UNT, compatible con todos los navegadores modernos)
│   └── logo.svg            # Logotipo horizontal para uso externo / OG images
└── Dockerfile
```

---

## 💻 Instalación y desarrollo local

```bash
# Instalar dependencias
npm install

# Servidor de desarrollo (hot reload)
npm run dev
# → http://localhost:3000

# Verificar tipos TypeScript + build de producción
npm run build

# Lint
npm run lint
```

---

## 🔧 Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `NEXT_PUBLIC_BACKEND_WS_URL` | `ws://localhost:8000/ws` | URL del WebSocket del backend. **Se incrusta en el bundle durante el build** — no se puede cambiar en runtime sin reconstruir. |

Para desarrollo local no se necesita configurar nada. Para producción, definir esta variable antes del build (Railway la inyecta como build arg automáticamente).

---

## 🔄 Flujo de la aplicación

La aplicación es una SPA con un estado centralizado en `app/page.tsx`:

```
idle ──[iniciar]──► login ──[credenciales]──► loading ──[dashboard_ready]──► done
                                                        └──[error]──────────► error
```

- **`idle`**: pantalla hero de bienvenida.
- **`login`**: formulario de credenciales (nunca se persisten en storage).
- **`loading`**: progreso de autenticación + extracción en tiempo real (eventos WebSocket).
- **`done`**: dashboard completo con 8 tabs.
- **`error`**: pantalla de error con opción de reintentar.

El backend emite un único evento `dashboard_ready` con el payload completo. A partir de ese momento, no se realizan más peticiones al servidor.

---

## 🎨 Sistema de diseño — Yellow UNT Edition

| Token | Valor | Uso |
|---|---|---|
| Amarillo acento | `#FFD200` | Elemento activo, highlights, badges |
| Fondo sidebar | `#0B0F14` | Sidebar, hero oscuro |
| Texto principal | `#1A1C1C` | Títulos, valores importantes |
| Texto secundario | `#5E5E5E` | Labels, subtítulos |
| Borde | `#E2E2E2` | Separadores, bordes de tarjeta |
| Error / Riesgo | `#BA1A1A` | Notas < 14, inhibición, alertas |

---

## 📱 Diseño responsivo

- **Desktop (≥ 768 px)**: sidebar fija a la izquierda (240 px), contenido a la derecha.
- **Mobile (< 768 px)**: sidebar oculta, accesible con botón hamburguesa (≡). Se abre como drawer deslizable con backdrop. El header sólo muestra el nombre del estudiante; las estadísticas se ocultan.

---

## 🚀 Build y despliegue

```bash
npm run build   # → .next/standalone (listo para Docker)
```

El `Dockerfile` usa build multi-stage:
1. **deps**: instala `node_modules`.
2. **builder**: ejecuta `next build` con las variables de entorno de build.
3. **runner**: imagen mínima `node:18-alpine` con el servidor standalone de Next.js.

Para despliegue en Railway, ver **[RAILWAY.md](../RAILWAY.md)**.

---

## ⚡ Notas técnicas

- **Sin routing entre páginas**: todo el estado del dashboard vive en `app/page.tsx` para evitar pasar `DashboardReport` entre rutas vía URL o contexto global.
- **Sin polling**: el progreso del scraping llega exclusivamente por eventos WebSocket.
- **Client Components mínimos**: sólo los componentes que usan estado o interacciones son `"use client"`.
- **CSV client-side**: la exportación de notas se genera en el navegador con `Blob`; no requiere backend.
- **Decimal como string**: las notas llegan como `string` desde el backend (para preservar precisión). El frontend las parsea a `number` sólo para comparaciones y formateo.
