# PR: feat(web): reading plans, daily progress, streak, and localized UI

## Summary

This PR adds a signed-in **reading plan** feature to the web app: PostgreSQL tables store catalog templates and per-user active plans plus daily completion rows; Express exposes authenticated REST endpoints to list templates, start or abandon a plan, mark a day complete, and return streak metadata. The React shell gains a **Reading** view with plan cards, progress, today’s passages (book/chapter ranges), and a flame **streak** badge in the header. Static Finnish strings and plan titles/descriptions for the three seeded plans are routed through `i18n.ts`, and **`COOKIE_SECURE`** is made configurable so the production Docker image can set session cookies over plain HTTP during local `task web-docker-run` (required because `NODE_ENV=production` would otherwise mark cookies `Secure` only).

## Purpose

- Give returning users a lightweight habit loop (plan + completion + streak) aligned with the roadmap’s reading-plan direction.
- Keep catalog text in English in the database while the UI can show Finnish when **Interface language** is Suomi.
- Fix local Docker testing where sessions never persisted because browsers do not send `Secure` cookies on `http://localhost`.

## Changes in This PR

### 1. Database model and seed data (`004_reading_plans.sql`, `seed_reading_plans.ts`, `data/reading_plans/*.json`)

Migration **004** introduces `reading_plan_templates` (JSONB `entries` per day), `user_reading_plans` (one active plan per user via partial unique index), and `reading_progress` (completed `day_number` rows with timestamps). The seed script reads JSON definitions from `data/reading_plans/`; smaller plans embed full `entries` arrays, while **annual** uses a `generator` (`sequentialChapters` over the full Bible) expanded at seed time so the repo stays small. Templates are upserted on server startup after migrations.

### 2. REST API and streak logic (`reading_routes.ts`, `reading_routes.test.ts`)

`readingRouter` mounts under `/api/user/reading` behind `requireAuth`. Handlers list templates, fetch or start the active plan, record day completion, and delete the active plan. **Streak** counts consecutive calendar days (UTC) with completion, allowing “today not yet done” by anchoring from yesterday when today is incomplete. Pure date math lives in `computeStreakFromCompletionDates`, covered by Vitest.

### 3. Server wiring and session cookies (`server.ts`, `Taskfile.yml`)

After migrations, `seedReadingPlanTemplates()` runs. The Express session `cookie.secure` flag follows **`COOKIE_SECURE`** when set (`true`/`false`), otherwise defaults to the prior production behavior (secure in production). **`task web-docker-run`** and **`web-docker-debug`** pass **`COOKIE_SECURE=false`** so the same image works on local HTTP.

### 4. Frontend state and UI (`ReadingPlanContext.tsx`, `ReadingPlanView.tsx`, `StreakBadge.tsx`, `App.tsx`, `main.tsx`)

`ReadingPlanProvider` wraps the app; the Reading tab loads plans and active state, starts or abandons plans, and marks days complete via `fetch` with credentials. `ReadingPlanView` shows either the catalog or the active plan with progress bar and today’s passages (USFX-style `bookId` labels until book-name mapping is added). `StreakBadge` shows the streak count next to the Reading control when the count is positive.

### 5. i18n (`i18n.ts`)

New keys cover Reading navigation, labels, buttons, streak aria text, and **per–plan-id** titles and descriptions via `localizedReadingPlanCopy` for `30day-psalms`, `90day-nt`, and `annual`; unknown plan ids still use API `name`/`description`.

## Files added

- `src/clible-web/db/migrations/004_reading_plans.sql` — templates, user plans, progress tables and indexes.
- `src/clible-web/db/seed_reading_plans.ts` — load JSON / generator plans and upsert templates.
- `src/clible-web/data/reading_plans/30day-psalms.json` — 30-day Psalms schedule.
- `src/clible-web/data/reading_plans/90day-nt.json` — 90-day New Testament schedule.
- `src/clible-web/data/reading_plans/annual.json` — yearly plan metadata + `sequentialChapters` generator.
- `src/clible-web/types/reading.ts` — shared TypeScript shapes for plans and API responses.
- `src/clible-web/user/reading_routes.ts` — Express router for reading plan CRUD and streak payload.
- `src/clible-web/user/reading_routes.test.ts` — unit tests for streak calculation.
- `src/clible-web/user/ReadingPlanContext.tsx` — client state and API calls.
- `src/clible-web/components/ReadingPlanView.tsx` — catalog and active-plan panels.
- `src/clible-web/components/StreakBadge.tsx` — header streak chip.
- `pr_stories/pr-TBD-reading-plans-streak.md` — this PR story.

## Files modified

- `Taskfile.yml` — `COOKIE_SECURE=false` for local Docker web tasks.
- `src/clible-web/server.ts` — seed hook, `/api/user/reading` mount, `COOKIE_SECURE` session handling.
- `src/clible-web/App.tsx` — Reading `viewMode`, nav tab with streak badge, `ReadingPlanProvider`.
- `src/clible-web/main.tsx` — wraps the tree with `ReadingPlanProvider`.
- `src/clible-web/utils/i18n.ts` — Reading strings, plan copy helper, EN/FI entries.

## Tests

```bash
uv run pytest -v
uv run ruff check .
uv run ruff format --check .
cd src/clible-web && npm run lint
cd src/clible-web && npm run test
```

**345** pytest tests passed; coverage **94.36%** (gate ≥ 80%). **50** Vitest tests passed (`npm run test` / `vitest run`). TypeScript: `tsc --noEmit` clean.

## Usage

```bash
# Full repo checks (Python + web unit tests)
task test

# Local web stack with Postgres env (see Taskfile); session works on http://localhost with COOKIE_SECURE=false
task web-docker-run
```

In the web UI (signed in): open **Lukeminen / Reading**, choose a plan, then **Merkitse tehdyksi** when done for the day; the header shows a streak after consecutive days.

## Notes

- Passage lines still show canonical **book IDs** (e.g. `PSA 1`); mapping to localized book names is out of scope here and can reuse `bookNames` later.
- Only the three seeded template ids have Finnish title/description overrides; new templates fall back to DB text until added to `localizedReadingPlanCopy`.
- Merge is left to the maintainer; branch: `feat/add-reading-pland-and-start-tracking-user-progress` (rename optional before opening PR).

## Related documentation

- `ROADMAP.md` — reading plans / engagement direction.
- `.cursor/rules/pr-stories.mdc` — PR description structure.
