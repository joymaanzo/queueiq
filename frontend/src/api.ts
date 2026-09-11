const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface Clinic {
  clinic_id: number
  name: string
  location: string
  service_type: string
  hours_open: string
  days_open: string
}

export interface PredictRequest {
  clinic_id: number
  timestamp: string
  current_queue_length?: number
}

export interface PredictResponse {
  clinic_id: number
  predicted_wait_minutes: number
  confidence_interval_lower: number
  confidence_interval_upper: number
  confidence_level: number
  busyness: string
  mode: 'conditional' | 'unconditional'
  prediction_id: number
}

export interface RecordActualRequest {
  prediction_id: number
  actual_wait_minutes: number
}

export interface RecordActualResponse {
  status: string
  prediction_id: number
  actual_wait_minutes: number
  error_minutes: number
}

export interface HourlyStat {
  hour: number
  avg_wait: number
  sample_count: number
}

export interface DailyStat {
  day: string
  avg_wait: number
}

export interface StatsResponse {
  clinic_id: number
  hourly_stats: HourlyStat[]
  daily_stats: DailyStat[]
}

export interface ForecastEntry {
  hours_ahead: number
  window: string
  expected_arrivals: number
  busyness: string
}

export interface ForecastResponse {
  clinic_id: number
  forecast: ForecastEntry[]
}

interface ApiError {
  detail?: string
  code?: string
}

export interface ApiRequestError extends Error {
  status: number
  code?: string
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    const error = (await response.json().catch(() => ({}))) as ApiError
    const requestError = new Error(
      error.detail || `Request failed (${response.status})`,
    ) as ApiRequestError
    requestError.status = response.status
    requestError.code = error.code
    throw requestError
  }
  return (await response.json()) as T
}

export function listClinics(): Promise<Clinic[]> {
  return request<Clinic[]>('/clinics')
}

export function predictWait(req: PredictRequest): Promise<PredictResponse> {
  return request<PredictResponse>('/predict-wait-time', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export function recordActualWait(
  req: RecordActualRequest,
): Promise<RecordActualResponse> {
  return request<RecordActualResponse>('/record-actual-wait', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export function getClinicStats(clinicId: number): Promise<StatsResponse> {
  return request<StatsResponse>(`/clinic/${clinicId}/stats`)
}

export function getClinicForecast(clinicId: number): Promise<ForecastResponse> {
  return request<ForecastResponse>(`/clinic/${clinicId}/forecast`)
}
