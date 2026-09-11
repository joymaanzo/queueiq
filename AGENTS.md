# AGENTS.md — QueueIQ Build Instructions

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
