# PR: perf: Lighthouse-oriented web delivery, UX a11y, and HTTP regression tests

## Summary

This change set tightens production delivery for the React SPA behind Express (compression, caching rules for hashed Vite assets, security headers via Helmet without a strict CSP that would fight the bundled app), trims the initial JavaScript download with route-level lazy loading, fills in basic SEO and Open Graph meta, improves login and chrome accessibility, documents optional Cloud Run minimum instances against cold-start TTFB, and locks in behavior with Vitest-driven supertests for static file semantics and `/health`.

## Purpose

- Lab tools such as Lighthouse and PageSpeed were likely flagging large uncompressed transfers, weak cache policy on fingerprinted assets, missing description and social meta, and missing or generic accessibility names on controls.
- Cloud Run on `min-instances=0` makes cold starts visible in synthetic tests; operators need a documented, env-driven way to trade cost for steadier latency.
- None of the above should regress silently: the static `Cache-Control` rules and `/health` response are now covered by automated HTTP tests.

## Changes in This PR

### 1. Express production static behavior (`productionStaticRoutes.ts`, `server.ts`)

`setProductionStaticAssetHeaders` encodes the Vite contract: anything under `assets/` is served with a one-year immutable cache, while `index.html` and the SPA fallback response use `no-cache` so deploys take effect immediately. `attachProductionStaticServing` mounts the static directory and the catch-all that serves the SPA shell. The main server wires `helmet` (with CSP and COEP disabled to avoid breaking the current build), `compression`, and — in production only — static serving. `CLIBLE_WEB_DIST` optionally overrides the dist root for tests.

`buildExpressApplication` extracts the Express graph from startup so Vitest can import the app without opening a listening socket. Running `tsx server.ts` (or `npm start`) remains the entrypoint: startup runs only when the process entry file resolves to this module (`fileURLToPath` comparison), so importing from tests does not listen or run migrations.

### 2. Frontend payload and UX (`App.tsx`, `index.html`, `LoginView.tsx`, `utils/i18n.ts`)

Heavy views (admin, reading plans, analytics, compare, original study, full-text search surface) load through `React.lazy` inside a single `Suspense` boundary with the existing localized loading string. Shell buttons gain `type`, `aria-label`, and `aria-expanded` where meaningful; icon-only controls mark icons `aria-hidden`. `index.html` gains `description`, `theme-color`, and Open Graph descriptors. Login fields use explicit labels, `autoComplete`, and an alert role on errors.

### 3. Deploy and ops (`Taskfile.yml`, `terraform/main.tf`, `.github/workflows/deploy-web.yml`)

Terraform introduces `web_min_instance_count` (default `0`) for `scaling.min_instance_count`. Taskfile `gcloud run deploy` invocations honor `CLOUD_RUN_MIN_INSTANCES` with shell default `0`. The GitHub deploy workflow reads optional repository variable `CLOUD_RUN_MIN_INSTANCES` into the deploy step so CI can mirror local behavior without committing secrets.

### 4. Automated tests (`productionStaticRoutes.test.ts`, `server.health.test.ts`)

Unit-style checks assert which `Cache-Control` values are applied for representative paths. Integration checks build a disposable `dist`-shaped tree, attach the same static stack used in production (Helmet stub config, compression), and validate asset responses (including gzip for a payload above the compression threshold) and SPA fallback headers. A separate case builds the full Express app under `NODE_ENV=test` and asserts `/health` returns JSON plus `X-Content-Type-Options` from Helmet.

## Files added

- `src/clible-web/productionStaticRoutes.ts` — shared static serving and header helper for hashed assets vs HTML shell.
- `src/clible-web/productionStaticRoutes.test.ts` — header unit tests and supertest integration for static + gzip + SPA fallback.
- `src/clible-web/server.health.test.ts` — supertest for `/health` and baseline security headers on the full app factory.

## Files modified

- `src/clible-web/server.ts` — Helmet, compression, `buildExpressApplication`, `CLIBLE_WEB_DIST`, gated process entry, delegates static serving to `productionStaticRoutes`.
- `src/clible-web/package.json` / `package-lock.json` — `compression`, `helmet`, dev `supertest` and `@types/supertest`.
- `src/clible-web/App.tsx` — lazy routes, Suspense fallback, header accessibility, `aria-hidden` on decorative chrome.
- `src/clible-web/index.html` — meta description, theme-color, Open Graph tags.
- `src/clible-web/views/LoginView.tsx` — labels, autocomplete, alert semantics.
- `src/clible-web/utils/i18n.ts` — strings for new `aria-label` keys (history, translation picker, admin).
- `Taskfile.yml` — documented `CLOUD_RUN_MIN_INSTANCES` for both deploy tasks.
- `terraform/main.tf` — `web_min_instance_count` variable wired into Cloud Run scaling.
- `.github/workflows/deploy-web.yml` — optional `vars.CLOUD_RUN_MIN_INSTANCES` passed into `gcloud`.

## Tests

```bash
uv run pytest -v
uv run ruff check .
uv run ruff format --check .
cd src/clible-web && npm run lint
cd src/clible-web && npm run test
```

**345** Python tests passed; coverage **94.36%** (gate ≥ 80%). **56** Vitest tests passed (`npm run test`), including new supertests. `npm run lint` (`tsc --noEmit`) clean.

## Usage

```bash
# Local production-ish run with custom dist tree (advanced)
export NODE_ENV=production
export CLIBLE_WEB_DIST=/path/to/vite/dist
tsx server.ts
```

Demonstrates overriding the SPA root without relying on `process.cwd()/dist`.

```bash
# Deploy with one warm instance (higher baseline cost)
export CLOUD_RUN_MIN_INSTANCES=1
task deploy-cloud-run
```

Shows reducing cold-start impact on Lighthouse TTFB at the expense of idle billing.

## Notes

Content Security Policy remains disabled for now; tightening CSP safely would mean nonces or hashes aligned with Vite output and warrants a focused follow-up. Canonical URL meta was omitted deliberately until a stable public origin is chosen. PSI field data was not available in the earlier crawl; revisiting Opportunities after deploy remains the fastest way to prioritize any remaining audits.

## Related documentation

- [docs/guides/deployment.md](docs/guides/deployment.md) — Cloud Run overview (operators may mirror new env vars here in a future doc-only PR if desired).

