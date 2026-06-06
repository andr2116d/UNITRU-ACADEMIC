"use client"

import { useState } from "react"
import type { LoginCredentials } from "../types/authentication_types"

interface LoginFormProps {
  onSubmit: (credentials: LoginCredentials) => void
  onBack: () => void
  disabled?: boolean
}

export function LoginForm({ onSubmit, onBack, disabled = false }: LoginFormProps) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (username.trim() && password.trim()) {
      onSubmit({ username: username.trim(), password: password.trim() })
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Panel izquierdo — branding (oculto en mobile) */}
      <div className="hidden flex-col justify-between bg-[#0B0F14] p-12 lg:flex lg:w-2/5">
        <div className="flex h-14 w-14 items-center justify-center bg-[#FFD200]">
          <span className="text-lg font-bold text-[#1A1C1C]">UNT</span>
        </div>
        <div className="flex flex-col gap-4">
          <h2 className="text-3xl font-bold text-white">UNITRU Academic</h2>
          <p className="text-[#D4D4D4]">
            Accede a tu información académica: notas, horarios, asistencia y
            más, directamente desde el SUV.
          </p>
        </div>
        <p className="text-xs text-[#5E5E5E]">Universidad Nacional de Trujillo</p>
      </div>

      {/* Panel derecho — formulario */}
      <div className="flex flex-1 flex-col items-center justify-center bg-white px-8 py-12">
        <div className="w-full max-w-sm">
          <button
            type="button"
            onClick={onBack}
            className="mb-8 flex items-center gap-1 text-sm text-[#5E5E5E] transition-colors hover:text-[#1A1C1C]"
          >
            ← Volver
          </button>

          <div className="mb-8 flex flex-col gap-1">
            <h1 className="text-2xl font-bold text-[#1A1C1C]">
              Ingresa con tu cuenta
            </h1>
            <p className="text-sm text-[#5E5E5E]">
              Usa tus credenciales del Sistema Único Virtual (SUV)
            </p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="username"
                className="text-xs font-semibold uppercase tracking-wide text-[#5E5E5E]"
              >
                Código de estudiante
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={disabled}
                autoComplete="username"
                placeholder="Ej. 72312345"
                className="rounded border border-[#E2E2E2] px-3 py-2.5 text-sm text-[#1A1C1C] placeholder-[#BDBDBD] transition-colors focus:border-[#1A1C1C] focus:outline-none disabled:opacity-50"
                required
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="password"
                className="text-xs font-semibold uppercase tracking-wide text-[#5E5E5E]"
              >
                Contraseña
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={disabled}
                autoComplete="current-password"
                placeholder="Contraseña SUV"
                className="rounded border border-[#E2E2E2] px-3 py-2.5 text-sm text-[#1A1C1C] placeholder-[#BDBDBD] transition-colors focus:border-[#1A1C1C] focus:outline-none disabled:opacity-50"
                required
              />
            </div>

            <button
              type="submit"
              disabled={disabled || !username.trim() || !password.trim()}
              className="mt-2 rounded bg-[#FFD200] py-3 text-sm font-semibold text-[#1A1C1C] transition-opacity hover:opacity-90 disabled:opacity-40"
            >
              {disabled ? "Procesando..." : "Ingresar"}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
