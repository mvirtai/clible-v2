# Web Architecture

This document describes how the clible web UI connects to the Python CLI backend and how data flows through the system.

---

## Container design

Everything runs in a single Docker container:

```
┌─────────────────── Docker Container ─────────────────────┐
│                                                            │
│  Browser (React/Vite, built and served as static assets)  │
│               │ HTTP                                       │
│  Express server (port 3000)                               │
│    • API bridge   • Session auth   • Gemini AI proxy      │
│               │ child_process.spawn                        │
│  Clible CLI (Python)                                      │
│    • Verse lookup   • FTS5 search   • Analytics           │
│               │ sqlite3                                    │
│  SQLite — verse data (seeded with clible seed install)    │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

User authentication and settings live in a separate **PostgreSQL database** (Neon or Cloud SQL) — outside the container. The SQLite file holds only Bible text.

---

## Request flow

A typical verse lookup:

1. User enters `John 3:16` in the browser
2. `bibleRepository.getVerse()` sends `GET /api/clible?cmd=verse&args="John+3:16"+-t+web`
3. Express sanitises args, calls `child_process.spawn('clible', ['verse', 'John 3:16', '-t', 'web', '--json'])`
4. CLI queries SQLite and prints one JSON object to stdout
5. Express parses stdout and responds with `res.json(parsed)`
6. React renders the verse

If stdout is not valid JSON, Express returns 500 with `{ error, rawOutput }`. Every CLI command that the bridge invokes must emit `--json` output.

---

## Express API bridge (`server.ts`)

The bridge handles four concerns:

| Concern              | How                                                             |
|---------------------|-----------------------------------------------------------------|
| CLI dispatch         | Sanitise `cmd`/`args` params, build argv, spawn `clible`       |
| Authentication guard | `requireAuth` — session cookie required for `/api/clible`, translation endpoints, reading plans, saved searches, etc. |
| AI proxy             | Forward text to Gemini with server-side API key; never expose key to browser |
| Rate limiting        | `MAX_REQUESTS_PER_HOUR` env var caps AI endpoint calls per user |

### Supported CLI bridge commands

| Request                          | Spawned command                           |
|----------------------------------|-------------------------------------------|
| `GET /api/clible?cmd=verse`      | `clible verse <args> --json`              |
| `GET /api/clible?cmd=search`     | `clible search <args> --json`             |
| `GET /api/clible?cmd=analytics`  | `clible analytics <args> --json`          |
| `GET /api/clible?cmd=seed&args=list` | `clible seed list --json`             |

---

## Frontend layers

The React frontend follows the same layered pattern as the Python CLI:

```
App.tsx               — state, routing
  components/views/   — render data, no fetching
    services/         — business logic (e.g. build analytics args)
      repositories/   — HTTP calls to /api/* only
```

`repositories/bibleRepository.ts` is the only place that touches `fetch`. Services translate user intent into the right repository call (e.g. `"John 3"` → `clible analytics chapter "John" 3`). Components receive data as props and render it.

---

## Authentication

Sessions are stored in PostgreSQL using `connect-pg-simple`. The session cookie is HTTP-only. Registration and login are handled by `auth/routes.ts`; the `requireAuth` middleware blocks unauthenticated requests to Bible bridge routes, translation install/list, reading-plan APIs, and similar user-facing endpoints.

Auth endpoints (`/api/auth/register`, `/login`, `/logout`, `/me`) do not require authentication.

Users rows carry capability flags (PostgreSQL migration `003`): `ai_access` must be true for Gemini routes (`requireAiAccess` middleware returns 403 otherwise); `is_admin` gates `/api/admin/*`.

---

## PostgreSQL user data

Alongside `sessions`, the pool-backed schema holds:

- **`users`** — accounts (`password_hash`, `ai_access`, `is_admin`)
- **`user_settings`** — `translation_id`, `theme`, **`ui_language`** (`en` | `fi`), timestamps

Reading-plan tables (migration `004`):

- **`reading_plan_templates`** — catalog entries seeded from `src/clible-web/data/reading_plans/*.json` at startup (`seed_reading_plans.ts`)
- **`user_reading_plans`** — which template a user is following (`status`: active or abandoned; unique active row per user)
- **`reading_progress`** — completed plan days (used for progress counts and streaks)

Bible text remains in SQLite via the CLI; PostgreSQL stores identity, preferences, and plan progress only.

---

## Reading plans API

Authenticated routes under `/api/user/reading` (see `user/reading_routes.ts`):

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/plans` | List template summaries |
| `GET` | `/active` | Current active plan + today's passages + streak, or JSON `null` |
| `POST` | `/start/:planId` | Abandon prior active plan and start the given template |
| `POST` | `/complete/:dayNumber` | Mark a day complete (idempotent per day) |
| `DELETE` | `/active` | Abandon the active plan |

The React layer loads this via `ReadingPlanContext` and renders `ReadingPlanView`.

---

## AI features

Gemini-backed `POST /api/ai/*` routes are implemented in `server.ts`. Each call requires:

- an authenticated session,
- **`ai_access`** on the user row (otherwise 403),
- **`GEMINI_API_KEY`** on the server (otherwise 503 / disabled message).

They share hourly rate limiting via `MAX_REQUESTS_PER_HOUR`. The API key never reaches the browser.

| Route | Role |
|-------|------|
| `/api/ai/insight` | Study note / reflection for passage text |
| `/api/ai/tone` | Tone, mood, and theme analysis |
| `/api/ai/study` | Original-language oriented study (Hebrew/Greek source plus translation text in the payload) |
| `/api/ai/deep-dive` | Longer topical deep dive (optional structured `context`, output language `en` / `fi`) |
| `/api/ai/original-study` | Multi-translation comparison with transliteration-style original-language emphasis (verse/chapter/book scope) |

**Response shape:** successful responses are JSON with generated **`text`** and often optional **`nextFocus`** — a short suggested follow-up angle the UI can send back as `focus` on the next request (see `extractNextFocus` / prompts in `server.ts`).

For machine-readable contracts, see `docs/api/openapi.yml` (partial) and `server.ts` for every field.

---

## JSON output contract

All CLI commands invoked via the bridge must output **a single JSON object** on stdout when `--json` is passed. If a command produces no results (e.g. zero search matches), it still emits a valid JSON object with an empty array — never plain text. This contract prevents bridge errors.

For the full shape of each command's JSON output, see the OpenAPI spec at `docs/api/openapi.yml`.

---

## Local development

```bash
# Run CLI directly
uv run clible verse "John 3:16"

# Run web (with Vite dev server + Express)
cd src/clible-web
npm install
npm run dev          # Vite proxy forwards /api/* to Express on :3001

# Run as Docker (production mode)
task web-docker-build
task web-docker-run PORT=3000
```

Environment variables needed locally: `GEMINI_API_KEY`, `SESSION_SECRET`, `DATABASE_URL`. Copy `.env.example` to `.env` and fill in the values.
