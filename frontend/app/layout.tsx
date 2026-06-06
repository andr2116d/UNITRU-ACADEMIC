import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
})

export const metadata: Metadata = {
  title: "UNITRU Academic",
  description:
    "Consulta tus notas, horario y asistencia del SUV de la Universidad Nacional de Trujillo de forma rápida y clara.",
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
    ],
    apple: "/favicon.svg",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es" className={`${inter.variable} h-full`}>
      <body className="h-full bg-white antialiased">{children}</body>
    </html>
  )
}
