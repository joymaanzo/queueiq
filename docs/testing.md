# Testing

## Backend

Install the backend dependencies and run the API tests:

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

These tests cover health and clinic discovery, valid and invalid predictions, actual-wait recording, statistics, forecasts, evaluation, and API error responses. With no `DATABASE_URL`, they use the local SQLite fallback.

## Frontend

```bash
cd frontend
npm install
npm test
```

The frontend check runs the TypeScript compiler and Vite production build.

## Integration tests

Start the full Compose environment, then run the Playwright suite from the repository root:

```bash
docker compose up --build -d
npm install
npx playwright install --with-deps chromium
npx playwright test tests/e2e/
```

The browser tests validate that the frontend loads, the health endpoint responds, a clinic can be selected, a prediction request succeeds, and a prediction remains in Postgres after restarting the backend container. The restart test requires Docker Compose and the named `postgres_data` volume.
