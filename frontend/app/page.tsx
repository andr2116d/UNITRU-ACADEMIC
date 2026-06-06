"use client"

import { useCallback, useState } from "react"
import { AuthenticationProgress } from "@/features/authentication/components/authentication_progress"
import { LoginForm } from "@/features/authentication/components/login_form"
import type { LoginCredentials } from "@/features/authentication/types/authentication_types"
import { DashboardLayout } from "@/features/dashboard/components/dashboard_layout"
import type { DashboardReport } from "@/features/dashboard/types/dashboard_types"
import { ErrorScreen } from "@/features/error/components/error_screen"
import { HeroSection } from "@/features/landing/components/hero_section"
import { connectAndFetch } from "@/infrastructure/websocket/websocket_client"

interface ProgressStep {
  event: string
  label: string
}

type AppView = "hero" | "login" | "loading" | "done" | "error"

export default function Home() {
  const [view, setView] = useState<AppView>("hero")
  const [progressSteps, setProgressSteps] = useState<ProgressStep[]>([])
  const [currentEvent, setCurrentEvent] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [dashboard, setDashboard] = useState<DashboardReport | null>(null)

  const handleLogin = useCallback((credentials: LoginCredentials) => {
    setView("loading")
    setProgressSteps([])
    setCurrentEvent(null)
    setErrorMessage(null)
    setDashboard(null)

    connectAndFetch(credentials.username, credentials.password, {
      onEvent: (event) => {
        setCurrentEvent(event)
        setProgressSteps((prev) => [...prev, { event, label: event }])
      },
      onDashboardReport: (report) => {
        setDashboard(report)
        setView("done")
        setProgressSteps((prev) => [
          ...prev,
          { event: "dashboard_ready", label: "Dashboard listo" },
        ])
      },
      onError: (message) => {
        setErrorMessage(message)
        setView("error")
        setProgressSteps((prev) => [
          ...prev,
          { event: "error", label: "Error" },
        ])
      },
      onClose: () => {
        setView((current) => {
          if (current === "loading") {
            setErrorMessage("La conexión se cerró inesperadamente")
            return "error"
          }
          return current
        })
      },
    })
  }, [])

  const handleReset = () => {
    setView("login")
    setProgressSteps([])
    setCurrentEvent(null)
    setErrorMessage(null)
    setDashboard(null)
  }

  if (view === "hero") {
    return <HeroSection onStart={() => setView("login")} />
  }

  if (view === "login") {
    return <LoginForm onSubmit={handleLogin} onBack={() => setView("hero")} />
  }

  if (view === "loading") {
    return (
      <AuthenticationProgress
        steps={progressSteps}
        currentEvent={currentEvent}
        errorMessage={errorMessage}
      />
    )
  }

  if (view === "error") {
    return <ErrorScreen message={errorMessage} onRetry={() => setView("login")} />
  }

  if (view === "done" && dashboard) {
    return <DashboardLayout report={dashboard} onReset={handleReset} />
  }

  return null
}
