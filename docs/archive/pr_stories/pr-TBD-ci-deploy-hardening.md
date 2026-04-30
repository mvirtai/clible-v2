# ci: harden web deploy checks

This PR tightens the web deployment path so Cloud Run deploys are gated by the same checks used for pull requests and runtime health checks target an explicit endpoint.

## Summary

- Add a lightweight `/health` endpoint to the Express server for container and platform health checks.
- Point the web Docker image health check at `/health`.
- Run web install, TypeScript checks, and Vite build before the Cloud Run deploy image is built.
- Use the shared `CLIBLE_GCP_ARTIFACT_REGISTRY` secret as the deploy image prefix.

## Files added

- None.

## Files modified

- `.github/workflows/deploy-web.yml` — adds Node/Task setup, web preflight checks, and shared registry prefix usage.
- `src/clible-web/server.ts` — adds the `/health` route before authenticated routes and static asset handling.
- `src/clible-web/Dockerfile` — aligns the container health check with the explicit server health route.

## Tests

- `npm ci && npm run lint && npm run build` — passed; verifies the same web install, TypeScript, and Vite build checks used by deploy preflight.
- `curl -i http://localhost:3000/health` — passed against the production-mode Express server; returned `HTTP/1.1 200 OK` and `{"status":"ok"}`.
- `docker build -f src/clible-web/Dockerfile -t clible-web-healthcheck-test .` — not run locally because Docker is not installed in this environment.
