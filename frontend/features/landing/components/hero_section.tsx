"use client"

interface HeroSectionProps {
  onStart: () => void
}

export function HeroSection({ onStart }: HeroSectionProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#0B0F14] px-4">
      <div className="flex flex-col items-center gap-8 text-center">
        <div className="flex h-20 w-20 items-center justify-center bg-[#FFD200]">
          <span className="text-2xl font-bold text-[#1A1C1C]">UNT</span>
        </div>

        <div className="flex flex-col items-center gap-3">
          <h1 className="text-4xl font-bold tracking-tight text-white">
            UNITRU Academic
          </h1>
          <p className="max-w-sm text-base text-[#D4D4D4]">
            Consulta tus notas, horarios y asistencia directamente desde el SUV
            de la Universidad Nacional de Trujillo
          </p>
        </div>

        <button
          onClick={onStart}
          className="rounded bg-[#FFD200] px-10 py-3 text-base font-semibold text-[#1A1C1C] transition-opacity hover:opacity-90"
        >
          Iniciar sesión
        </button>
      </div>
    </div>
  )
}
