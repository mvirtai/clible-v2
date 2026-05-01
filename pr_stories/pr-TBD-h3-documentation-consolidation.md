# PR: docs: consolidate documentation (H3) — archive legacy, add ADRs, OpenAPI, guides

## Summary

This PR implements the H3 documentation consolidation milestone. It cleans up a scattered 60+ file documentation surface into a structured, navigable `docs/` hierarchy, archives all legacy and duplicate content, and adds three things the project was missing: Architecture Decision Records, an OpenAPI spec for the web API, and a single-source deployment guide.

## Purpose

- The project had two parallel documentation trees (`docs/` and `docs/internal_docs/`) with many identical files
- `PLAN.md` (816 lines, bible-api.com references) was the stated "source of truth" but was obsolete
- No documentation explained *why* key decisions were made (offline-first, layered arch, Postgres vs SQLite)
- The web API had no machine-readable spec
- The project is approaching a wider audience; public docs should present the web app as the primary interface

## Changes in This PR

### 1. Archive (commit 1)

- Moved `PLAN.md`, `BETA_DEPLOY.md`, `PR_STORY.md` → `docs/archive/`
- Moved entire `docs/internal_docs/` → `docs/archive/internal_docs/`
- Moved `pr_stories/` (30 files) → `docs/archive/pr_stories/`
- Removed duplicate `docs/` files that existed identically in `internal_docs/`: `GCP_SETUP.md`, `INTEGRATION.md`, `SEARCH_FLOW.md`, `LEARNING_PHASE_2_USER_PROFILE_AND_SETTINGS.md`
- Added `docs/archive/README.md` explaining what is archived and why

### 2. New docs structure (commit 2)

- `docs/guides/deployment.md` — consolidated from DEPLOYMENT + GCP_SETUP + BETA_DEPLOY (all providers: Cloud Run, Compute Engine, Railway, Render, Fly.io)
- `docs/guides/development.md` — local setup, workflow, architecture layers, migration and translation conventions
- `docs/guides/search.md` — FTS5 search flow (moved from `docs/SEARCH_FLOW.md`)
- `docs/architecture/overview.md` — layered architecture, data model, key patterns with ASCII diagram
- `docs/architecture/web-architecture.md` — Express bridge design, frontend layers, auth, AI proxy, JSON contract
- `docs/architecture/adr/001-offline-first-sqlite.md`
- `docs/architecture/adr/002-layered-architecture.md`
- `docs/architecture/adr/003-xml-seed-parsers.md`
- `docs/architecture/adr/004-postgres-for-user-data.md`
- `docs/api/openapi.yml` — OpenAPI 3.1 spec covering all 12 API routes (auth, settings, translations, CLI bridge, AI) with full request/response schemas and session cookie security scheme

### 3. Cross-references and README rewrite (commit 3)

- `ROADMAP.md` — new root-level roadmap replacing PLAN.md; includes current status (test coverage >91% marked done), near-term priorities (H2 perf, H4 error handling), feature roadmap, and bold ideas
- `README.md` — full rewrite: web app presented as the primary interface, architecture diagram and tech stack table for portfolio visibility, CLI docs secondary; removed deployment tutorial content (belongs in docs/guides/)
- `AGENTS.md` — updated Related Documents section; PLAN.md → ROADMAP.md; `docs/GCP_SETUP.md` → `docs/guides/deployment.md`
- `docs/PROJECT_OVERVIEW.md` — updated Related Documents and What's Next sections
- `.cursor/rules/project-context.mdc` — PLAN.md references → ROADMAP.md
- `.cursor/rules/pr-templates.md` — "Link to PLAN.md ticket" → "Link to relevant ROADMAP.md item"

## Files Changed

**Added (21):**
- `ROADMAP.md`
- `docs/archive/README.md`
- `docs/archive/PLAN.md`, `BETA_DEPLOY.md`, `PR_STORY.md`
- `docs/archive/internal_docs/` (9 files)
- `docs/archive/pr_stories/` (30 files)
- `docs/api/openapi.yml`
- `docs/architecture/overview.md`, `web-architecture.md`
- `docs/architecture/adr/001–004`
- `docs/guides/deployment.md`, `development.md`, `search.md`
- `pr_stories/pr-TBD-h3-documentation-consolidation.md`

**Modified (5):**
- `README.md` — rewritten with web-first framing
- `AGENTS.md` — updated doc references
- `docs/PROJECT_OVERVIEW.md` — updated Related Documents and backlog
- `.cursor/rules/project-context.mdc` — PLAN.md → ROADMAP.md
- `.cursor/rules/pr-templates.md` — updated PR story template link

**Deleted (20):**
- `PLAN.md`, `BETA_DEPLOY.md`, `PR_STORY.md` (from root)
- `docs/GCP_SETUP.md`, `INTEGRATION.md`, `SEARCH_FLOW.md`, `LEARNING_PHASE_2_USER_PROFILE_AND_SETTINGS.md`
- `docs/internal_docs/` (9 files and scripts)
- `pr_stories/` (30 files)

## Test Plan

- [x] No code changes — no tests needed
- [x] `uv run pytest -v` passes (unaffected by docs-only changes)
- [x] `uv run ruff check .` passes
- [x] All internal doc links verified against the new structure

## Notes

- `src/clible-web/WEB_INTEGRATION.md` and `ARCHITECTURAL_STRUCTURE.md` remain in place; they are web-layer internal docs and moving them would break any relative links within the web source tree. The new `docs/architecture/web-architecture.md` captures the same content in a more concise, maintainable form.
- `docs/CLOUD_SQL_SETUP.md`, `docs/GCLOUD_CHEATSHEET.md`, `docs/API_KEY_MANAGEMENT.md`, and `docs/SECURE_COMMIT_STRATEGY.md` are kept as-is; they are specific enough to remain standalone reference docs.
- ADR format follows the lightweight RFC style: Status, Context, Decision, Consequences.

## Related Documentation

- `ROADMAP.md` — H3 milestone
- `docs/archive/README.md` — archive contents and rationale
