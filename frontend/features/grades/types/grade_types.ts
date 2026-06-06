export interface CoursePrediction {
  course_id: string
  course_name: string
  total_units: number
  known: Record<string, string>
  pending: string[]
  required_pending_sum: string
  min_per_pending: string
  is_possible: boolean
  already_passes: boolean
  combinations: Record<string, number>[]
}

export interface Course {
  course_id: string
  course_name: string
  attempt: number
  u1: string | null
  u2: string | null
  u3: string | null
  u4: string | null
  u5: string | null
  u6: string | null
  sust: string | null
  np: string | null
  apla: string | null
  final_grade: string | null
  inh: boolean
  // Promedio de las unidades publicadas (parcial mientras el ciclo va en curso).
  average: string | null
  prediction: CoursePrediction | null
}

export interface GradeReport {
  period: string | null
  payment_order: string | null
  enrollment_type: string | null
  courses: Course[]
}
