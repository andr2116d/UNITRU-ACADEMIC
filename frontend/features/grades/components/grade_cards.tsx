"use client"

import { useState } from "react"
import type { Enrollment } from "@/features/dashboard/types/dashboard_types"
import type { Course, GradeReport } from "../types/grade_types"

interface GradeCardsProps {
  report: GradeReport
  enrollment: Enrollment | null
}

type StatusColor = "yellow" | "green" | "red" | "gray"

function getCourseStatus(course: Course): { label: string; color: StatusColor } {
  if (course.inh) return { label: "INHIBIDO", color: "red" }
  if (course.final_grade) return { label: "COMPLETADO", color: "green" }
  const units = [course.u1, course.u2, course.u3, course.u4, course.u5, course.u6]
  if (units.some((u) => u !== null)) return { label: "EN CURSO", color: "yellow" }
  return { label: "POR INICIAR", color: "gray" }
}

const ACCENT_COLORS: Record<StatusColor, string> = {
  yellow: "bg-[#FFD200]",
  green: "bg-green-500",
  red: "bg-[#BA1A1A]",
  gray: "bg-[#E2E2E2]",
}

const BADGE_COLORS: Record<StatusColor, string> = {
  yellow: "bg-[#FFD200] text-[#1A1C1C]",
  green: "bg-green-100 text-green-700",
  red: "bg-[#BA1A1A]/10 text-[#BA1A1A]",
  gray: "bg-[#F5F5F5] text-[#5E5E5E]",
}

function UnitChip({ label, value }: { label: string; value: string | null }) {
  const passing = value !== null && parseFloat(value) >= 10.5
  const failing = value !== null && parseFloat(value) < 10.5
  return (
    <div className="flex flex-col items-center gap-1">
      <span className="text-[10px] text-[#BDBDBD]">{label}</span>
      <span
        className={`flex h-7 w-9 items-center justify-center rounded text-xs font-semibold ${
          passing
            ? "bg-[#FFD200] text-[#1A1C1C]"
            : failing
            ? "bg-[#BA1A1A]/10 text-[#BA1A1A]"
            : "bg-[#F5F5F5] text-[#BDBDBD]"
        }`}
      >
        {value ?? "—"}
      </span>
    </div>
  )
}

