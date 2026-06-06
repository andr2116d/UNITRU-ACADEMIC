import type {
  Enrollment,
  ScheduleSlot,
} from "@/features/dashboard/types/dashboard_types"

interface ScheduleGridProps {
  slots: ScheduleSlot[]
  enrollment: Enrollment | null
}

const DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

const normalize = (name: string) => name.trim().toUpperCase().replace(/\s+/g, " ")

export function ScheduleGrid({ slots, enrollment }: ScheduleGridProps) {
  if (slots.length === 0) {
    return (
      <p className="text-sm text-[#5E5E5E]">
        No hay datos de horario disponibles.
      </p>
    )
  }

  const activeDays = DAYS.filter((day) => slots.some((s) => s.day === day))

  // Cursos matriculados que aún no aparecen en el horario (sin asistencia que
  // confirme su turno): se avisan aparte para que el alumno no los pierda.
  const scheduled = new Set(slots.map((s) => normalize(s.course_name)))
  const unscheduled =
    enrollment?.courses.filter((c) => !scheduled.has(normalize(c.course_name))) ?? []

  return (
    <div className="flex flex-col gap-3">
      {unscheduled.length > 0 && (
        <p className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
          ⚠ Sin horario confirmado (sin asistencia registrada):{" "}
          {unscheduled.map((c) => `${c.course_name} (grupo ${c.group})`).join(", ")}.
        </p>
      )}

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-[#E2E2E2] bg-[#F5F5F5]">
              <th className="py-2.5 pr-4 text-left text-xs font-semibold text-[#5E5E5E]">
                Hora
              </th>
              {activeDays.map((day) => (
                <th
                  key={day}
                  className="px-2 py-2.5 text-center text-xs font-semibold text-[#5E5E5E]"
                >
                  {day}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {groupByTime(slots, activeDays).map(({ time, cells }, i) => (
              <tr
                key={i}
                className="border-b border-[#E2E2E2] align-top"
              >
                <td className="py-2 pr-4 text-xs text-[#5E5E5E] whitespace-nowrap">
                  {time}
                </td>
                {activeDays.map((day) => (
                  <td key={day} className="px-2 py-1">
                    <div className="flex flex-col gap-1">
                      {cells[day].map((slot, j) => (
                        <SlotBlock key={j} slot={slot} />
                      ))}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function SlotBlock({ slot }: { slot: ScheduleSlot }) {
  return (
    <div className="rounded border border-[#FFD200]/40 bg-[#FFD200]/10 px-2 py-1.5 text-xs">
      <div className="font-semibold leading-tight text-[#1A1C1C]">
        {slot.course_name}
      </div>
      {slot.group && (
        <div className="mt-0.5 text-[#5E5E5E]">Grupo {slot.group}</div>
      )}
      {slot.teacher && (
        <div className="mt-0.5 leading-tight text-[#5E5E5E]">{slot.teacher}</div>
      )}
      {slot.classroom && (
        <div className="mt-0.5 text-[#5E5E5E]">{slot.classroom}</div>
      )}
    </div>
  )
}

function groupByTime(
  slots: ScheduleSlot[],
  days: string[]
): { time: string; cells: Record<string, ScheduleSlot[]> }[] {
  const times = Array.from(
    new Set(slots.map((s) => `${s.start_time}–${s.end_time}`))
  ).sort()

  return times.map((time) => {
    const [start, end] = time.split("–")
    const cells: Record<string, ScheduleSlot[]> = {}
    for (const day of days) {
      // Varios cursos pueden caer en la misma franja (turnos solapados o
      // teoría/práctica): los apilamos en vez de descartar todos menos uno.
      cells[day] = slots.filter(
        (s) => s.day === day && s.start_time === start && s.end_time === end
      )
    }
    return { time, cells }
  })
}
