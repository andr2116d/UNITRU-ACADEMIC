"use client"

import {
  BarChart2,
  BookOpen,
  CalendarCheck,
  CalendarDays,
  ClipboardList,
  Home,
  User,
  UserCheck,
  X,
} from "lucide-react"

export type Tab =
  | "inicio"
  | "notas"
  | "horario"
  | "mejor_horario"
  | "asistencia"
  | "record"
  | "perfil"
  | "analiticas"

interface SidebarNavProps {
  activeTab: Tab
  onTabChange: (tab: Tab) => void
  onReset: () => void
  studentName?: string
  hasAtRisk?: boolean
  isOpen?: boolean
  onClose?: () => void
}

const NAV_ITEMS: { id: Tab; label: string; Icon: React.ElementType }[] = [
  { id: "inicio", label: "Inicio", Icon: Home },
  { id: "notas", label: "Notas", Icon: BookOpen },
  { id: "horario", label: "Horario", Icon: CalendarDays },
  { id: "mejor_horario", label: "Mejor Horario", Icon: CalendarCheck },
  { id: "asistencia", label: "Asistencia", Icon: UserCheck },
  { id: "record", label: "Récord", Icon: ClipboardList },
  { id: "analiticas", label: "Analíticas", Icon: BarChart2 },
  { id: "perfil", label: "Perfil", Icon: User },
]

export function SidebarNav({
  activeTab,
  onTabChange,
  onReset,
  studentName,
  hasAtRisk,
  isOpen = false,
  onClose,
}: SidebarNavProps) {
  return (
    <>
      {/* Backdrop oscuro en mobile cuando el drawer está abierto */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={[
          // Posición fija en mobile (drawer deslizable), normal en desktop
          "fixed inset-y-0 left-0 z-50 flex w-60 flex-col bg-[#0B0F14]",
          "transition-transform duration-200 ease-in-out",
          isOpen ? "translate-x-0" : "-translate-x-full",
          // En desktop: vuelve al flujo normal y siempre visible
          "md:relative md:z-auto md:h-full md:shrink-0 md:translate-x-0",
        ].join(" ")}
      >
        {/* Logo + botón de cierre en mobile */}
        <div className="flex items-center gap-3 border-b border-white/5 px-5 py-5">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center bg-[#FFD200]">
            <span className="text-xs font-bold text-[#1A1C1C]">UNT</span>
          </div>
          <span className="text-sm font-semibold text-white">UNITRU Academic</span>
          <button
            onClick={onClose}
            className="ml-auto text-[#5E5E5E] hover:text-white md:hidden"
            aria-label="Cerrar menú"
          >
            <X size={16} />
          </button>
        </div>

        {/* Nombre del alumno */}
        {studentName && (
          <div className="border-b border-white/5 px-5 py-3">
            <p className="truncate text-xs text-[#D4D4D4]">{studentName}</p>
          </div>
        )}

        {/* Ítems de navegación */}
        <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-3 py-4">
          {NAV_ITEMS.map(({ id, label, Icon }) => {
            const isActive = activeTab === id
            return (
              <button
                key={id}
                onClick={() => onTabChange(id)}
                className={`flex w-full items-center gap-3 rounded px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-[#FFD200] text-[#1A1C1C]"
                    : "text-[#D4D4D4] hover:bg-white/5 hover:text-white"
                }`}
              >
                <Icon size={16} strokeWidth={2} />
                <span>{label}</span>
                {id === "asistencia" && hasAtRisk && (
                  <span className="ml-auto h-2 w-2 rounded-full bg-[#BA1A1A]" />
                )}
              </button>
            )
          })}
        </nav>

        {/* Acción de reset */}
        <div className="border-t border-white/5 px-3 py-4">
          <button
            onClick={onReset}
            className="w-full rounded px-3 py-2.5 text-left text-sm text-[#5E5E5E] transition-colors hover:bg-white/5 hover:text-[#D4D4D4]"
          >
            Nueva consulta
          </button>
        </div>
      </aside>
    </>
  )
}
