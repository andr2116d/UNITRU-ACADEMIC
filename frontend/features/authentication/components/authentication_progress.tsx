"use client"

import { EVENT_LABELS } from "../types/authentication_types"

interface ProgressStep {
  event: string
  label: string
}

interface AuthenticationProgressProps {
  steps: ProgressStep[]
  currentEvent: string | null
  errorMessage: string | null
}

const ERROR_EVENTS = new Set([
  "authentication_failed",
  "grade_extraction_failed",
  "dashboard_extraction_failed",
  "error",
])

const STEP_GROUPS = [
  {
    id: "auth",
    label: "Autenticando",
    events: [
      "opening_suv",
      "loading_login",
      "downloading_captcha",
      "solving_captcha",
      "submitting_login",
      "selecting_student",
      "authentication_success",
    ],
  },
  {
    id: "profile",
    label: "Perfil y matrícula",
    events: [
      "extracting_profile",
      "profile_extraction_success",
      "profile_extraction_failed",
      "extracting_record",
      "record_extraction_success",
      "record_extraction_failed",
      "extracting_enrollment",
      "enrollment_extraction_success",
      "enrollment_extraction_failed",
    ],
  },
  {
    id: "data",
    label: "Notas y asistencia",
    events: [
      "extracting_attendance",
      "attendance_extraction_success",
      "attendance_extraction_failed",
      "extracting_grades",
      "extracting_academic_info",
      "extracting_courses",
      "grade_extraction_success",
      "optimizing_schedule",
      "schedule_optimized",
      "schedule_optimization_failed",
    ],
  },
  {
    id: "ready",
    label: "Dashboard listo",
    events: ["dashboard_ready"],
  },
]

export function AuthenticationProgress({
  steps,
  currentEvent,
  errorMessage,
}: AuthenticationProgressProps) {
  if (steps.length === 0 && !errorMessage) return null

  const hasError =
    !!errorMessage || steps.some((s) => ERROR_EVENTS.has(s.event))
  const isDone = steps.some((s) => s.event === "dashboard_ready")

  const activeGroupIndex = (() => {
    if (isDone) return STEP_GROUPS.length - 1
    for (let i = STEP_GROUPS.length - 1; i >= 0; i--) {
      if (steps.some((s) => STEP_GROUPS[i].events.includes(s.event))) return i
    }
    return 0
  })()

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#0B0F14] px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex justify-center">
          <div className="flex h-12 w-12 items-center justify-center bg-[#FFD200]">
            <span className="text-sm font-bold text-[#1A1C1C]">UNT</span>
          </div>
        </div>

        <h2 className="mb-8 text-center text-lg font-semibold text-white">
          {hasError
            ? "Ocurrió un error"
            : isDone
            ? "¡Dashboard listo!"
            : "Cargando tu información..."}
        </h2>

        <div className="flex flex-col gap-4">
          {STEP_GROUPS.map((group, i) => {
            const isCompleted = i < activeGroupIndex || isDone
            const isActive = i === activeGroupIndex && !isDone && !hasError
            const isError = hasError && i === activeGroupIndex

            return (
              <div key={group.id} className="flex items-center gap-3">
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
                    isError
                      ? "bg-[#BA1A1A] text-white"
                      : isCompleted
                      ? "bg-[#FFD200] text-[#1A1C1C]"
                      : isActive
                      ? "border-2 border-[#FFD200] text-[#FFD200]"
                      : "border border-[#2A2A2A] text-[#5E5E5E]"
                  }`}
                >
                  {isError ? "✕" : isCompleted ? "✓" : i + 1}
                </div>

                <div className="flex flex-1 flex-col gap-0.5">
                  <span
                    className={`text-sm font-medium ${
                      isError
                        ? "text-[#BA1A1A]"
                        : isCompleted
                        ? "text-white"
                        : isActive
                        ? "text-[#FFD200]"
                        : "text-[#5E5E5E]"
                    }`}
                  >
                    {group.label}
                  </span>
                  {isActive && currentEvent && (
                    <span className="text-xs text-[#D4D4D4]">
                      {EVENT_LABELS[currentEvent] ?? currentEvent}
                    </span>
                  )}
                </div>

                {isActive && (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#FFD200] border-t-transparent" />
                )}
              </div>
            )
          })}
        </div>

        {errorMessage && (
          <p className="mt-6 rounded border border-[#BA1A1A]/30 bg-[#BA1A1A]/10 px-4 py-3 text-sm text-[#BA1A1A]">
            {errorMessage}
          </p>
        )}
      </div>
    </div>
  )
}
