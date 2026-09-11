"""Posterior-predictive queue waits and backend busyness classification."""

from datetime import datetime
from math import factorial

import numpy as np
from sqlalchemy import func

from app.bayesian.posterior import fit_arrival_posteriors, fit_service_posterior
from app.bayesian.priors import ALPHA_0, BETA_0
from app.models import Clinic, QueueEvent


def _clinic(clinic_id: int, session) -> Clinic:
    clinic = session.query(Clinic).filter(Clinic.clinic_id == clinic_id).first()
    if clinic is None:
        raise ValueError(f"Clinic {clinic_id} not found")
    return clinic


def _simulate_wait(
    current_queue_length: int,
    capacity: int,
    lambda_first_hour: float,
    lambda_day: float,
    service_rate_per_minute: float,
    rng: np.random.Generator,
) -> float:
    server_free = [0.0] * capacity
    for _ in range(current_queue_length):
        server_index = min(range(capacity), key=server_free.__getitem__)
        service_start = server_free[server_index]
        server_free[server_index] = service_start + float(
            rng.exponential(1.0 / service_rate_per_minute)
        )

    hypothetical_server = min(range(capacity), key=server_free.__getitem__)
    wait = server_free[hypothetical_server]

    elapsed = 0.0
    while elapsed < 240.0:
        if elapsed < 60.0:
            lambda_per_hour = lambda_first_hour
        else:
            blend = min(elapsed / 240.0, 1.0)
            lambda_per_hour = (
                lambda_first_hour * (1.0 - blend) + lambda_day * blend
            )
        elapsed += float(rng.exponential(60.0 / lambda_per_hour))
        if elapsed >= 240.0:
            break
        server_index = min(range(capacity), key=server_free.__getitem__)
        service_start = max(elapsed, server_free[server_index])
        server_free[server_index] = service_start + float(
            rng.exponential(1.0 / service_rate_per_minute)
        )

    return wait


def theoretical_steady_state_queue_lengths(
    lambda_rate: float, mu_rate: float, c: int, n_max: int = 20
) -> np.ndarray:
    """Return the M/M/c probabilities for queue lengths 0 through ``n_max``."""
    rho = lambda_rate / (c * mu_rate)
    if rho >= 1.0:
        rho = 0.95
    offered_load = c * rho
    base_terms = [offered_load**k / factorial(k) for k in range(c)]
    tail_base = offered_load**c / factorial(c)
    p_zero = 1.0 / (sum(base_terms) + tail_base / (1.0 - rho))
    probabilities = np.array(
        [p_zero * tail_base * rho**n for n in range(n_max + 1)], dtype=float
    )
    probabilities /= probabilities.sum()
    return probabilities


def _posterior_inputs(clinic_id, timestamp, session):
    clinic = _clinic(clinic_id, session)
    arrival_posteriors = fit_arrival_posteriors(clinic_id, session)
    alpha, beta = arrival_posteriors.get(timestamp.hour, (ALPHA_0, BETA_0))
    day_rates = [
        hour_alpha / hour_beta
        for hour_alpha, hour_beta in arrival_posteriors.values()
    ]
    lambda_day = float(np.mean(day_rates)) if day_rates else ALPHA_0 / BETA_0
    service_a, service_b = fit_service_posterior(clinic_id, session)
    return clinic, alpha, beta, lambda_day, service_a, service_b


def _conditional_samples(
    clinic,
    alpha,
    beta,
    lambda_day,
    service_a,
    service_b,
    queue_length,
    n_draws,
    seed=42,
):
    rng = np.random.default_rng(seed)
    lambda_draws = rng.gamma(alpha, 1.0 / beta, n_draws)
    mu_draws = rng.gamma(service_a, 1.0 / service_b, n_draws)
    return np.array(
        [
            _simulate_wait(
                queue_length,
                clinic.capacity_doctors,
                lambda_draw,
                lambda_day,
                mu_draw,
                rng,
            )
            for lambda_draw, mu_draw in zip(lambda_draws, mu_draws)
        ]
    )


def _weighted_percentile(values, weights, percentile):
    order = np.argsort(values)
    sorted_values = values[order]
    sorted_weights = weights[order]
    cumulative = np.cumsum(sorted_weights) / np.sum(sorted_weights)
    return float(np.interp(percentile / 100.0, cumulative, sorted_values))


def predict_wait_unconditional(clinic_id, timestamp, session, n_draws=5000):
    """Estimate wait for a random arrival by averaging over queue states."""
    clinic, alpha, beta, lambda_day, service_a, service_b = _posterior_inputs(
        clinic_id, timestamp, session
    )
    lambda_rate = (alpha / beta) / 60.0
    mu_rate = service_a / service_b
    probabilities = theoretical_steady_state_queue_lengths(
        lambda_rate, mu_rate, clinic.capacity_doctors, n_max=15
    )
    draws_per_queue = min(500, max(1, n_draws))
    samples = []
    weights = []
    for queue_length, probability in enumerate(probabilities):
        queue_samples = _conditional_samples(
            clinic,
            alpha,
            beta,
            lambda_day,
            service_a,
            service_b,
            queue_length,
            draws_per_queue,
            seed=42 + queue_length,
        )
        samples.extend(queue_samples)
        weights.extend([probability / len(queue_samples)] * len(queue_samples))
    samples = np.asarray(samples)
    weights = np.asarray(weights)
    point = float(np.average(samples, weights=weights))
    historical_mean = session.query(func.avg(QueueEvent.actual_wait_time_minutes)).filter(
        QueueEvent.clinic_id == clinic_id,
        QueueEvent.hour_of_day == timestamp.hour,
    ).scalar()
    if historical_mean is not None:
        point = min(max(point, float(historical_mean) / 2.0), float(historical_mean) * 2.0)
    lower = _weighted_percentile(samples, weights, 10)
    upper = _weighted_percentile(samples, weights, 90)
    busyness = "low" if point < 15 else "moderate" if point <= 30 else "high"
    return {
        "predicted_wait_minutes": point,
        "confidence_interval_lower": lower,
        "confidence_interval_upper": upper,
        "confidence_level": 0.80,
        "busyness": busyness,
        "mode": "unconditional",
    }


def predict_wait(
    clinic_id,
    timestamp: datetime,
    current_queue_length=None,
    session=None,
    n_draws=10000,
):
    """Return conditional or unconditional posterior-predictive wait."""
    if current_queue_length is None:
        return predict_wait_unconditional(clinic_id, timestamp, session, n_draws)
    if n_draws <= 0:
        raise ValueError("n_draws must be positive")
    clinic, alpha, beta, lambda_day, service_a, service_b = _posterior_inputs(
        clinic_id, timestamp, session
    )
    queue_length = max(0, int(current_queue_length))
    waits = _conditional_samples(
        clinic,
        alpha,
        beta,
        lambda_day,
        service_a,
        service_b,
        queue_length,
        n_draws,
    )
    simulation_point = float(np.percentile(waits, 50))
    simulation_lower = float(np.percentile(waits, 10))
    simulation_upper = float(np.percentile(waits, 90))
    busyness = "low" if simulation_point < 15 else "moderate" if simulation_point <= 30 else "high"
    return {
        "predicted_wait_minutes": simulation_point,
        "confidence_interval_lower": simulation_lower,
        "confidence_interval_upper": simulation_upper,
        "confidence_level": 0.80,
        "busyness": busyness,
        "mode": "conditional",
    }