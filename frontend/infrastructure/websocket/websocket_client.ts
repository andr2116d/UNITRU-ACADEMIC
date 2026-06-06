import type { WebSocketMessage } from "@/features/authentication/types/authentication_types"
import type { DashboardReport } from "@/features/dashboard/types/dashboard_types"

// Configurable en build (Docker/despliegue). El navegador del alumno se conecta
// a esta URL, por eso apunta al backend público, no a un nombre interno de red.
const BACKEND_WS_URL =
  process.env.NEXT_PUBLIC_BACKEND_WS_URL ?? "ws://localhost:8000/ws"

export interface WebSocketCallbacks {
  onEvent: (event: string, data: Record<string, unknown>) => void
  onDashboardReport: (report: DashboardReport) => void
  onError: (message: string) => void
  onClose: () => void
}

export function connectAndFetch(
  username: string,
  password: string,
  callbacks: WebSocketCallbacks
): () => void {
  const ws = new WebSocket(BACKEND_WS_URL)

  ws.onopen = () => {
    ws.send(JSON.stringify({ username, password }))
  }

  ws.onmessage = (event) => {
    let message: WebSocketMessage
    try {
      message = JSON.parse(event.data)
    } catch {
      callbacks.onError("Respuesta inválida del servidor")
      return
    }

    if (message.event === "dashboard_ready") {
      callbacks.onDashboardReport(message.data as unknown as DashboardReport)
    } else if (message.event === "error") {
      const data = message.data as { message?: string }
      callbacks.onError(data.message ?? "Error desconocido")
    } else {
      callbacks.onEvent(message.event, message.data)
    }
  }

  ws.onerror = () => {
    callbacks.onError("No se pudo conectar al servidor")
  }

  ws.onclose = () => {
    callbacks.onClose()
  }

  return () => ws.close()
}
