"""Deterministic synthetic queue-event generation for QueueIQ."""

from datetime import datetime, timedelta
from pathlib import Path
import sys

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.database import SessionLocal
from app.models import Clinic, QueueEvent


SEED = 42
OPEN_DAYS_TO_GENERATE = 30
DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def _parse_hours(hours_open: str) -> tuple[int, int]:
    start, end = hours_open.split("-")
    return int(start.split(":")[0]), int(end.split(":")[0])


def _is_open(clinic: Clinic, date: datetime) -> bool:
    return DAY_NAMES[date.weekday()] in clinic.days_open


def _arrival_rate(clinic: Clinic, hour: int, weekday: int, rng: np.random.Generator) -> float:
    if clinic.name == "Central Medical":
        rate = {8: 12.0, 9: 12.0, 12: 11.0, 15: 10.0, 16: 10.0}.get(hour, 8.0)
        if weekday == 0:
            rate *= 1.15
        elif weekday == 4:
            rate *= 0.75
        return rate
    if clinic.name == "Midtown Urgent Care":
        rate = 9.0 if hour == 12 and rng.random() < 0.20 else 5.0
        if weekday == 0:
            rate *= 1.15
        elif weekday == 5:
            rate *= 0.85
        return rate
    rate = 5.0 if hour in (8, 9) else 2.0 if hour >= 14 else 3.0
    return rate * (1.10 if weekday == 0 else 1.0)


def _service_mean_minutes(clinic: Clinic) -> float:
    return {
        "Central Medical": 20.0,
        "Midtown Urgent Care": 15.0,
        "Riverside Family Dental": 12.0,
    }[clinic.name]


def _open_dates(clinic: Clinic, start_date: datetime) -> list[datetime]:
    dates = []
    current = start_date
    while len(dates) < OPEN_DAYS_TO_GENERATE:
        if _is_open(clinic, current):
            dates.append(current)
        current += timedelta(days=1)
    return dates


def _events_for_clinic(
    clinic: Clinic, rng: np.random.Generator, start_date: datetime
) -> list[QueueEvent]:
    opening_hour, closing_hour = _parse_hours(clinic.hours_open)
    service_mean = _service_mean_minutes(clinic)
    events = []

    for date in _open_dates(clinic, start_date):
        arrivals = []
        for hour in range(opening_hour, closing_hour):
            count = rng.poisson(_arrival_rate(clinic, hour, date.weekday(), rng))
            minute_offsets = rng.uniform(0, 60, count)
            arrivals.extend(
                date.replace(hour=hour, minute=0, second=0, microsecond=0)
                + timedelta(minutes=float(offset))
                for offset in minute_offsets
            )

        arrivals.sort()
        opening = date.replace(hour=opening_hour, minute=0, second=0, microsecond=0)
        server_free = [opening] * clinic.capacity_doctors
        for sequence, arrival_time in enumerate(arrivals):
            server_index = min(range(len(server_free)), key=server_free.__getitem__)
            service_start = max(arrival_time, server_free[server_index])
            service_duration = float(rng.exponential(service_mean))
            service_end = service_start + timedelta(minutes=service_duration)
            server_free[server_index] = service_end
            events.append(
                QueueEvent(
                    clinic_id=clinic.clinic_id,
                    patient_id=f"synthetic-{clinic.clinic_id}-{date:%Y%m%d}-{sequence:04d}",
                    arrival_time=arrival_time,
                    service_start_time=service_start,
                    service_end_time=service_end,
                    actual_wait_time_minutes=(service_start - arrival_time).total_seconds() / 60,
                    service_duration_minutes=service_duration,
                    day_of_week=date.weekday(),
                    hour_of_day=arrival_time.hour,
                )
            )
    return events


def generate_synthetic_data() -> dict[str, int]:
    """Generate events once for each clinic and return inserted counts."""
    rng = np.random.default_rng(SEED)
    start_date = datetime(2025, 1, 6)
    counts = {}
    db = SessionLocal()
    try:
        clinics = db.query(Clinic).order_by(Clinic.clinic_id).all()
        for clinic in clinics:
            if db.query(QueueEvent).filter(QueueEvent.clinic_id == clinic.clinic_id).first():
                counts[clinic.name] = 0
                continue
            events = _events_for_clinic(clinic, rng, start_date)
            db.add_all(events)
            counts[clinic.name] = len(events)
        db.commit()
        return counts
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()