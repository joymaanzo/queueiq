"""Pydantic request and response schemas for the QueueIQ API."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PredictRequest(BaseModel):
    clinic_id: int
    timestamp: datetime
    current_queue_length: Optional[int] = None


class PredictResponse(BaseModel):
    clinic_id: int
    predicted_wait_minutes: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    confidence_level: float
    busyness: str
    mode: str
    prediction_id: int


class RecordActualRequest(BaseModel):
    prediction_id: int
    actual_wait_minutes: float


class RecordActualResponse(BaseModel):
    status: str
    prediction_id: int
    actual_wait_minutes: float
    error_minutes: float


class ClinicResponse(BaseModel):
    clinic_id: int
    name: str
    location: str
    service_type: str
    hours_open: str
    days_open: str


class HourlyStat(BaseModel):
    hour: int
    avg_wait: float
    sample_count: int


class DailyStat(BaseModel):
    day: str
    avg_wait: float


class StatsResponse(BaseModel):
    clinic_id: int
    hourly_stats: List[HourlyStat]
    daily_stats: List[DailyStat]


class ForecastEntry(BaseModel):
    hours_ahead: int
    window: str
    expected_arrivals: float
    busyness: str


class ForecastResponse(BaseModel):
    clinic_id: int
    forecast: List[ForecastEntry]


class EvaluationResponse(BaseModel):
    clinic_id: int
    predictions_with_actuals: int
    model_mae: float
    baseline_mae: float
    improvement_pct: float
    interval_coverage: float
    interval_level: float
    events_evaluated: int


class ErrorResponse(BaseModel):
    detail: str
    code: str
