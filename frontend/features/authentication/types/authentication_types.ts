export interface LoginCredentials {
  username: string
  password: string
}

export type AuthProgressEvent =
  | "opening_suv"
  | "loading_login"
  | "downloading_captcha"
  | "solving_captcha"
  | "submitting_login"
  | "selecting_student"
  | "authentication_success"
  | "authentication_failed"
  | "extracting_profile"
  | "profile_extraction_success"
  | "profile_extraction_failed"
  | "extracting_record"
  | "record_extraction_success"
  | "record_extraction_failed"
  | "extracting_enrollment"
  | "enrollment_extraction_success"
  | "enrollment_extraction_failed"
  | "extracting_attendance"
  | "attendance_extraction_success"
  | "attendance_extraction_failed"
  | "extracting_grades"
  | "extracting_academic_info"
  | "extracting_courses"
  | "grade_extraction_success"
  | "grade_extraction_failed"
  | "optimizing_schedule"
  | "schedule_optimized"
  | "schedule_optimization_failed"
  | "dashboard_ready"
  | "dashboard_extraction_failed"
  | "error"

export interface WebSocketMessage {
  event: AuthProgressEvent
  data: Record<string, unknown>
}

export const EVENT_LABELS: Record<string, string> = {
  opening_suv: "Abriendo SUV...",
  loading_login: "Cargando pantalla de login...",
  downloading_captcha: "Descargando captcha...",
  solving_captcha: "Resolviendo captcha...",
  submitting_login: "Iniciando sesión...",
  selecting_student: "Seleccionando perfil Alumno...",
  authentication_success: "Autenticación exitosa",
  authentication_failed: "Autenticación fallida",
  extracting_profile: "Extrayendo perfil...",
  profile_extraction_success: "Perfil extraído",
  profile_extraction_failed: "Perfil no disponible",
  extracting_record: "Extrayendo record académico...",
  record_extraction_success: "Record extraído",
  record_extraction_failed: "Record no disponible",
  extracting_enrollment: "Extrayendo matrícula...",
  enrollment_extraction_success: "Matrícula extraída",
  enrollment_extraction_failed: "Matrícula no disponible",
  extracting_attendance: "Extrayendo asistencia...",
  attendance_extraction_success: "Asistencia extraída",
  attendance_extraction_failed: "Asistencia no disponible",
  extracting_grades: "Extrayendo notas...",
  extracting_academic_info: "Extrayendo información académica...",
  extracting_courses: "Extrayendo cursos...",
  grade_extraction_success: "Notas extraídas",
  grade_extraction_failed: "Error al extraer notas",
  optimizing_schedule: "Optimizando horario...",
  schedule_optimized: "Horario optimizado",
  schedule_optimization_failed: "Optimización no disponible",
  dashboard_ready: "Dashboard listo",
  dashboard_extraction_failed: "Error al extraer datos",
  error: "Error",
}
