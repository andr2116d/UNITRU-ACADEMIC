"use client"

import { Download, Menu } from "lucide-react"
import { useState } from "react"
import type { DashboardReport } from "@/features/dashboard/types/dashboard_types"
import type { GradeReport } from "@/features/grades/types/grade_types"
import { DashboardHeader } from "./dashboard_header"
import { DashboardTabs } from "./dashboard_tabs"
import { SidebarNav, type Tab } from "./sidebar_nav"

interface DashboardLayoutProps {
  report: DashboardReport
  onReset: () => void
}

function exportGradesCsv(gradeReport: GradeReport, studentName: string) {
  const rows: string[][] = [
    ["Estudiante", studentName],
    ["Período", gradeReport.period ?? ""],
    [],
    ["Curso", "Código", "U1", "U2", "U3", "Promedio", "P. Final"],
  ]
  for (const c of gradeReport.courses) {
    rows.push([
      c.course_name,
      c.course_id,
      c.u1 ?? "",
      c.u2 ?? "",
      c.u3 ?? "",
      c.average ?? "",
      c.final_grade ?? "",
    ])
  }
  const csv = rows.map((r) => r.map((v) => `"${v}"`).join(",")).join("\n")
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `notas_${gradeReport.period ?? "ciclo"}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

export function DashboardLayout({ report, onReset }: DashboardLayoutProps) {
  const [activeTab, setActiveTab] = useState<Tab>("inicio")
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const studentName =
    report.student_profile?.full_name ??
    report.academic_record?.student_name ??
    "Estudiante"
  const hasAtRisk = report.attendance.some((s) => s.is_at_risk)

  return (
    <div className="flex h-screen overflow-hidden">
      <SidebarNav
        activeTab={activeTab}
        onTabChange={(tab) => {
          setActiveTab(tab)
          setSidebarOpen(false)
        }}
        onReset={onReset}
        studentName={studentName}
        hasAtRisk={hasAtRisk}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center border-b border-[#E2E2E2] bg-white">
          {/* Botón hamburguesa — solo en mobile */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="flex shrink-0 items-center justify-center px-4 py-4 text-[#1A1C1C] md:hidden"
            aria-label="Abrir menú"
          >
            <Menu size={20} />
          </button>

          <DashboardHeader
            profile={report.student_profile}
            record={report.academic_record}
          />

          <div className="shrink-0 pr-4">
            <button
              onClick={() => exportGradesCsv(report.grade_report, studentName)}
              title="Exportar notas a CSV"
              className="flex items-center gap-1.5 rounded border border-[#E2E2E2] px-3 py-1.5 text-xs text-[#5E5E5E] transition-colors hover:border-[#1A1C1C] hover:text-[#1A1C1C]"
            >
              <Download size={13} />
              <span className="hidden sm:inline">Exportar CSV</span>
            </button>
          </div>
        </div>

        <main className="flex-1 overflow-y-auto bg-[#F5F5F5] p-3 md:p-6">
          <DashboardTabs active={activeTab} report={report} />
        </main>
      </div>
    </div>
  )
}
