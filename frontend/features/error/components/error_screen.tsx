interface ErrorScreenProps {
  message: string | null
  onRetry: () => void
}

export function ErrorScreen({ message, onRetry }: ErrorScreenProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-white px-4">
      <div className="w-full max-w-sm text-center">
        <div className="mb-6 flex justify-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#BA1A1A]/10">
            <span className="text-2xl font-bold text-[#BA1A1A]">✕</span>
          </div>
        </div>

        <h1 className="mb-2 text-xl font-bold text-[#1A1C1C]">
          Ocurrió un problema
        </h1>
        <p className="mb-8 text-sm text-[#5E5E5E]">
          {message ?? "Algo salió mal. Por favor intenta de nuevo."}
        </p>

        <button
          onClick={onRetry}
          className="rounded bg-[#FFD200] px-8 py-3 text-sm font-semibold text-[#1A1C1C] transition-opacity hover:opacity-90"
        >
          Reintentar
        </button>
      </div>
    </div>
  )
}
