"""
QueueIQ FastAPI application.

Phase A: /health and /clinics only.
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func

from app.bayesian.posterior import fit_arrival_posteriors
from app.bayesian.predict import predict_wait
from app.database import Base, engine, SessionLocal
from app.models import Clinic, Prediction, QueueEvent
from app.schemas import (
    ClinicResponse,
    DailyStat,
    ErrorResponse,
    ForecastEntry,
    ForecastResponse,
    HourlyStat,
    PredictRequest,
    PredictResponse,
    RecordActualRequest,
    RecordActualResponse,
    StatsResponse,
)


DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def _raise_api_error(status_code: int, detail: str, code: str):
    raise HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"x-queueiq-error-code": code},
    )


def _get_clinic(db, clinic_id: int):
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first()
    if clinic is None:
        _raise_api_error(404, "Clinic not found", "CLINIC_NOT_FOUND")
    return clinic


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="QueueIQ API",
    version="0.1.0",
    description="Bayesian clinic queue prediction platform (Module 2 MVP)",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = exc.headers.get("x-queueiq-error-code") if exc.headers else None
    if code is None:
        code = {
            400: "BAD_REQUEST",
            404: "NOT_FOUND",
            409: "CONFLICT",
        }.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=str(exc.detail), code=code).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(detail="Invalid request", code="VALIDATION_ERROR").model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            detail="Internal server error", code="INTERNAL_ERROR"
        ).model_dump(),
    )


@app.get("/")
def root():
    return {
        "name": "QueueIQ API",
        "docs": "/docs",
        "health": "/health",
        "clinics": "/clinics",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": "connected",
        "model_loaded": False,
    }


@app.get("/clinics", response_model=list[ClinicResponse])
def list_clinics():
    db = SessionLocal()
    try:
        clinics = db.query(Clinic).all()
        return [
            {
                "clinic_id": c.clinic_id,
                "name": c.name,
                "location": c.location,
                "service_type": c.service_type,
                "hours_open": c.hours_open,
                "days_open": c.days_open,
            }
            for c in clinics
        ]
    finally:
        db.close()


@app.post("/predict-wait-time", response_model=PredictResponse)
def create_prediction(request: PredictRequest):
    db = SessionLocal()
    try:
        _get_clinic(db, request.clinic_id)
        if request.current_queue_length is not None and not 0 <= request.current_queue_length <= 100:
            _raise_api_error(400, "Queue length must be between 0 and 100", "INVALID_QUEUE_LENGTH")
        result = predict_wait(
            request.clinic_id,
            request.timestamp,
            request.current_queue_length,
            db,
        )
        prediction = Prediction(
            clinic_id=request.clinic_id,
            timestamp_of_prediction=datetime.utcnow(),
            predicted_wait_time_minutes=result["predicted_wait_minutes"],
            confidence_interval_lower=result["confidence_interval_lower"],
            confidence_interval_upper=result["confidence_interval_upper"],
            confidence_level=result["confidence_level"],
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return PredictResponse(
            clinic_id=request.clinic_id,
            **result,
            prediction_id=prediction.prediction_id,
        )
    finally:
        db.close()


@app.post("/record-actual-wait", response_model=RecordActualResponse)
def record_actual_wait(request: RecordActualRequest):
    db = SessionLocal()
    try:
        prediction = db.query(Prediction).filter(
            Prediction.prediction_id == request.prediction_id
        ).first()
        if prediction is None:
            _raise_api_error(404, "Prediction not found", "PREDICTION_NOT_FOUND")
        if prediction.actual_wait_time_minutes is not None:
            _raise_api_error(
                409,
                "Actual wait has already been reported",
                "ACTUAL_WAIT_ALREADY_REPORTED",
            )
        if not 0 <= request.actual_wait_minutes <= 600:
            _raise_api_error(400, "Actual wait must be between 0 and 600 minutes", "INVALID_WAIT_VALUE")
        prediction.actual_wait_time_minutes = request.actual_wait_minutes
        prediction.reported_at = datetime.utcnow()
        db.commit()
        return RecordActualResponse(
            status="recorded",
            prediction_id=prediction.prediction_id,
            actual_wait_minutes=request.actual_wait_minutes,
            error_minutes=prediction.predicted_wait_time_minutes - request.actual_wait_minutes,
        )
    finally:
        db.close()


@app.get("/clinic/{clinic_id}/stats", response_model=StatsResponse)
def clinic_stats(clinic_id: int):
    db = SessionLocal()
    try:
        _get_clinic(db, clinic_id)
        hourly_rows = db.query(
            QueueEvent.hour_of_day,
            func.avg(QueueEvent.actual_wait_time_minutes),
            func.count(QueueEvent.event_id),
        ).filter(QueueEvent.clinic_id == clinic_id).group_by(
            QueueEvent.hour_of_day
        ).order_by(QueueEvent.hour_of_day).all()
        daily_rows = db.query(
            QueueEvent.day_of_week,
            func.avg(QueueEvent.actual_wait_time_minutes),
        ).filter(QueueEvent.clinic_id == clinic_id).group_by(
            QueueEvent.day_of_week
        ).order_by(QueueEvent.day_of_week).all()
        return StatsResponse(
            clinic_id=clinic_id,
            hourly_stats=[
                HourlyStat(hour=hour, avg_wait=avg_wait, sample_count=count)
                for hour, avg_wait, count in hourly_rows
            ],
            daily_stats=[
                DailyStat(day=DAY_NAMES[day], avg_wait=avg_wait)
                for day, avg_wait in daily_rows
            ],
        )
    finally:
        db.close()


@app.get("/clinic/{clinic_id}/forecast", response_model=ForecastResponse)
def clinic_forecast(clinic_id: int):
    db = SessionLocal()
    try:
        _get_clinic(db, clinic_id)
        now = datetime.now()
        posteriors = fit_arrival_posteriors(clinic_id, db)
        forecast = []
        for hours_ahead in (1, 2, 4):
            start_hour = now.hour
            expected_arrivals = sum(
                posteriors.get(hour % 24, (0.0, 1.0))[0]
                / posteriors.get(hour % 24, (0.0, 1.0))[1]
                for hour in range(start_hour, start_hour + hours_ahead)
            )
            busyness = (
                "Low"
                if expected_arrivals < 5
                else "Moderate"
                if expected_arrivals < 12
                else "High"
            )
            forecast.append(
                ForecastEntry(
                    hours_ahead=hours_ahead,
                    window=f"{start_hour:02d}:00-{(start_hour + hours_ahead) % 24:02d}:00",
                    expected_arrivals=expected_arrivals,
                    busyness=busyness,
                )
            )
        return ForecastResponse(clinic_id=clinic_id, forecast=forecast)
    finally:
        db.close()
