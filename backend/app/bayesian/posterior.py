"""Conjugate posterior fitting for clinic arrival and service data."""

from datetime import datetime

from app.bayesian.priors import A_0, ALPHA_0, B_0, BETA_0
from app.models import Clinic, ModelParameter, QueueEvent


def _operating_hours(clinic: Clinic) -> range:
    start, end = clinic.hours_open.split("-")
    opening_hour = int(start.split(":")[0])
    closing_hour = int(end.split(":")[0])
    return range(opening_hour, closing_hour)


def _get_clinic(clinic_id: int, session) -> Clinic:
    clinic = session.query(Clinic).filter(Clinic.clinic_id == clinic_id).first()
    if clinic is None:
        raise ValueError(f"Clinic {clinic_id} not found")
    return clinic


def _events(clinic_id: int, session) -> list[QueueEvent]:
    return session.query(QueueEvent).filter(QueueEvent.clinic_id == clinic_id).all()


def fit_arrival_posteriors(clinic_id, session):
    """Fit Gamma arrival-rate posteriors for each operating hour."""
    clinic = _get_clinic(clinic_id, session)
    events = _events(clinic_id, session)
    posteriors = {}
    for hour in _operating_hours(clinic):
        hour_events = [event for event in events if event.hour_of_day == hour]
        observed_days = {event.arrival_time.date() for event in hour_events}
        posteriors[hour] = (
            ALPHA_0 + len(hour_events),
            BETA_0 + len(observed_days),
        )
    return posteriors


def fit_service_posterior(clinic_id, session):
    """Fit the Gamma posterior for the clinic service rate per minute."""
    events = _events(clinic_id, session)
    return (
        A_0 + len(events),
        B_0 + sum(event.service_duration_minutes for event in events),
    )


def persist_posteriors(session):
    """Replace persisted model parameters with a full fit for every clinic."""
    now = datetime.utcnow()
    for clinic in session.query(Clinic).order_by(Clinic.clinic_id).all():
        events = _events(clinic.clinic_id, session)
        event_count = len(events)
        session.query(ModelParameter).filter(
            ModelParameter.clinic_id == clinic.clinic_id
        ).delete(synchronize_session=False)

        for hour, (alpha, beta) in fit_arrival_posteriors(clinic.clinic_id, session).items():
            hour_label = f"{hour:02d}"
            hour_count = sum(event.hour_of_day == hour for event in events)
            session.add_all(
                [
                    ModelParameter(
                        clinic_id=clinic.clinic_id,
                        param_name=f"lambda_alpha_hour_{hour_label}",
                        param_value=alpha,
                        fitted_at=now,
                        data_points_used=hour_count,
                    ),
                    ModelParameter(
                        clinic_id=clinic.clinic_id,
                        param_name=f"lambda_beta_hour_{hour_label}",
                        param_value=beta,
                        fitted_at=now,
                        data_points_used=hour_count,
                    ),
                ]
            )

        service_a, service_b = fit_service_posterior(clinic.clinic_id, session)
        session.add_all(
            [
                ModelParameter(
                    clinic_id=clinic.clinic_id,
                    param_name="mu_a",
                    param_value=service_a,
                    fitted_at=now,
                    data_points_used=event_count,
                ),
                ModelParameter(
                    clinic_id=clinic.clinic_id,
                    param_name="mu_b",
                    param_value=service_b,
                    fitted_at=now,
                    data_points_used=event_count,
                ),
            ]
        )
    session.commit()