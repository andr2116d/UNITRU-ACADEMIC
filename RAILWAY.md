# Despliegue en Railway

El proyecto son **dos servicios** (backend y frontend) desplegados desde el mismo
repo. Cada uno tiene su `Dockerfile` y su `railway.json`.

## 1. Crear los dos servicios

En el proyecto de Railway, "New → GitHub Repo" (este repo) **dos veces**:

| Servicio | Root Directory | Detecta |
|---|---|---|
| `backend`  | `backend`  | `backend/Dockerfile` + `backend/railway.json` (healthcheck `/health`) |
| `frontend` | `frontend` | `frontend/Dockerfile` + `frontend/railway.json` |

> El **Root Directory** se setea en Settings del servicio (Railway monorepo).

## 2. Generar dominios públicos

En cada servicio: Settings → Networking → **Generate Domain**.
Quedan, por ejemplo:
- backend  → `unitru-backend.up.railway.app`
- frontend → `unitru-academic.up.railway.app`

## 3. Variables

**Servicio `backend`** (Variables):
```
ALLOWED_ORIGINS = https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
```

**Servicio `frontend`** (Variables) — se usa como **build arg** (la URL se incrusta
en el bundle, por eso debe estar antes/durante el build):
```
NEXT_PUBLIC_BACKEND_WS_URL = wss://${{backend.RAILWAY_PUBLIC_DOMAIN}}/ws
```

`${{servicio.RAILWAY_PUBLIC_DOMAIN}}` es una referencia entre servicios que Railway
resuelve solo (no hace falta pegar el dominio a mano). Nota el `wss://` (TLS) y el
`/ws` final.

`PORT` lo inyecta Railway automáticamente: el backend ya arranca con `${PORT}` y el
server standalone de Next lo respeta. No hay que setearlo.

## 4. Desplegar

Railway construye y despliega al hacer push. Si cambiaste `NEXT_PUBLIC_BACKEND_WS_URL`
después del primer build, **redeploy del frontend** (es build-time).

Abrir el dominio del frontend.

## Notas

- **Backend pesado**: la imagen trae Chromium + Tesseract; la primera build tarda y
  el runtime de un navegador headless necesita RAM (recomendado ≥1 GB para el servicio
  `backend`).
- **WSS detrás del proxy**: el backend corre `uvicorn ... --proxy-headers
  --forwarded-allow-ips=*`, necesario para el WebSocket tras el TLS de Railway.
- **Catálogo de horarios**: va horneado en la imagen del backend
  (`data/horarios_catalogo.json`). Para actualizarlo, re-corre `scripts/parse_horarios.py`,
  commitea el JSON y redeploy (o, a futuro, el adaptador de enlace en vivo).
- **Credenciales**: nunca se persisten; viven solo durante la sesión WebSocket.
- Para local sigue sirviendo `docker compose up --build` (ver `docker-compose.yml`).