function PredictionSection({ prediction }: { prediction: Course["prediction"] }) {
  const [open, setOpen] = useState(false)
  if (!prediction) return null

  if (prediction.already_passes) {
    return (
      <div className="border-t border-[#E2E2E2] bg-green-50/60 px-4 py-2.5">
        <span className="text-xs font-semibold text-green-600">✓ Ya aprueba con las notas actuales</span>
      </div>
    )
  }

  if (!prediction.is_possible) {
    return (
      <div className="border-t border-[#E2E2E2] bg-[#BA1A1A]/5 px-4 py-2.5">
        <span className="text-xs font-semibold text-[#BA1A1A]">✗ Ya no es posible aprobar este ciclo</span>
      </div>
    )
  }

  const pendingLabels = prediction.pending.map((k) => k.toUpperCase())
  const pendingJoined = pendingLabels.join(" y ")

  return (
    <div className="border-t border-[#E2E2E2]">
      {/* Header colapsable — el mínimo es visible sin necesidad de abrir */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-3 px-4 py-2.5 text-left transition-colors hover:bg-[#F5F5F5]"
      >
        <div className="flex min-w-0 items-center gap-2">
          <span className="shrink-0 text-[10px] font-semibold uppercase tracking-wide text-[#5E5E5E]">
            Para aprobar
          </span>
          <span className="rounded bg-[#FFD200] px-1.5 py-0.5 text-xs font-bold text-[#1A1C1C]">
            {prediction.min_per_pending}
          </span>
          <span className="truncate text-[11px] text-[#5E5E5E]">mín. en {pendingJoined}</span>
        </div>
        <span className="shrink-0 text-[10px] text-[#BDBDBD]">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="flex flex-col gap-3 border-t border-[#E2E2E2] bg-[#F5F5F5] px-4 py-3">
          {/* Notas ya registradas + pendientes */}
          {Object.keys(prediction.known).length > 0 && (
            <div>
              <p className="mb-1.5 text-[10px] text-[#5E5E5E]">Notas registradas:</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(prediction.known).map(([k, v]) => (
                  <div key={k} className="flex flex-col items-center gap-0.5">
                    <span className="text-[9px] uppercase text-[#BDBDBD]">{k}</span>
                    <span className="rounded border border-[#E2E2E2] bg-white px-2 py-0.5 text-xs font-semibold text-[#1A1C1C]">
                      {v}
                    </span>
                  </div>
                ))}
                {prediction.pending.map((k) => (
                  <div key={k} className="flex flex-col items-center gap-0.5">
                    <span className="text-[9px] font-semibold uppercase text-[#1A1C1C]">{k}</span>
                    <span className="rounded bg-[#FFD200]/30 px-2 py-0.5 text-xs font-bold text-[#1A1C1C]">
                      ?
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Nota mínima recomendada */}
          <div className="rounded-lg border border-[#E2E2E2] bg-white px-3 py-2.5">
            <p className="mb-0.5 text-[10px] text-[#5E5E5E]">
              Si sacas lo mismo en las unidades pendientes:
            </p>
            <p className="text-sm text-[#5E5E5E]">
              Mínimo{" "}
              <span className="text-2xl font-bold text-[#1A1C1C]">
                {prediction.min_per_pending}
              </span>{" "}
              en {pendingJoined}
            </p>
          </div>

          {/* Tabla de todas las combinaciones que aprueban */}
          {prediction.combinations.length > 0 && (
            <div>
              <p className="mb-1 text-[10px] text-[#5E5E5E]">
                {prediction.combinations.length} combinaciones posibles (notas de 0 a 20):
              </p>
              <div className="max-h-36 overflow-y-auto rounded border border-[#E2E2E2] bg-white">
                <table className="w-full text-xs">
                  <thead className="sticky top-0 bg-[#F5F5F5]">
                    <tr className="border-b border-[#E2E2E2]">
                      {prediction.pending.map((k) => (
                        <th key={k} className="px-3 py-1.5 text-left font-semibold text-[#1A1C1C]">
                          {k.toUpperCase()}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {prediction.combinations.map((combo, i) => (
                      <tr key={i} className="border-b border-[#E2E2E2]/50 last:border-0">
                        {prediction.pending.map((k) => (
                          <td key={k} className="px-3 py-1 tabular-nums text-[#1A1C1C]">
                            {combo[k]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function CourseCard({ course, groupLabel }: { course: Course; groupLabel?: string }) {
  const [expanded, setExpanded] = useState(false)
  const status = getCourseStatus(course)

  const gradeDisplay = course.final_grade
    ? { label: "P. Final", value: course.final_grade }
    : course.average
    ? { label: "Promedio parcial", value: course.average + "*" }
    : null

  const units: { label: string; value: string | null }[] = [
    { label: "U1", value: course.u1 },
    { label: "U2", value: course.u2 },
    { label: "U3", value: course.u3 },
    { label: "U4", value: course.u4 },
    { label: "U5", value: course.u5 },
    { label: "U6", value: course.u6 },
  ]

  const details: { label: string; value: string | null }[] = [
    { label: "Sust", value: course.sust },
    { label: "NP", value: course.np },
    { label: "APLA", value: course.apla },
    { label: "P.Final", value: course.final_grade },
    { label: "INH", value: course.inh ? "Sí" : null },
  ]

  return (
    <div className="flex overflow-hidden rounded-lg border border-[#E2E2E2] bg-white">
      {/* Accent bar izquierda */}
      <div className={`w-1 shrink-0 ${ACCENT_COLORS[status.color]}`} />

      <div className="flex flex-1 flex-col">
        <div className="flex flex-col gap-3 p-4">
          {/* Badges */}
          <div className="flex flex-wrap items-center gap-2">
            <span className={`rounded px-2 py-0.5 text-xs font-semibold ${BADGE_COLORS[status.color]}`}>
              {status.label}
            </span>
            {course.attempt > 1 && (
              <span className="rounded bg-[#F5F5F5] px-2 py-0.5 text-xs text-[#5E5E5E]">
                Vez {course.attempt}
              </span>
            )}
          </div>

          {/* Nombre y código */}
          <div>
            <p className="font-semibold leading-snug text-[#1A1C1C]">
              {course.course_name}
            </p>
            <p className="mt-0.5 text-xs text-[#5E5E5E]">
              {course.course_id}
              {groupLabel && ` · ${groupLabel}`}
            </p>
          </div>

          {/* Chips de unidades */}
          <div className="flex flex-wrap gap-1">
            {units.map(({ label, value }) => (
              <UnitChip key={label} label={label} value={value} />
            ))}
          </div>

          {/* Nota principal */}
          {gradeDisplay && (
            <div className="flex items-baseline gap-1.5">
              <span className="text-xs text-[#5E5E5E]">{gradeDisplay.label}:</span>
              <span
                className={`text-2xl font-bold tabular-nums ${
                  parseFloat(gradeDisplay.value) >= 10.5
                    ? "text-[#1A1C1C]"
                    : "text-[#BA1A1A]"
                }`}
              >
                {gradeDisplay.value}
              </span>
            </div>
          )}
        </div>

        {/* Toggle para ver detalles adicionales */}
        <button
          onClick={() => setExpanded((v) => !v)}
          className="flex w-full items-center justify-between border-t border-[#E2E2E2] px-4 py-2 text-xs text-[#5E5E5E] transition-colors hover:bg-[#F5F5F5]"
        >
          <span>Ver detalles</span>
          <span className="text-[10px]">{expanded ? "▲" : "▼"}</span>
        </button>

        {expanded && (
          <div className="border-t border-[#E2E2E2] px-4 py-3">
            <div className="grid grid-cols-5 gap-2">
              {details.map(({ label, value }) => (
                <div key={label} className="flex flex-col items-center gap-1">
                  <span className="text-[10px] text-[#5E5E5E]">{label}</span>
                  <span
                    className={`text-xs font-semibold ${
                      value === "Sí"
                        ? "text-[#BA1A1A]"
                        : value && !isNaN(parseFloat(value))
                        ? parseFloat(value) >= 10.5
                          ? "text-[#1A1C1C]"
                          : "text-[#BA1A1A]"
                        : "text-[#BDBDBD]"
                    }`}
                  >
                    {value ?? "—"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        <PredictionSection prediction={course.prediction} />
      </div>
    </div>
  )
}

export function GradeCards({ report, enrollment }: GradeCardsProps) {
  // Enriquece cada curso con el grupo de la matrícula (cruce por course_id).
  const groupByCode: Record<string, string> = {}
  if (enrollment) {
    for (const c of enrollment.courses) {
      groupByCode[c.course_id] = `Grupo ${c.group}`
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-4 text-sm text-[#5E5E5E]">
        {report.period && (
          <span>
            <span className="font-semibold text-[#1A1C1C]">Período:</span>{" "}
            {report.period}
          </span>
        )}
        {report.payment_order && (
          <span>
            <span className="font-semibold text-[#1A1C1C]">Orden de pago:</span>{" "}
            {report.payment_order}
          </span>
        )}
        {report.enrollment_type && (
          <span>
            <span className="font-semibold text-[#1A1C1C]">Tipo:</span>{" "}
            {report.enrollment_type}
          </span>
        )}
      </div>

      {report.courses.length === 0 ? (
        <p className="text-sm text-[#5E5E5E]">No se encontraron cursos.</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {report.courses.map((course, i) => (
            <CourseCard
              key={course.course_id + i}
              course={course}
              groupLabel={groupByCode[course.course_id]}
            />
          ))}
        </div>
      )}
    </div>
  )
}
