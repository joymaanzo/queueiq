"""
generate_queueiq_docs.py

Creates product-spec.md and AGENTS.md in the QueueIQ project folder.
Run:  python generate_queueiq_docs.py
"""

from pathlib import Path

TARGET_DIR = Path(r"C:\Users\Maaan\OneDrive\Desktop\PROJECT QUEUEIQ")

PRODUCT_SPEC = r"""# QueueIQ — Product Specification

**Version:** 1.1
**Module:** Module 2 MVP
**Status:** Ready for implementation

---

## 1. Product Overview

QueueIQ is a full-stack web application that predicts clinic waiting times using historical queue data, current queue conditions, and Bayesian statistical modelling.

It helps patients decide when to visit a clinic, clinic staff understand expected demand, and clinic managers evaluate queue patterns and prediction accuracy.

Module 2 uses **synthetic clinic data only**. No real clinic systems, patient records, medical information, or authentication are used.

---

## 2. Problem Statement

Patients arriving at clinics have no reliable way to know how long they will wait. Current approaches include arriving and waiting, calling ahead, relying on receptionist estimates, relying on prior experience, or avoiding the clinic entirely.

Patients experience wasted time, frustration, difficulty planning, and delayed care. Clinics experience unpredictable demand, difficulty identifying peaks, inefficient staffing, and no historical visibility.

QueueIQ turns historical queue data into a probabilistic estimate of future waiting time.

---

## 3. Product Vision

A patient should be able to answer: "If I go to this clinic now, how long am I likely to wait?"

The system returns a point estimate, a likely range, an 80% prediction interval, and a busyness indicator.

---

## 4. Core Value Proposition

QueueIQ reduces uncertainty around clinic waiting times by giving patients statistically informed predictions while giving clinics visibility into queue patterns and expected demand.

---

## 5. Users

### 5.1 Patient
Member of the public considering a GP, general clinic, urgent care, or dental visit. Occasional use. Low to moderate technical skill.

### 5.2 Clinic Staff
Receptionist or front-desk staff managing patient flow. Daily use. Moderate technical skill.

### 5.3 Clinic Manager
Responsible for operational efficiency, staffing, scheduling. Weekly analysis. Moderate to high technical skill.

### 5.4 Future User — Data Analyst (Out of Scope for Module 2)

---

## 6. User Stories

### US-001 — Patient Checks Wait Time
As a patient, I want to select a clinic and time and receive a predicted waiting time so that I can decide whether to visit now or later.

### US-002 — Patient Views Historical Patterns
As a patient, I want to view typical waiting times by hour so that I can choose a better time to visit.

### US-003 — Patient Reports Actual Wait
As a patient, I want to report my actual waiting time so QueueIQ can evaluate and improve future predictions.

### US-004 — Staff Views Expected Demand
As clinic staff, I want to see expected patient arrivals for the next several hours so I can prepare for busy periods.

### US-005 — Staff Views Peak Times
As clinic staff, I want to see historically busy hours and days so I can plan staffing and preparation.

### US-006 — Manager Evaluates Model
As a clinic manager, I want to see how accurate QueueIQ predictions have been so I can determine whether the system is reliable.

### US-007 — Patient Compares Clinics (P2)

---

## 7. MVP Scope

### 7.1 In Scope

Frontend: clinic selection, time selection, queue-size input, wait-time prediction, prediction interval, prediction level, busyness indicator, historical wait chart, actual-wait submission, staff demand view, prediction accuracy statistics.

Backend endpoints:
- GET /health
- GET /clinics
- POST /predict-wait-time
- POST /record-actual-wait
- GET /clinic/{id}/stats
- GET /clinic/{id}/forecast

Database (SQLite): clinics, queue_events, predictions, model_parameters, clinic_hourly_stats.

---

## 8. Out of Scope

Clinic admin dashboard, patient accounts, mobile application, WebSockets, real clinic integration, SMS notifications, prescription refills, payment processing, HIPAA compliance, multi-language support, full WCAG certification, neural-network ML, 1M-user scalability, appointment booking, prescription management, insurance verification, telemedicine.

---

## 9. Synthetic Clinics

### 9.1 Central Medical
General Practice. Large. 4 doctors. 07:00–19:00. Mon–Fri. ~80 patients/day. Downtown.

### 9.2 Midtown Urgent Care
Urgent Care. Medium. 2 doctors. 09:00–17:00. Mon–Sat. ~40 patients/day. Residential/commercial.

### 9.3 Riverside Family Dental
Dental. Small. 1 dentist + 1 hygienist. 08:00–16:00. Tue–Fri. ~20 patients/day. Suburban.

---

## 10. Synthetic Queue Dynamics

### 10.1 Patient Arrivals
Poisson processes. Rates vary by clinic, hour, day of week. Peaks: 08:00–10:00, 12:00–13:00, 15:00–17:00. Monday busier. Friday quieter. No seasonal variation in Module 2.

### 10.2 Arrival Rates

Central Medical: base lambda = 8/hour; peaks 12, 11, 10; Friday ~6.
Midtown Urgent Care: base lambda = 5/hour; occasional spike to 9.
Riverside Family Dental: base lambda = 3/hour; morning 5; after 14:00 = 2.

### 10.3 Service Times
Exponential throughout. Central Medical mean 20 min. Midtown Urgent Care mean 15 min. Riverside Family Dental mean 12 min.

---

## 11. Queue Simulation

Waiting times must emerge from arrival and service processes, not be generated directly. For each day: draw Poisson arrivals per hour, assign timestamps, sort, assign to first free server (FIFO across c servers), compute service_start = max(arrival, server_free), draw Exponential service duration, update server_free, record wait and duration.

Reproducibility: use np.random.default_rng(42). Pin NumPy version.

---

## 12. Data Model

### 12.1 clinics
clinic_id PK, name, location, service_type, capacity_doctors, capacity_patients_per_day, hours_open, days_open, created_at

### 12.2 queue_events
event_id PK, clinic_id FK, patient_id, arrival_time, service_start_time, service_end_time, actual_wait_time_minutes, service_duration_minutes, day_of_week, hour_of_day

### 12.3 predictions
prediction_id PK, clinic_id FK, timestamp_of_prediction, predicted_wait_time_minutes, confidence_interval_lower, confidence_interval_upper, confidence_level, actual_wait_time_minutes (nullable), reported_at (nullable)

### 12.4 model_parameters
param_id PK, clinic_id FK, param_name, param_value, fitted_at, data_points_used

### 12.5 clinic_hourly_stats
stat_id PK, clinic_id FK, day_of_week, hour_of_day, avg_wait_minutes, std_wait_minutes, sample_count, last_updated

---

## 13. Bayesian Model

### 13.1 Prediction Target
Waiting time until service begins, in minutes.

### 13.2 Inputs
Clinic, time of day (hour bucket), day of week, current queue length, historical arrival rate lambda, historical service rate mu.

### 13.3 Outputs
predicted_wait_minutes, confidence_interval_lower, confidence_interval_upper, confidence_level, busyness, prediction_id.

### 13.4 Arrival Model
A_t ~ Poisson(lambda_t). Gamma prior: lambda ~ Gamma(alpha0, beta0). Posterior: lambda | data ~ Gamma(alpha0 + sum(A), beta0 + H). Priors: alpha0 = 2, beta0 = 0.25.

### 13.5 Service Model
S ~ Exponential(mu). Gamma prior on mu: mu ~ Gamma(a0, b0). Posterior: mu | data ~ Gamma(a0 + n, b0 + sum(S)). Priors: a0 = 2, b0 = 0.1.

### 13.6 Queue Prediction
Posterior-predictive discrete-event simulation. Draw N = 10,000 joint samples (lambda_i, mu_i). For each sample, initialize c servers, place Q patients at time 0, simulate next 60 minutes of arrivals, assign to first free server, record wait for a hypothetical new arrival at time 0. Aggregate: median as point estimate, 10th and 90th percentiles for 80% interval.

### 13.7 Busyness Thresholds
Low: < 15 min. Moderate: 15–30 min. High: > 30 min. Computed on backend only.

---

## 14. Statistical Terminology
UI displays "80% prediction interval". API uses confidence_level for backwards compatibility. OpenAPI must note the distinction.

---

## 15. Bayesian Updating
On startup: load queue_events, compute posteriors, write model_parameters, load into memory. On record-actual-wait: reject duplicates with 409, store actual, compute error, refresh hourly stats. Full refit on startup.

---

## 16. API Specification

All errors use schema: {"detail": "...", "code": "..."}

HTTP codes: 200 success, 400 validation, 404 not found, 409 conflict, 500 internal.

### GET /health
{"status": "ok", "database": "connected", "model_loaded": true}

### GET /clinics
Array of clinic objects.

### POST /predict-wait-time
Request: {"clinic_id": 1, "timestamp": "2026-09-11T14:30:00", "current_queue_length": 5}
Response: {"clinic_id": 1, "predicted_wait_minutes": 24.0, "confidence_interval_lower": 19.0, "confidence_interval_upper": 29.0, "confidence_level": 0.80, "busyness": "moderate", "prediction_id": 1234}

### POST /record-actual-wait
Request: {"prediction_id": 1234, "actual_wait_minutes": 22.0}
Response: {"status": "recorded", "prediction_id": 1234, "actual_wait_minutes": 22.0, "error_minutes": -2.0}
Errors: 404 PREDICTION_NOT_FOUND, 409 ACTUAL_WAIT_ALREADY_REPORTED, 400 INVALID_WAIT_VALUE.

### GET /clinic/{id}/stats
Returns hourly_stats and daily_stats.

### GET /clinic/{id}/forecast
Returns forecast array with hours_ahead, window, expected_arrivals, busyness.

---

## 17. Frontend Requirements
Main interface: clinic selector, time input, queue size input, predict button, prediction card, historical chart, actual-wait form, stats panel.

Components: ClinicSelector, TimeInput, QueueSizeInput, PredictionForm, PredictionCard, BusynessIndicator, HistoricalChart, ActualWaitForm, StaffDashboard, StatsPanel.

Technology: React + TypeScript, Recharts, Tailwind CSS.

---

## 18. Backend Technology
FastAPI, NumPy, SciPy, SQLite + SQLAlchemy, Uvicorn. CORS enabled via FRONTEND_ORIGIN env var. Structured logging to stdout. Global exception handler returning standard error schema.

---

## 19. Docker
docker-compose runs backend and frontend. Named volume queueiq_data mounted at /app/data. SQLite file at /app/data/queueiq.db. Do not use docker-compose down -v in normal workflow.

---

## 20. Testing
Pytest for backend. HTTPX for API integration. Test posterior calculations, predictions, interval ordering, queue-size behavior, clinic differences, hour differences. Test all endpoints including 404/409/400. Test DB persistence. Test frontend forms.

---

## 21. Synthetic Data Generation
NumPy + datetime. SEED = 42 via np.random.default_rng. Pin NumPy version. Minimum 30 days per clinic, 500 events per clinic. Target 2000-5000 total events. Auto-generate if DB empty.

---

## 22. Acceptance Criteria

Functional: frontend loads < 2s, prediction returned < 1s, prediction includes point + interval + level + busyness, historical data viewable, actual wait submittable with 409 on duplicate, staff forecast shows 1/2/4-hour windows, backend stores all, DB persists.

Accuracy: MAE < 10 min, 80% interval achieves 70-90% coverage, beats historical-average baseline, sensible differences by hour and clinic.

Technical: >80% test coverage on Bayesian core, all endpoints tested, frontend workflow tested, docker-compose works, OpenAPI docs at /docs, no critical startup errors, CORS configured, global error handler, SQLite persists.

Data: 30 days per clinic, 500 events per clinic, morning peaks visible, day-of-week variation visible, clinics differ, service times vary, waits emerge from queue dynamics.

---

## 23. Security & Privacy Scope
Synthetic data only. No real patient information, medical records, passwords, accounts, or identifiers.

---

## 24. Model Evaluation
Baseline: historical average wait for relevant clinic x day x hour. Metrics: MAE, prediction interval coverage. Target coverage for 80% interval: 70-90%.

---

## 25. Model Update Strategy
Startup: load queue_events, compute posteriors, store model_parameters, load model. Actual-wait submission: store, compute error, refresh hourly stats. Next startup: recalculate posteriors.

---

## 26. Non-Goals
Not a medical diagnosis system, treatment recommendation, appointment booking, EHR, insurance platform, telemedicine, prescription system, emergency triage, or production hospital-management system.

---

## 27. Success Story
A patient opens QueueIQ at 2:30 PM on a Wednesday, selects Central Medical, and sees "Estimated wait: 18 minutes — likely range 14-23 minutes. Busyness: Moderate." They visit and later report an actual 17-minute wait. QueueIQ stores the result and incorporates it into future Bayesian updates.

---

## 28. Architecture
React + TypeScript frontend calls FastAPI backend via REST with CORS. Backend uses Bayesian model, SQLite database, and synthetic data engine.

---

## 29. Primary User Flow
Open QueueIQ, select clinic, select time, enter queue length, click Predict Wait, FastAPI runs posterior predictive simulation, prediction stored, frontend displays result, patient decides, optionally reports actual wait, backend calculates error and refreshes stats, future model update on next startup.

---

## 30. Implementation Priorities

P0: FastAPI backend, SQLite database, synthetic queue generation, Bayesian model, POST /predict-wait-time, React frontend, clinic selection, prediction display, persistent database, tests, Docker Compose, CORS + error schema.

P1: Historical charts, actual-wait submission with 409 handling, staff forecast with time windows, historical stats, baseline comparison, model evaluation.

P2: Clinic comparison, advanced visualizations, automatic refitting, dashboard polish.

---

## 31. Definition of Done
Three clinics exist. Synthetic data exists (30+ days, 500+ events/clinic). SQLite works and persists. Bayesian model loads and predicts with intervals. All 6 endpoints work. React frontend works end-to-end. Prediction card, chart, actual-wait form, staff forecast functional. Model evaluation works. Duplicate reports return 409. Tests pass. docker-compose up works. OpenAPI docs available. README explains setup. No real patient data.

---

## 32. Final Product Definition
QueueIQ is a full-stack Bayesian clinic queue prediction platform. It uses synthetic historical queue data and current queue conditions to estimate how long a patient will wait before receiving service. Patients can view predictions, uncertainty ranges, historical patterns, and optionally report actual waits. Clinic staff can view expected demand and peak periods. The backend persists queue events and predictions in SQLite and evaluates the Bayesian model against a historical-average baseline.

Core loop: DATA -> BAYESIAN MODEL -> PREDICTION -> PATIENT DECISION -> ACTUAL WAIT -> EVALUATION -> MODEL UPDATE

---

## 33. Known Limitations
No seasonality. Hour-bucket lambda only. Exponential service times. Single-queue M/M/c assumption. No real-time updates. Naive timestamps. Synthetic data only. No authentication. SQLite concurrency limits. Fixed priors.

---

## 34. Changelog v1.0 to v1.1
1. Service times fixed to Exponential (generator + likelihood aligned).
2. Queueing model upgraded to posterior-predictive discrete-event simulation.
3. Busyness thresholds defined.
4. Standard error schema + HTTP codes.
5. Duplicate actual-wait reports rejected with 409.
6. Forecast response includes time window.
7. CORS, logging, global error handler specified.
8. Docker volume details specified.
9. Reproducibility via np.random.default_rng.
10. clinic_hourly_stats refresh policy specified.
11. Statistical terminology note for confidence_level.
12. Known Limitations section added.
"""

