# Deployment

QueueIQ deploys to Render.com. The `render.yaml` blueprint defines the Docker web service and a managed PostgreSQL database. Render uses `/health` as the service health check.

The public URL is the URL assigned to the `queueiq-api` Render web service. Set it as the `RENDER_SERVICE_URL` GitHub Actions secret for the post-deploy smoke test.

## Environment variables

- `DATABASE_URL`: Render's managed Postgres connection string.
- `ENVIRONMENT=production`: production runtime marker.
- `RENDER_DEPLOY_HOOK_URL`: GitHub secret used to trigger the Render deployment.
- `RENDER_SERVICE_URL`: GitHub secret containing the public app URL used by the smoke test.

Database tables are created automatically by the FastAPI lifespan startup, and the idempotent synthetic seed runs when the database is empty.

## Redeploy

Push a change to `main`. GitHub Actions runs CI first; the deploy workflow triggers Render only after CI succeeds. Render's health check must pass before the deployment is considered healthy.
