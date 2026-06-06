"use client"

import { AnalyticsView } from "@/features/analytics/components/analytics_view"
import { AttendanceList } from "@/features/attendance/components/attendance_list"
import type { DashboardReport } from "@/features/dashboard/types/dashboard_types"
import { GradeCards } from "@/features/grades/components/grade_cards"
import { HomeView } from "@/features/home/components/home_view"
import { ProfileCard } from "@/features/profile/components/profile_card"
import { RecordTable } from "@/features/record/components/record_table"
import { ScheduleGrid } from "@/features/schedule/components/schedule_grid"
import { OptimizerView } from "@/features/schedule_optimizer/components/optimizer_view"
import type { Tab } from "./sidebar_nav"

interface DashboardTabsProps {
  active: Tab
  report: DashboardReport
}

const normalizeName = (s: string) => s.trim().toUpperCase().replace(/\s+/g, " ")

export function DashboardTabs({ active, report }: DashboardTabsProps) {
  // El período en curso aún no tiene P. Final publicado; cruzamos el promedio
  // parcial de Notas para mostrarlo en el Récord (en cursiva).
  const currentPeriod = report.grade_report.period
  const currentAverages: Record<string, string> = {}
  for (const c of report.grade_report.courses) {
    if (c.average) currentAverages[normalizeName(c.course_name)] = c.average
  }

  return (
    <div className="rounded-lg bg-white p-6 shadow-sm">
      {active === "inicio" && <HomeView report={report} />}

      {active === "notas" && (
        <GradeCards report={report.grade_report} enrollment={report.enrollment} />
      )}

      {active === "horario" && (
        <ScheduleGrid slots={report.schedule} enrollment={report.enrollment} />
      )}

      {active === "mejor_horario" && (
        <OptimizerView schedules={report.optimized_schedules} />
      )}

      {active === "asistencia" && (
        <AttendanceList summaries={report.attendance} />
      )}

      {active === "record" &&
        (report.academic_record ? (
          <RecordTable
            record={report.academic_record}
            currentPeriod={currentPeriod}
            currentAverages={currentAverages}
          />
        ) : (
          <p className="text-sm text-[#5E5E5E]">
            Record académico no disponible.
          </p>
        ))}

      {active === "analiticas" &&
        (report.analytics ? (
          <AnalyticsView analytics={report.analytics} />
        ) : (
          <p className="text-sm text-[#5E5E5E]">
            Analíticas no disponibles (se requiere Record Académico).
          </p>
        ))}

      {active === "perfil" &&
        (report.student_profile ? (
          <ProfileCard profile={report.student_profile} />
        ) : (
          <p className="text-sm text-[#5E5E5E]">
            Datos personales no disponibles.
          </p>
        ))}
    </div>
  )
}