AGENTS_MD = r"""# AGENTS.md — QueueIQ Build Instructions

This file guides AI coding agents building QueueIQ Module 2. Read the full product-spec.md before starting. This file is the execution plan; the spec is the source of truth.

---

## 0. Prime Directives

1. Follow the spec. If the spec and this file disagree, the spec wins.
2. Build in the order in Section 2. Do not jump ahead.
3. Test as you go. Every P0 module ships with tests.
4. No scope creep. P2 features are only touched if P0 and P1 are 100% done.
5. Synthetic data only. Never introduce real patient data.
6. Deterministic generation. Use np.random.default_rng(42). Never np.random.seed.
7. One source of truth per value. Busyness is computed once (backend). Frontend renders it.

---

## 1. Tech Stack (Locked)

Frontend: React + TypeScript (Vite recommended).
Styling: Tailwind CSS.
Charts: Recharts.
Backend: FastAPI with Pydantic v2.
Server: Uvicorn.
Bayesian: NumPy + SciPy. No PyMC3 or Stan.
DB: SQLite + SQLAlchemy at /app/data/queueiq.db.
Tests: Pytest + HTTPX for backend, Vitest for frontend.
Container: Docker Compose with named volume queueiq_data.

---

## 2. Build Order (Strict)

### Phase A — Backend Foundation
Project skeleton with backend/app, backend/tests, requirements.txt, Dockerfile. SQLAlchemy models for all 5 tables. DB init script. /health endpoint. /clinics endpoint returning 3 seeded clinics.
Exit criteria: uvicorn runs, /health and /clinics return correct JSON.

### Phase B — Synthetic Data
synthetic/generator.py implementing queue simulation. Seed 3 clinics. Generate 30+ days and 500+ events per clinic on first startup if DB is empty.
Exit criteria: DB has 1500+ queue_events total; hourly avg waits show visible peaks.

### Phase C — Bayesian Model
bayesian/priors.py, bayesian/posterior.py, bayesian/predict.py with posterior-predictive simulation (10,000 draws). Busyness function. Populate model_parameters on startup.
Exit criteria: unit tests pass for positive predictions, interval ordering, larger queue yields longer wait, different hours/clinics yield different predictions.

### Phase D — Prediction API
POST /predict-wait-time. POST /record-actual-wait with 409 on duplicate. GET /clinic/{id}/stats. GET /clinic/{id}/forecast with window field. Global error handler. CORS middleware. Structured logging.
Exit criteria: all 6 endpoints pass HTTPX integration tests including 404/409/400.

### Phase E — Frontend Foundation
Vite + React + TS + Tailwind scaffold. API client with typed interfaces. ClinicSelector, TimeInput, QueueSizeInput, PredictionForm, PredictionCard, BusynessIndicator.
Exit criteria: user can select clinic, enter queue, click Predict, and see a result.

### Phase F — Frontend P1
HistoricalChart with Recharts. ActualWaitForm with 409 handling. StaffDashboard with forecast table. StatsPanel with MAE and coverage.
Exit criteria: all P1 user stories visible and functional.

### Phase G — Evaluation
evaluation/metrics.py with MAE, coverage, baseline. Evaluation script. Expose metrics.
Exit criteria: model beats or competes with historical-average baseline.

### Phase H — Packaging
docker-compose.yml with backend + frontend and named volume. Verify persistence across restart. README.md. OpenAPI check at /docs.
Exit criteria: Definition of Done fully checked.

### Phase I — P2 (Only If Time Allows)
ClinicComparison component. Automatic refit after N=10 new actual waits. Dashboard polish.

---

## 3. Coding Conventions

Python: PEP 8, type hints, Pydantic models for all API I/O.
TypeScript: strict mode, no any in API client.
Naming: snake_case for Python/SQL, camelCase for TS variables, PascalCase for components.
Errors: never swallow exceptions; use standard error schema.
Logging: INFO for requests, ERROR for exceptions.
Comments: explain why, reference spec sections.

---

## 4. Testing Requirements

Bayesian core: Pytest with >80% coverage.
API endpoints: Pytest + HTTPX, every endpoint with happy path and 3 error cases.
DB: Pytest with insert, retrieve, persistence, FK.
Frontend forms: Vitest + Testing Library.
Frontend components: Vitest for PredictionCard.

Run pytest and npm test before declaring any phase complete.

---

## 5. Anti-Patterns (Do NOT)

Do not generate random waiting times directly. Simulate the queue.
Do not use np.random.seed(). Use np.random.default_rng(SEED).
Do not compute busyness on the frontend.
Do not return raw Python exceptions to the client.
Do not use PyMC3, Stan, or probabilistic programming frameworks.
Do not add authentication.
Do not add WebSockets.
Do not store real patient data.
Do not add P2 features before P0 and P1 are complete.
Do not use docker-compose down -v in normal workflow.

---

## 6. Definition of Done (Per Phase)

A phase is done when all exit criteria are met, tests are written and passing, no new warnings on startup, code reviewed against spec, and changes committed with a message referencing the phase.

---

## 7. Escalation Rules

Stop and consult the spec if: the spec is ambiguous, a phase cannot be completed without adding scope, tests reveal nonsensical output, Docker persistence fails, or the 1-second SLA is exceeded. Document the issue, propose 2 options, pick the one that keeps the core loop intact.

---

## 8. Reference Map

Clinic definitions: spec section 9.
Arrival rates: spec section 10.2.
Service times: spec section 10.3.
Queue simulation: spec section 11.
DB schema: spec section 12.
Bayesian priors: spec sections 13.4 and 13.5.
Posterior predictive: spec section 13.6.
Busyness: spec section 13.7.
API contract: spec section 16.
Frontend layout: spec section 17.
Docker: spec section 19.
Testing: spec section 20.
Acceptance: spec section 22.
Known limits: spec section 33.

---

## 9. Final Reminder

The core loop is sacred: DATA -> BAYESIAN MODEL -> PREDICTION -> PATIENT DECISION -> ACTUAL WAIT -> EVALUATION -> MODEL UPDATE

Every decision should protect this loop. Every optional feature is negotiable. The loop is not.
"""


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    spec_path = TARGET_DIR / "product-spec.md"
    agents_path = TARGET_DIR / "AGENTS.md"

    spec_path.write_text(PRODUCT_SPEC, encoding="utf-8")
    agents_path.write_text(AGENTS_MD, encoding="utf-8")

    print(f"Created: {spec_path}")
    print(f"Created: {agents_path}")
    print(f"\nBoth files are in: {TARGET_DIR}")


if __name__ == "__main__":
    main()