import type { AcademicRecord, StudentProfile } from "@/features/dashboard/types/dashboard_types"

interface DashboardHeaderProps {
  profile: StudentProfile | null
  record: AcademicRecord | null
}

export function DashboardHeader({ profile, record }: DashboardHeaderProps) {
  const name = profile?.full_name ?? record?.student_name ?? "—"
  const school = profile?.school ?? "—"
  const average = record?.weighted_average
    ? parseFloat(record.weighted_average).toFixed(2)
    : null
  const credits = record?.accumulated_credits ?? null
  const paymentStatus = record?.payment_status ?? null

  return (
    <div className="flex flex-1 items-center justify-between overflow-hidden px-3 py-3 sm:px-6 sm:py-4">
      <div className="flex min-w-0 flex-col gap-0.5">
        <span className="truncate text-sm font-semibold text-[#1A1C1C] sm:text-base">{name}</span>
        <span className="truncate text-xs text-[#5E5E5E]">{school}</span>
      </div>

      {/* Estadísticas — ocultas en mobile para no saturar el header */}
      <div className="hidden items-center gap-6 sm:flex">
        {average && (
          <div className="flex flex-col items-end">
            <span className="text-xs text-[#5E5E5E]">Promedio ponderado</span>
            <span className="text-lg font-bold text-[#1A1C1C]">{average}</span>
          </div>
        )}
        {credits !== null && (
          <div className="flex flex-col items-end">
            <span className="text-xs text-[#5E5E5E]">Créditos</span>
            <span className="text-lg font-bold text-[#1A1C1C]">{credits}</span>
          </div>
        )}
        {paymentStatus && <PaymentBadge status={paymentStatus} />}
      </div>
    </div>
  )
}

function PaymentBadge({ status }: { status: string }) {
  const isPaid = status === "PAGADA"
  return (
    <span
      className={`rounded px-3 py-1 text-xs font-semibold ${
        isPaid ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
      }`}
    >
      {status}
    </span>
  )
}
