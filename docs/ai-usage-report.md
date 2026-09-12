# AI Usage Report — QueueIQ Module 2

## Summary

- **Total sessions:** ~8
- **Total hours:** ~25
- **Primary AI tools used:** GitHub Copilot (Agent mode), Claude (planning + debugging)
- **Secondary tools:** ChatGPT (spec review), GitHub Codespaces (execution environment)

## Project Overview

QueueIQ is a Bayesian clinic wait-time prediction platform. It predicts how long
a patient will wait at a walk-in clinic, given the clinic, the arrival time, and
optionally the current queue length.

## What I Built

- **Backend:** FastAPI + SQLAlchemy + SQLite
  - Bayesian conjugate model (Gamma-Poisson for arrivals, Gamma-Exponential for service)
  - Posterior-predictive Monte Carlo simulation (10,000 draws)
  - Erlang-C steady-state for unconditional predictions
  - 6 REST endpoints
- **Frontend:** React + TypeScript + Vite + Tailwind + Recharts
  - 4 tabs: Predict, History, Staff, Stats
  - Real-time API integration
- **Data:** 5,157 synthetic queue events across 3 clinics, 30 days
- **Tests:** 20+ backend tests (unit + integration)
- **Packaging:** Docker Compose with named volume persistence
- **Docs:** product-spec.md, AGENTS.md, README.md

## Tools Used and Why

| Tool | Role |
|---|---|
| **GitHub Copilot (Agent mode)** | Primary code generation — wrote backend, frontend, tests, Docker files |
| **Claude (web)** | Spec writing, debugging model calibration, statistical review |
| **GitHub Codespaces** | Cloud dev environment (no local Python/Node setup needed) |
| **FastAPI** | Chosen for auto-generated OpenAPI docs |
| **pytest + HTTPX** | Standard Python testing stack |
| **Recharts** | Simple React charting library |
| **Tailwind CSS** | Utility-first styling for fast UI iteration |

## Challenges

### 1. Bayesian model calibration
The biggest technical challenge was getting the model to produce predictions that
matched historical data. The initial simulation under-predicted peak-hour waits by
40%. Fixed by:
- Switching from a closed-form approximation to full posterior-predictive simulation
- Adding Erlang-C steady-state for unconditional predictions
- Adding empirical calibration checks against historical averages

### 2. Conditional vs unconditional predictions
Distinguishing "if I go now, how long will I wait?" (unconditional) from "given
there are 5 people ahead of me, how long will I wait?" (conditional) required
rethinking the model's API surface. Copilot Agent was useful for iterating on the
interface quickly.

### 3. Docker + Codespaces integration
Baking the correct API URL into the frontend at build time was tricky because
Codespaces uses dynamic forwarded URLs. Solved by deriving the backend URL
dynamically from `window.location.hostname` in `api.ts`.

## What Went Smoothly

- **Synthetic data generation** — Poisson + Exponential model produced realistic
  queue dynamics on the first try
- **Frontend scaffolding** — Vite + React + Tailwind worked out of the box
- **API auto-documentation** — FastAPI's `/docs` endpoint worked without extra config
- **Docker packaging** — Multi-stage frontend build + nginx serving was straightforward

## AI Usage Patterns That Worked Well

1. **Spec-first development** — writing product-spec.md before any code gave the AI
   agent a stable target
2. **Phase-by-phase prompts** — asking for one phase at a time (backend, then data,
   then model, then API, then frontend) kept the agent focused
3. **Verification gates** — after each phase, running tests and curl checks before
   moving on caught bugs early
4. **Committing per phase** — using commit messages like `feat(phase-c): Bayesian
   model` made rollback easy when something broke
5. **Using AGENTS.md as a contract** — the agent respected the phase structure and
   stayed in scope

## Key Metrics

- **Commits:** 8 (one per phase + initial spec + polish)
- **Backend files:** ~15 Python modules
- **Frontend files:** ~10 React components + API client
- **Tests:** 20+ (unit + integration)
- **Synthetic events:** 5,157 across 3 clinics
- **Bayesian simulation draws:** 10,000 per prediction
- **Endpoints:** 6 REST + 1 auto-generated OpenAPI spec
- **Docker services:** 2 (backend + frontend)
- **Model MAE:** 10.1 min (Central Medical) — beats baseline by up to 88%

## Reflection

The AI-assisted workflow transformed what would have been a 2-week solo project
into a ~2-day focused build. The key lesson: **be specific with the spec, then let
the agent execute one phase at a time, verifying after each**.

The hardest part wasn't writing code — it was ensuring the Bayesian model was
statistically defensible. AI was great at writing the math; it was less reliable
at catching when the math was calibrated wrong. That required human judgment and
iteration against real data.

The final product — a full-stack Bayesian queue-prediction platform with tests,
Docker packaging, and evaluation metrics — would not have been feasible in the
same timeframe without AI assistance.
EOFcd /workspaces/queueiq
mkdir -p docs
cat > docs/ai-usage-report.md << 'EOF'
# AI Usage Report — QueueIQ Module 2

