# Release Process

1. Commit the change locally and push the branch.
2. Open a pull request into `main`.
3. Wait for all parallel CI jobs to pass: backend tests, frontend build, Compose integration tests, and Docker build.
4. Merge the pull request into `main`.
5. The deploy workflow triggers Render only after the successful `main` CI workflow.
6. Confirm the Render deployment and `/health` smoke test succeed.

## Check status

Open the repository's **Actions** tab on GitHub. The CI workflow and the dependent Deploy workflow show logs for every job and smoke-test attempt.

## Roll back

Revert the problematic commit, push the revert to `main`, and let CI/CD run again. Render will auto-deploy the reverted source after CI succeeds. If a deployment is unhealthy, Render's service health check prevents it from becoming healthy; fix or revert the source and push again.
