# QueueIQ

QueueIQ is a Bayesian clinic queue prediction platform that estimates patient wait times from synthetic historical queue data and current queue conditions.

## Architecture

```text
+----------------------+       REST + CORS       +----------------------+
| React + TypeScript   | <----------------------> | FastAPI backend      |
| Vite + Tailwind      |                          | Bayesian prediction  |
| Recharts             |                          | Synthetic generator  |
+----------------------+                          +----------+-----------+
                                                               |
                                                               v
                                                    +----------------------+
                                                    | SQLite               |
                                                    | queueiq.db           |
                                                    +----------------------+
```

## Quick Start (Docker)

```bash
docker-compose up --build
```

- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

Do not use `docker-compose down -v` during normal development; the named volume stores the SQLite database.

## Local Development (without Docker)

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Testing

```bash
cd backend && pytest -v
cd frontend && npm run build
```

## Project Structure

```text
backend/
  app/                 FastAPI application, Bayesian model, and evaluation
  data/                SQLite database for local development
  scripts/              Synthetic data seeding scripts
  tests/                Backend tests
  Dockerfile
frontend/
  src/                 React components and API client
  public/               Static assets
  Dockerfile
  nginx.conf
docker-compose.yml     Backend and frontend services
```

## Data

- Synthetic only: 3 clinics, 30+ days, and 500+ events per clinic.
- SQLite is stored at `backend/data/queueiq.db` locally or `/app/data/queueiq.db` in Docker.
- Docker persistence is provided by the named volume `queueiq_data`.

## Module 2 Scope

- Bayesian queue prediction with conditional and unconditional modes
- Historical statistics, staff forecast, and evaluation metrics
- No authentication, no real clinic integration, and synthetic data only

## Verification Steps

1. Run `docker-compose up --build`.
2. Check `curl http://localhost:8000/health`.
3. Open http://localhost:5173, select a clinic, and predict a wait.
4. Run `docker-compose down`.
5. Run `docker-compose up`.
6. Confirm predictions persist across the restart.
