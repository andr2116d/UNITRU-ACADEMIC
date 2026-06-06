import type { DashboardReport, ScheduleSlot } from "@/features/dashboard/types/dashboard_types"

interface HomeViewProps {
  report: DashboardReport
}

const WEEKDAYS = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

export function HomeView({ report }: HomeViewProps) {
  const profile = report.student_profile
  const record = report.academic_record

  const name = profile?.full_name ?? record?.student_name ?? "Estudiante"
  const school = profile?.school ?? null
  const period = report.grade_report.period
  const average = record?.weighted_average
    ? parseFloat(record.weighted_average).toFixed(2)
    : null
  const credits = record?.accumulated_credits ?? null
  const condition = record?.condition ?? null

  const today = WEEKDAYS[new Date().getDay()]
  const todaySlots = report.schedule
    .filter((s) => s.day === today)
    .sort((a, b) => a.start_time.localeCompare(b.start_time))

  const atRisk = report.attendance.filter((s) => s.is_at_risk)

  return (
    <div className="flex flex-col gap-6">
      {/* Hero saludo */}
      <div className="rounded-lg bg-[#0B0F14] px-6 py-8">
        <p className="mb-1 text-sm text-[#D4D4D4]">Bienvenido,</p>
        <h1 className="text-2xl font-bold text-white">{name}</h1>
        {(period || school) && (
          <p className="mt-1 text-sm text-[#5E5E5E]">
            {[period, school].filter(Boolean).join(" · ")}
          </p>
        )}
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <MetricCard label="Promedio Ponderado" value={average ?? "—"} />
        <MetricCard label="Créditos Aprobados" value={credits !== null ? String(credits) : "—"} />
        <MetricCard label="Situación" value={condition ?? "—"} />
        <MetricCard label="Período Actual" value={period ?? "—"} />
      </div>

      {/* Dos columnas */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <TodaySchedule day={today} slots={todaySlots} />
        <AtRiskSection atRisk={atRisk.map((s) => ({ name: s.course_name, pct: parseFloat(s.attendance_percentage) }))} />
      </div>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 rounded-lg border border-[#E2E2E2] bg-white px-4 py-4">
      <span className="text-xs text-[#5E5E5E]">{label}</span>
      <span className="text-2xl font-bold tabular-nums leading-none text-[#1A1C1C]">
        {value}
      </span>
    </div>
  )
}

function TodaySchedule({ day, slots }: { day: string; slots: ScheduleSlot[] }) {
  return (
    <div className="rounded-lg border border-[#E2E2E2] bg-white p-4">
      <h2 className="mb-3 text-sm font-semibold text-[#1A1C1C]">
        Horario de Hoy
        <span className="ml-2 text-xs font-normal text-[#5E5E5E]">{day}</span>
      </h2>

      {slots.length === 0 ? (
        <p className="text-sm text-[#5E5E5E]">No hay clases hoy.</p>
      ) : (
        <div className="flex flex-col gap-2">
          {slots.map((slot, i) => (
            <div
              key={i}
              className="flex items-start gap-3 rounded border border-[#FFD200]/30 bg-[#FFD200]/8 px-3 py-2"
            >
              <div className="flex flex-col items-center">
                <span className="text-xs font-semibold text-[#1A1C1C]">
                  {slot.start_time}
                </span>
                <span className="text-[10px] text-[#5E5E5E]">{slot.end_time}</span>
              </div>
              <div className="flex flex-col gap-0.5">
                <span className="text-sm font-medium leading-tight text-[#1A1C1C]">
                  {slot.course_name}
                </span>
                {slot.classroom && (
                  <span className="text-xs text-[#5E5E5E]">{slot.classroom}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function AtRiskSection({
  atRisk,
}: {
  atRisk: { name: string; pct: number }[]
}) {
  return (
    <div className="rounded-lg border border-[#E2E2E2] bg-white p-4">
      <h2 className="mb-3 text-sm font-semibold text-[#1A1C1C]">Cursos en Riesgo</h2>

      {atRisk.length === 0 ? (
        <div className="flex items-center gap-2 text-sm text-green-600">
          <span>✓</span>
          <span>Sin cursos en riesgo</span>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {atRisk.map((course, i) => (
            <div key={i} className="flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium leading-tight text-[#1A1C1C]">
                  {course.name}
                </span>
                <span className="text-sm font-bold text-[#BA1A1A]">
                  {course.pct.toFixed(1)}%
                </span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#E2E2E2]">
                <div
                  className="h-full rounded-full bg-[#BA1A1A]"
                  style={{ width: `${Math.min(course.pct, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
