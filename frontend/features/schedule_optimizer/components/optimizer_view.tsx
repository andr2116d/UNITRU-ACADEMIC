import type {
  OptimizedSchedule,
  ScheduleSlot,
} from "@/features/dashboard/types/dashboard_types"
import { ScheduleGrid } from "@/features/schedule/components/schedule_grid"

interface OptimizerViewProps {
  schedules: OptimizedSchedule[]
}

function toSlots(opt: OptimizedSchedule): ScheduleSlot[] {
  return opt.sessions.map((s) => ({
    day: s.day,
    start_time: s.start_time,
    end_time: s.end_time,
    course_name: s.course,
    classroom: s.room,
    teacher: s.teacher,
    group: s.section,
  }))
}

function gapLabel(minutes: number): string {
  if (minutes === 0) return "sin huecos"
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return `${h > 0 ? `${h}h ` : ""}${m > 0 ? `${m}min` : ""}`.trim() + " libres"
}

export function OptimizerView({ schedules }: OptimizerViewProps) {
  if (schedules.length === 0) {
    return (
      <p className="text-sm text-[#5E5E5E]">
        No hay sugerencias de horario disponibles (sin matrícula o sin oferta en
        el catálogo).
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <p className="text-xs text-[#5E5E5E]">
        Mejores horarios posibles combinando secciones para tus cursos
        matriculados, priorizando menos huecos, menos días y evitar horas
        extremas.
      </p>

      {schedules.map((opt, i) => (
        <div
          key={i}
          className="rounded-lg border border-[#E2E2E2] p-5"
        >
          <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-3">
              <span
                className={`rounded px-2.5 py-0.5 text-xs font-semibold ${
                  i === 0
                    ? "bg-[#FFD200] text-[#1A1C1C]"
                    : "bg-[#F5F5F5] text-[#5E5E5E]"
                }`}
              >
                Opción {i + 1}
                {i === 0 && " · recomendada"}
              </span>
              <span className="text-xs text-[#5E5E5E]">
                {opt.days} {opt.days === 1 ? "día" : "días"} ·{" "}
                {gapLabel(opt.gap_minutes)}
                {opt.extreme_sessions > 0 &&
                  ` · ${opt.extreme_sessions} en horas extremas`}
              </span>
            </div>
          </div>

          <div className="mb-4 flex flex-wrap gap-1.5">
            {opt.selections.map((sel) => (
              <span
                key={sel.course}
                className="rounded border border-[#E2E2E2] bg-[#F5F5F5] px-2 py-0.5 text-xs text-[#5E5E5E]"
              >
                {sel.course}: <b className="text-[#1A1C1C]">Secc. {sel.section}</b>
                {sel.subgroup && ` / ${sel.subgroup}`}
              </span>
            ))}
          </div>

          <ScheduleGrid slots={toSlots(opt)} enrollment={null} />
        </div>
      ))}
    </div>
  )
}
