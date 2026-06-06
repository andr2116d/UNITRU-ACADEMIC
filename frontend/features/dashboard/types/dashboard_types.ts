import type { GradeReport } from "@/features/grades/types/grade_types"

export interface StudentProfile {
  full_name: string
  first_name: string
  last_name: string
  enrollment_number: string
  faculty: string
  school: string
  campus: string
  admission_year: number | null
  institutional_email: string | null
  personal_email: string | null
  phone: string | null
  document: string | null
  birth_date: string | null
  sex: string | null
  marital_status: string | null
  address: string | null
  curriculum: string | null
  condition: string | null
  photo_data_url: string | null
}

export interface CourseHistory {
  period: string
  course_id: string
  course_name: string
  attempt: number
  cycle: number
  credits: number
  course_type: string
  section: string | null
  group: string | null
  final_grade: string | null
  is_disabled: boolean
}

export interface AcademicRecord {
  student_name: string
  enrollment_number: string
  condition: string
  accumulated_credits: number
  weighted_average: string
  payment_status: string | null
  payment_order: string | null
  courses: CourseHistory[]
}

export interface AttendanceSummary {
  course_id: string
  course_name: string
  teacher: string | null
  total_sessions: number
  attended: number
  absent: number
  justified: number
  attendance_percentage: string
  is_at_risk: boolean
}

export interface ScheduleSlot {
  day: string
  start_time: string
  end_time: string
  course_name: string
  classroom: string | null
  teacher: string | null
  // Grupo poblado desde la Ficha de Matrícula (cruce por nombre de curso).
  group: string | null
}

export interface EnrolledCourse {
  cycle: string
  course_id: string
  course_name: string
  course_type: string
  credits: number
  group: string
  attempt: number
  teacher: string | null
}

export interface Enrollment {
  period: string
  courses: EnrolledCourse[]
  total_credits: number
}

export interface OptimizedSession {
  course: string
  tipo: string | null
  day: string
  start_time: string
  end_time: string
  room: string | null
  subgroup: string | null
  teacher: string | null
  section: string | null
}

export interface OptimizedSelection {
  course: string
  cycle: string | null
  section: string | null
  subgroup: string | null
}

export interface OptimizedSchedule {
  score: number
  days: number
  gap_minutes: number
  extreme_sessions: number
  selections: OptimizedSelection[]
  sessions: OptimizedSession[]
}

export interface PeriodStat {
  period: string
  courses_taken: number
  courses_passed: number
  courses_failed: number
  pass_rate: string
  weighted_average: string
}

export interface AcademicAnalytics {
  period_stats: PeriodStat[]
  total_courses: number
  total_passed: number
  total_failed: number
  overall_pass_rate: string
  retried_course_names: string[]
  best_period: string | null
  worst_period: string | null
}

export interface DashboardReport {
  grade_report: GradeReport
  student_profile: StudentProfile | null
  academic_record: AcademicRecord | null
  attendance: AttendanceSummary[]
  schedule: ScheduleSlot[]
  enrollment: Enrollment | null
  optimized_schedules: OptimizedSchedule[]
  analytics: AcademicAnalytics | null
}
