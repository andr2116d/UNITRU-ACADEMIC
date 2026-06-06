import type { StudentProfile } from "@/features/dashboard/types/dashboard_types"

interface ProfileCardProps {
  profile: StudentProfile
}

export function ProfileCard({ profile }: ProfileCardProps) {
  const fields: { label: string; value: string | number | null }[] = [
    { label: "Código", value: profile.enrollment_number },
    { label: "DNI", value: profile.document },
    { label: "Fecha de nacimiento", value: profile.birth_date },
    { label: "Sexo", value: profile.sex },
    { label: "Estado civil", value: profile.marital_status },
    { label: "Domicilio", value: profile.address },
    { label: "Celular", value: profile.phone },
    { label: "Correo personal", value: profile.personal_email },
    { label: "Correo institucional", value: profile.institutional_email },
    { label: "Facultad", value: profile.faculty },
    { label: "Escuela", value: profile.school },
    { label: "Currícula", value: profile.curriculum },
    { label: "Sede", value: profile.campus },
    { label: "Año de ingreso", value: profile.admission_year },
    { label: "Condición", value: profile.condition },
  ]

  return (
    <div className="flex flex-col gap-6 sm:flex-row">
      <div className="flex flex-col items-center gap-3 sm:w-48 sm:shrink-0">
        {profile.photo_data_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={profile.photo_data_url}
            alt={profile.full_name}
            className="w-40 rounded-lg border border-[#E2E2E2] object-cover"
          />
        ) : (
          <div className="flex h-48 w-40 items-center justify-center rounded-lg border border-dashed border-[#E2E2E2] text-xs text-[#5E5E5E]">
            Sin foto
          </div>
        )}
        <span className="text-center text-sm font-semibold text-[#1A1C1C]">
          {profile.full_name}
        </span>
        {profile.condition && (
          <span className="rounded-full bg-[#FFD200] px-3 py-0.5 text-xs font-semibold text-[#1A1C1C]">
            {profile.condition}
          </span>
        )}
      </div>

      <dl className="grid flex-1 grid-cols-1 gap-x-8 gap-y-3 sm:grid-cols-2">
        {fields.map(
          (f) =>
            f.value != null &&
            f.value !== "" && (
              <div key={f.label} className="flex flex-col gap-0.5">
                <dt className="text-xs font-semibold uppercase tracking-wide text-[#5E5E5E]">
                  {f.label}
                </dt>
                <dd className="text-sm text-[#1A1C1C]">{f.value}</dd>
              </div>
            )
        )}
      </dl>
    </div>
  )
}
