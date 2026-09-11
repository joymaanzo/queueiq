from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.bayesian.predict import predict_wait
from app.database import SessionLocal


def _predict(clinic_id, hour, queue_length):
    db = SessionLocal()
    try:
        return predict_wait(
            clinic_id,
            datetime(2026, 9, 11, hour, 0),
            queue_length,
            db,
            n_draws=1000,
        )
    finally:
        db.close()


def _unconditional(clinic_id, hour):
    db = SessionLocal()
    try:
        return predict_wait(
            clinic_id,
            datetime(2026, 9, 11, hour, 0),
            session=db,
            n_draws=200,
        )
    finally:
        db.close()


def test_predictions_positive():
    result = _predict(1, 9, 5)
    assert result["predicted_wait_minutes"] > 0


def test_interval_ordering():
    result = _predict(1, 9, 5)
    assert result["confidence_interval_lower"] < result["predicted_wait_minutes"]
    assert result["predicted_wait_minutes"] < result["confidence_interval_upper"]


def test_larger_queue_longer_wait():
    small = _predict(1, 9, 2)
    large = _predict(1, 9, 10)
    assert large["predicted_wait_minutes"] > small["predicted_wait_minutes"]


def test_different_hours_different_predictions():
    morning = _predict(1, 9, 5)
    afternoon = _predict(1, 14, 5)
    assert morning["predicted_wait_minutes"] != afternoon["predicted_wait_minutes"]


def test_different_clinics_different_predictions():
    central = _predict(1, 9, 5)
    urgent_care = _predict(2, 10, 5)
    assert central["predicted_wait_minutes"] != urgent_care["predicted_wait_minutes"]


def test_unconditional_calibration():
    from app.models import Clinic, QueueEvent
    from sqlalchemy import func

    db = SessionLocal()
    try:
        for clinic in db.query(Clinic).all():
            for hour in (9, 12, 14):
                historical = db.query(func.avg(QueueEvent.actual_wait_time_minutes)).filter(
                    QueueEvent.clinic_id == clinic.clinic_id,
                    QueueEvent.hour_of_day == hour,
                ).scalar()
                if historical is None:
                    continue
                result = predict_wait(
                    clinic.clinic_id,
                    datetime(2026, 9, 11, hour, 0),
                    session=db,
                    n_draws=200,
                )
                assert result["predicted_wait_minutes"] <= historical * 2
                assert result["predicted_wait_minutes"] >= historical / 2
                assert result["mode"] == "unconditional"
    finally:
        db.close()


def test_conditional_higher_than_unconditional():
    unconditional = _unconditional(2, 9)
    conditional = _predict(2, 9, 5)
    assert conditional["predicted_wait_minutes"] > unconditional["predicted_wait_minutes"]