## Summary

- **Total sessions:** ~8
- **Total hours:** ~25
- **Primary AI tools used:** GitHub Copilot (Agent mode), Claude (planning + debugging)
- **Secondary tools:** ChatGPT (spec review), GitHub Codespaces (execution environment)

## Project Overview

QueueIQ is a Bayesian clinic wait-time prediction platform. It predicts how long
a patient will wait at a walk-in clinic, given the clinic, the arrival time, and
optionally the current queue length.

## What I Built

- **Backend:** FastAPI + SQLAlchemy + SQLite
  - Bayesian conjugate model (Gamma-Poisson for arrivals, Gamma-Exponential for service)
  - Posterior-predictive Monte Carlo simulation (10,000 draws)
  - Erlang-C steady-state for unconditional predictions
  - 6 REST endpoints
- **Frontend:** React + TypeScript + Vite + Tailwind + Recharts
  - 4 tabs: Predict, History, Staff, Stats
  - Real-time API integration
- **Data:** 5,157 synthetic queue events across 3 clinics, 30 days
- **Tests:** 20+ backend tests (unit + integration)
- **Packaging:** Docker Compose with named volume persistence
- **Docs:** product-spec.md, AGENTS.md, README.md

## Tools Used and Why

| Tool | Role |
|---|---|
| **GitHub Copilot (Agent mode)** | Primary code generation — wrote backend, frontend, tests, Docker files |
| **Claude (web)** | Spec writing, debugging model calibration, statistical review |
| **GitHub Codespaces** | Cloud dev environment (no local Python/Node setup needed) |
| **FastAPI** | Chosen for auto-generated OpenAPI docs |
| **pytest + HTTPX** | Standard Python testing stack |
| **Recharts** | Simple React charting library |
| **Tailwind CSS** | Utility-first styling for fast UI iteration |

## Challenges

### 1. Bayesian model calibration
The biggest technical challenge was getting the model to produce predictions that
matched historical data. The initial simulation under-predicted peak-hour waits by
40%. Fixed by:
- Switching from a closed-form approximation to full posterior-predictive simulation
- Adding Erlang-C steady-state for unconditional predictions
- Adding empirical calibration checks against historical averages

### 2. Conditional vs unconditional predictions
Distinguishing "if I go now, how long will I wait?" (unconditional) from "given
there are 5 people ahead of me, how long will I wait?" (conditional) required
rethinking the model's API surface. Copilot Agent was useful for iterating on the
interface quickly.

### 3. Docker + Codespaces integration
Baking the correct API URL into the frontend at build time was tricky because
Codespaces uses dynamic forwarded URLs. Solved by deriving the backend URL
dynamically from `window.location.hostname` in `api.ts`.

## What Went Smoothly

- **Synthetic data generation** — Poisson + Exponential model produced realistic
  queue dynamics on the first try
- **Frontend scaffolding** — Vite + React + Tailwind worked out of the box
- **API auto-documentation** — FastAPI's `/docs` endpoint worked without extra config
- **Docker packaging** — Multi-stage frontend build + nginx serving was straightforward

## AI Usage Patterns That Worked Well

1. **Spec-first development** — writing product-spec.md before any code gave the AI
   agent a stable target
2. **Phase-by-phase prompts** — asking for one phase at a time (backend, then data,
   then model, then API, then frontend) kept the agent focused
3. **Verification gates** — after each phase, running tests and curl checks before
   moving on caught bugs early
4. **Committing per phase** — using commit messages like `feat(phase-c): Bayesian
   model` made rollback easy when something broke
5. **Using AGENTS.md as a contract** — the agent respected the phase structure and
   stayed in scope

## Key Metrics

- **Commits:** 8 (one per phase + initial spec + polish)
- **Backend files:** ~15 Python modules
- **Frontend files:** ~10 React components + API client
- **Tests:** 20+ (unit + integration)
- **Synthetic events:** 5,157 across 3 clinics
- **Bayesian simulation draws:** 10,000 per prediction
- **Endpoints:** 6 REST + 1 auto-generated OpenAPI spec
- **Docker services:** 2 (backend + frontend)
- **Model MAE:** 10.1 min (Central Medical) — beats baseline by up to 88%

## Reflection

The AI-assisted workflow transformed what would have been a 2-week solo project
into a ~2-day focused build. The key lesson: **be specific with the spec, then let
the agent execute one phase at a time, verifying after each**.

The hardest part wasn't writing code — it was ensuring the Bayesian model was
statistically defensible. AI was great at writing the math; it was less reliable
at catching when the math was calibrated wrong. That required human judgment and
iteration against real data.

The final product — a full-stack Bayesian queue-prediction platform with tests,
Docker packaging, and evaluation metrics — would not have been feasible in the
same timeframe without AI assistance.
