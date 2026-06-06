import type { AttendanceSummary } from "@/features/dashboard/types/dashboard_types"

interface AttendanceListProps {
  summaries: AttendanceSummary[]
}

export function AttendanceList({ summaries }: AttendanceListProps) {
  if (summaries.length === 0) {
    return (
      <p className="text-sm text-[#5E5E5E]">
        No hay datos de asistencia disponibles.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      {summaries.map((s) => (
        <AttendanceCard key={s.course_id} summary={s} />
      ))}
    </div>
  )
}

function AttendanceCard({ summary }: { summary: AttendanceSummary }) {
  const pct = parseFloat(summary.attendance_percentage)

  return (
    <div
      className={`rounded-lg border px-4 py-3 ${
        summary.is_at_risk
          ? "border-[#BA1A1A]/20 bg-[#BA1A1A]/5"
          : "border-[#E2E2E2] bg-white"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col gap-0.5">
          <span className="text-sm font-medium text-[#1A1C1C]">
            {summary.course_name}
          </span>
          <span className="text-xs text-[#5E5E5E]">
            {summary.attended + summary.justified} / {summary.total_sessions} sesiones
            {summary.justified > 0 && ` (${summary.justified} justif.)`}
          </span>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span
            className={`text-lg font-bold tabular-nums ${
              pct >= 70 ? "text-[#1A1C1C]" : "text-[#BA1A1A]"
            }`}
          >
            {pct.toFixed(1)}%
          </span>
          {summary.is_at_risk && (
            <span className="rounded-full bg-[#BA1A1A] px-2 py-0.5 text-xs font-semibold text-white">
              EN RIESGO
            </span>
          )}
        </div>
      </div>

      <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-[#E2E2E2]">
        <div
          className={`h-full rounded-full transition-all ${
            pct >= 70 ? "bg-[#FFD200]" : "bg-[#BA1A1A]"
          }`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
    </div>
  )
}
