"""Evaluation metrics for QueueIQ predictions and historical baselines."""

from sqlalchemy import func

from app.bayesian.predict import predict_wait
from app.models import Prediction, QueueEvent


def mean_absolute_error(predictions: list[float], actuals: list[float]) -> float:
    """Return the mean absolute error, or 0.0 when either list is empty."""
    if not predictions or not actuals:
        return 0.0
    count = min(len(predictions), len(actuals))
    return sum(
        abs(actuals[index] - predictions[index]) for index in range(count)
    ) / count


def prediction_interval_coverage(lower, upper, actuals) -> float:
    """Return the fraction of actuals inside inclusive prediction intervals."""
    if not actuals:
        return 0.0
    count = min(len(lower), len(upper), len(actuals))
    covered = sum(
        lower[index] <= actuals[index] <= upper[index] for index in range(count)
    )
    return covered / count if count else 0.0


def baseline_mae(clinic_id: int, session) -> tuple[float, int]:
    """Compare each event with its clinic, day, and hour historical average."""
    events = session.query(QueueEvent).filter(
        QueueEvent.clinic_id == clinic_id
    ).all()
    if not events:
        return 0.0, 0

    historical_means = {
        (day_of_week, hour_of_day): average_wait
        for day_of_week, hour_of_day, average_wait in session.query(
            QueueEvent.day_of_week,
            QueueEvent.hour_of_day,
            func.avg(QueueEvent.actual_wait_time_minutes),
        ).filter(
            QueueEvent.clinic_id == clinic_id
        ).group_by(
            QueueEvent.day_of_week,
            QueueEvent.hour_of_day,
        ).all()
    }
    predictions = [
        historical_means[(event.day_of_week, event.hour_of_day)]
        for event in events
    ]
    actuals = [event.actual_wait_time_minutes for event in events]
    return mean_absolute_error(predictions, actuals), len(events)


def model_mae(
    clinic_id: int,
    session,
    max_events: int = 50,
    n_draws: int = 2000,
) -> tuple[float, int]:
    """Evaluate recent historical events with conditional model predictions."""
    events = session.query(QueueEvent).filter(
        QueueEvent.clinic_id == clinic_id
    ).order_by(QueueEvent.event_id.desc()).limit(max_events).all()
    predictions = []
    actuals = []
    for event in events:
        result = predict_wait(
            clinic_id,
            event.arrival_time,
            current_queue_length=0,
            session=session,
            n_draws=n_draws,
        )
        predictions.append(result["predicted_wait_minutes"])
        actuals.append(event.actual_wait_time_minutes)
    return mean_absolute_error(predictions, actuals), len(events)


def evaluation_summary(clinic_id: int, session) -> dict:
    """Return model, baseline, and reported-prediction evaluation metrics."""
    reported_predictions = session.query(Prediction).filter(
        Prediction.clinic_id == clinic_id,
        Prediction.actual_wait_time_minutes.isnot(None),
    ).all()
    interval_coverage = prediction_interval_coverage(
        [prediction.confidence_interval_lower for prediction in reported_predictions],
        [prediction.confidence_interval_upper for prediction in reported_predictions],
        [prediction.actual_wait_time_minutes for prediction in reported_predictions],
    )
    evaluated_model_mae, events_evaluated = model_mae(clinic_id, session)
    evaluated_baseline_mae, _ = baseline_mae(clinic_id, session)
    improvement_pct = (
        (evaluated_baseline_mae - evaluated_model_mae)
        / evaluated_baseline_mae
        * 100.0
        if evaluated_baseline_mae
        else 0.0
    )
    return {
        "clinic_id": clinic_id,
        "predictions_with_actuals": len(reported_predictions),
        "model_mae": evaluated_model_mae,
        "baseline_mae": evaluated_baseline_mae,
        "improvement_pct": improvement_pct,
        "interval_coverage": interval_coverage,
        "interval_level": 0.80,
        "events_evaluated": events_evaluated,
    }