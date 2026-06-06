"use client"

import { useState } from "react"
import type { AcademicRecord, CourseHistory } from "@/features/dashboard/types/dashboard_types"

interface RecordTableProps {
  record: AcademicRecord
  currentPeriod: string | null
  currentAverages: Record<string, string>
}

const normalizeName = (s: string) => s.trim().toUpperCase().replace(/\s+/g, " ")

export function RecordTable({ record, currentPeriod, currentAverages }: RecordTableProps) {
  const periods = Array.from(new Set(record.courses.map((c) => c.period))).reverse()
  const [expanded, setExpanded] = useState<Set<string>>(new Set(periods.slice(0, 1)))

  const toggle = (period: string) => {
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(period)) next.delete(period)
      else next.add(period)
      return next
    })
  }

  const byPeriod = (period: string): CourseHistory[] =>
    record.courses.filter((c) => c.period === period)

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-[#5E5E5E]">
        <span>
          Promedio ponderado:{" "}
          <b className="text-[#1A1C1C]">{formatAverage(record.weighted_average)}</b>
        </span>
        <span>
          Créditos acumulados:{" "}
          <b className="text-[#1A1C1C]">{record.accumulated_credits}</b>
        </span>
        <span>
          Condición:{" "}
          <b className="text-[#1A1C1C]">{record.condition}</b>
        </span>
        {record.payment_status && <PaymentBadge status={record.payment_status} />}
      </div>

      {periods.map((period) => {
        const courses = byPeriod(period)
        const isOpen = expanded.has(period)
        return (
          <div
            key={period}
            className="overflow-hidden rounded-lg border border-[#E2E2E2]"
          >
            <button
              onClick={() => toggle(period)}
              className="flex w-full items-center justify-between bg-[#F5F5F5] px-4 py-3 text-left transition-colors hover:bg-[#EBEBEB]"
            >
              <span className="font-semibold text-[#1A1C1C]">{period}</span>
              <span className="text-xs text-[#5E5E5E]">
                {isOpen ? "▲" : "▼"} {courses.length} cursos
              </span>
            </button>
            {isOpen && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#E2E2E2] text-left text-xs font-semibold uppercase tracking-wide text-[#5E5E5E]">
                      <th className="px-4 py-2.5">ID</th>
                      <th className="px-4 py-2.5">Curso</th>
                      <th className="px-4 py-2.5 text-center">Vez</th>
                      <th className="px-4 py-2.5 text-center">Tipo</th>
                      <th className="px-4 py-2.5 text-center">Créd.</th>
                      <th className="px-4 py-2.5 text-center">P. Final</th>
                      <th className="px-4 py-2.5 text-center">Inh.</th>
                    </tr>
                  </thead>
                  <tbody>
                    {courses.map((c, i) => (
                      <tr
                        key={i}
                        className="border-b border-[#E2E2E2] last:border-0 transition-colors hover:bg-[#F5F5F5]"
                      >
                        <td className="px-4 py-2.5 text-xs text-[#5E5E5E]">
                          {c.course_id}
                        </td>
                        <td className="px-4 py-2.5 text-[#1A1C1C]">
                          {c.course_name}
                        </td>
                        <td className="px-4 py-2.5 text-center text-[#5E5E5E]">
                          {c.attempt}
                        </td>
                        <td className="px-4 py-2.5 text-center text-xs text-[#5E5E5E]">
                          {c.course_type}
                        </td>
                        <td className="px-4 py-2.5 text-center text-[#5E5E5E]">
                          {c.credits}
                        </td>
                        <td className="px-4 py-2.5 text-center">
                          <GradeCell
                            grade={c.final_grade}
                            partial={
                              !c.final_grade && c.period === currentPeriod
                                ? (currentAverages[normalizeName(c.course_name)] ?? null)
                                : null
                            }
                          />
                        </td>
                        <td className="px-4 py-2.5 text-center">
                          {c.is_disabled && (
                            <span className="rounded bg-[#BA1A1A]/10 px-1.5 py-0.5 text-xs font-semibold text-[#BA1A1A]">
                              INH
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

function formatAverage(value: string): string {
  const n = parseFloat(value)
  return Number.isFinite(n) ? n.toFixed(2) : "—"
}

function PaymentBadge({ status }: { status: string }) {
  const isPaid = status === "PAGADA"
  return (
    <span
      className={`rounded px-2.5 py-0.5 text-xs font-semibold ${
        isPaid ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
      }`}
    >
      {status}
    </span>
  )
}

function GradeCell({
  grade,
  partial = null,
}: {
  grade: string | null
  partial?: string | null
}) {
  // El P. Final del período en curso aún no se publica; mostramos el promedio
  // parcial calculado (en cursiva) para que no quede vacío.
  if (!grade && partial) {
    const value = parseFloat(partial)
    const color = value >= 14 ? "text-blue-500/80" : "text-[#BA1A1A]/70"
    return (
      <span
        className={`italic ${color}`}
        title="Promedio parcial (período en curso)"
      >
        {partial}*
      </span>
    )
  }
  if (!grade) return <span className="text-[#BDBDBD]">—</span>
  const value = parseFloat(grade)
  const color = value >= 14 ? "text-blue-600" : "text-[#BA1A1A]"
  return <span className={`font-semibold ${color}`}>{grade}</span>
}
