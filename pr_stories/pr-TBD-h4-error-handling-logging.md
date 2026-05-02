# PR: feat: structured logging, HTTP retries, and consistent CLI/API errors (H4)

## Summary

This PR delivers the H4 “Error handling & logging” milestone: structlog-based structured logging at CLI startup, tenacity-backed retries for seed XML downloads and GitHub catalog fetches, clearer handling of network failures in seed commands, and Express middleware so unmatched `/api/*` routes return JSON 404 while unhandled errors return a safe 500 response.

## Purpose

- Offline-first seeding still hits the network; transient failures should retry instead of failing immediately.
- Operators and developers need machine-readable logs (`CLIBLE_LOG_FORMAT=json`) without polluting stdout used for CLI data and pipes.
- Users should see actionable messages for common failures (timeouts, connection errors) instead of raw tracebacks.
- The web bridge should not fall through to the SPA for unknown API paths, and unexpected server errors should be logged consistently.

## Changes in This PR

### 1. Logging (`src/clible/logging_config.py`, `src/clible/cli.py`)

- Configure structlog once from the root Click group via `CLIBLE_LOG_LEVEL` and `CLIBLE_LOG_FORMAT` (default `WARNING` / `console`).
- Logs go to stderr via `PrintLoggerFactory`; processor chain avoids `stdlib.add_logger_name` (incompatible with `PrintLogger`).

### 2. HTTP retries (services)

- `src/clible/services/seed_service.py`: `_download_xml` wrapped with tenacity (`stop_after_attempt(3)`, exponential wait, `retry_if_exception_type(requests.exceptions.RequestException)`). Structured events: `seed.download.start`, `seed.download.complete`, `http.retry`.
- `src/clible/services/translation_catalog_sync.py`: same retry policy on `_fetch_github_tree` plus `catalog.sync.retry` warnings. Retries apply only to `requests` failures so invalid API payloads raise `TranslationCatalogSyncError` once.

### 3. CLI errors (`src/clible/commands/seed.py`)

- `seed install` and `seed sync-catalog`: handle `ValueError`, `ConnectionError`, `Timeout`, `RequestException`, and unexpected errors with `log.warning` / `log.exception` where appropriate and user-facing Rich messages.

### 4. Web API (`src/clible-web/server.ts`)

- After registered API routes: `app.use("/api", …)` returns JSON `{ error: "Not found" }` for unmatched API paths (before static/SPA in production).
- Global four-argument error handler: JSON 500, structured `console.error`, skips body if `headersSent`.

### 5. Tests (`tests/conftest.py`, new service tests)

- Autouse fixture drops all structlog events during tests (`DropEvent`) for structlog 25+ compatibility.
- `tests/test_services/test_seed_download_retry.py`: `_download_xml` retry behavior (mocked `requests.get`, `time.sleep` stubbed for speed).
- `tests/test_services/test_translation_catalog_fetch_retry.py`: `_fetch_github_tree` retry plus single-shot invalid payload.

### 6. Dependencies

- Runtime: `structlog`, `tenacity` (already declared in `pyproject.toml`).

## Files added

- `pr_stories/pr-TBD-h4-error-handling-logging.md` — this PR story (paste into GitHub description).
- `tests/test_services/test_seed_download_retry.py` — unit tests for seed download retries.
- `tests/test_services/test_translation_catalog_fetch_retry.py` — unit tests for GitHub tree fetch retries.

## Files modified

- `src/clible/cli.py` — call `configure_logging` at CLI entry with env overrides.
- `src/clible/logging_config.py` — structlog processors and renderers (console vs JSON).
- `src/clible/services/seed_service.py` — `_download_xml`, retries, structlog events.
- `src/clible/services/translation_catalog_sync.py` — retries on `_fetch_github_tree`, structlog.
- `src/clible/commands/seed.py` — network and unexpected error handling for install/sync-catalog.
- `src/clible-web/server.ts` — API 404 middleware, global error handler, Express type imports.
- `tests/conftest.py` — structlog silencing fixture for pytest.

## Tests

```bash
uv run pytest -v
uv run ruff check .
uv run ruff format --check .
cd src/clible-web && npm run lint
```

Expect **287** pytest tests (or current suite size), all passing; coverage gate **≥ 80%** unchanged.

## Usage

```bash
# Developer-friendly colored logs on stderr
CLIBLE_LOG_LEVEL=DEBUG uv run clible seed install web

# One JSON object per line (suitable for log collectors)
CLIBLE_LOG_FORMAT=json CLIBLE_LOG_LEVEL=INFO uv run clible seed install web 2>&1
```

## Notes

- Sentry was explicitly out of scope for this PR.
- Repository layer remains free of logging per project architecture; services and CLI handle observability at boundaries.

## Related documentation

- `ROADMAP.md` — H4 near-term item.
- `plans/h4_error_handling_&_logging_be647519.plan.md` — implementation guide (local plan; not part of this commit if gitignored).
