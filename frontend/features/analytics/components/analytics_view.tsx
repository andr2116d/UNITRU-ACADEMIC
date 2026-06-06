"use client"

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import type { AcademicAnalytics } from "@/features/dashboard/types/dashboard_types"

interface AnalyticsViewProps {
  analytics: AcademicAnalytics
}

export function AnalyticsView({ analytics }: AnalyticsViewProps) {
  const chartData = analytics.period_stats.map((p) => ({
    period: p.period,
    Promedio: parseFloat(p.weighted_average),
    Aprobados: p.courses_passed,
    Reprobados: p.courses_failed,
  }))

  return (
    <div className="flex flex-col gap-6">
      {/* Resumen global */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <SummaryCard label="Total cursos" value={String(analytics.total_courses)} />
        <SummaryCard
          label="Aprobados"
          value={String(analytics.total_passed)}
          color="text-green-600"
        />
        <SummaryCard
          label="Reprobados"
          value={String(analytics.total_failed)}
          color="text-[#BA1A1A]"
        />
        <SummaryCard
          label="Tasa global"
          value={`${parseFloat(analytics.overall_pass_rate).toFixed(1)}%`}
          color="text-[#1A1C1C]"
        />
      </div>

      {/* Gráfica de promedio por período */}
      {chartData.length > 0 && (
        <div className="rounded-lg border border-[#E2E2E2] bg-white p-4">
          <h2 className="mb-4 text-sm font-semibold text-[#1A1C1C]">
            Promedio por período
          </h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E2E2" />
              <XAxis
                dataKey="period"
                tick={{ fontSize: 11, fill: "#5E5E5E" }}
                tickLine={false}
              />
              <YAxis
                domain={[0, 20]}
                tick={{ fontSize: 11, fill: "#5E5E5E" }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{ fontSize: 12, borderColor: "#E2E2E2", borderRadius: 6 }}
              />
              <Bar dataKey="Promedio" fill="#FFD200" radius={[3, 3, 0, 0]} maxBarSize={48} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Gráfica de aprobados vs reprobados */}
      {chartData.length > 0 && (
        <div className="rounded-lg border border-[#E2E2E2] bg-white p-4">
          <h2 className="mb-4 text-sm font-semibold text-[#1A1C1C]">
            Aprobados vs. reprobados por período
          </h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E2E2" />
              <XAxis
                dataKey="period"
                tick={{ fontSize: 11, fill: "#5E5E5E" }}
                tickLine={false}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fontSize: 11, fill: "#5E5E5E" }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{ fontSize: 12, borderColor: "#E2E2E2", borderRadius: 6 }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="Aprobados" fill="#22c55e" radius={[3, 3, 0, 0]} maxBarSize={36} />
              <Bar dataKey="Reprobados" fill="#BA1A1A" radius={[3, 3, 0, 0]} maxBarSize={36} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Tabla de períodos */}
      <div className="rounded-lg border border-[#E2E2E2] bg-white">
        <div className="border-b border-[#E2E2E2] px-4 py-3">
          <h2 className="text-sm font-semibold text-[#1A1C1C]">Detalle por período</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#E2E2E2] bg-[#F5F5F5]">
                {["Período", "Cursos", "Aprobados", "Reprobados", "Promedio", "Tasa"].map(
                  (h) => (
                    <th
                      key={h}
                      className="px-4 py-2.5 text-left text-xs font-semibold text-[#1A1C1C]"
                    >
                      {h}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody>
              {analytics.period_stats.map((p) => (
                <tr key={p.period} className="border-b border-[#E2E2E2] last:border-0">
                  <td className="px-4 py-2.5 font-medium text-[#1A1C1C]">{p.period}</td>
                  <td className="px-4 py-2.5 tabular-nums text-[#5E5E5E]">{p.courses_taken}</td>
                  <td className="px-4 py-2.5 tabular-nums text-green-600">{p.courses_passed}</td>
                  <td className="px-4 py-2.5 tabular-nums text-[#BA1A1A]">{p.courses_failed}</td>
                  <td className="px-4 py-2.5 tabular-nums text-[#1A1C1C]">
                    {p.weighted_average}
                  </td>
                  <td className="px-4 py-2.5 tabular-nums text-[#5E5E5E]">
                    {parseFloat(p.pass_rate).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cursos repetidos */}
      {analytics.retried_course_names.length > 0 && (
        <div className="rounded-lg border border-[#E2E2E2] bg-white p-4">
          <h2 className="mb-3 text-sm font-semibold text-[#1A1C1C]">
            Cursos llevados más de una vez
          </h2>
          <div className="flex flex-wrap gap-2">
            {analytics.retried_course_names.map((name) => (
              <span
                key={name}
                className="rounded bg-[#BA1A1A]/10 px-2 py-1 text-xs font-medium text-[#BA1A1A]"
              >
                {name}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Highlights */}
      {(analytics.best_period || analytics.worst_period) && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {analytics.best_period && (
            <div className="flex items-center gap-3 rounded-lg border border-green-200 bg-green-50 px-4 py-3">
              <span className="text-lg">🏆</span>
              <div>
                <p className="text-xs text-[#5E5E5E]">Mejor período</p>
                <p className="text-sm font-semibold text-[#1A1C1C]">{analytics.best_period}</p>
              </div>
            </div>
          )}
          {analytics.worst_period && analytics.worst_period !== analytics.best_period && (
            <div className="flex items-center gap-3 rounded-lg border border-[#BA1A1A]/20 bg-[#BA1A1A]/5 px-4 py-3">
              <span className="text-lg">📉</span>
              <div>
                <p className="text-xs text-[#5E5E5E]">Período más bajo</p>
                <p className="text-sm font-semibold text-[#1A1C1C]">{analytics.worst_period}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function SummaryCard({
  label,
  value,
  color = "text-[#1A1C1C]",
}: {
  label: string
  value: string
  color?: string
}) {
  return (
    <div className="flex flex-col gap-1 rounded-lg border border-[#E2E2E2] bg-white px-4 py-4">
      <span className="text-xs text-[#5E5E5E]">{label}</span>
      <span className={`text-2xl font-bold tabular-nums leading-none ${color}`}>{value}</span>
    </div>
  )
}
