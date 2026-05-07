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
| Authentication guard | `requireAuth` middleware — session cookie required on all `/api/clible` routes |
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

Sessions are stored in PostgreSQL using `connect-pg-simple`. The session cookie is HTTP-only. Registration and login are handled by `auth/routes.ts`; the `requireAuth` middleware blocks unauthenticated requests to all `/api/clible` and AI endpoints.

Auth endpoints (`/api/auth/register`, `/login`, `/logout`, `/me`) do not require authentication.

---

## AI features

Two Gemini-backed endpoints are available to authenticated users:

- `POST /api/ai/insight` — study insight for a given verse/passage
- `POST /api/ai/tone` — tone/theme analysis

Both are rate-limited. The Gemini API key is never sent to the browser — it is read from `GEMINI_API_KEY` env var and used only server-side.

---

## JSON output contract

All CLI commands invoked via the bridge must output **a single JSON object** on stdout when `--json` is passed. If a command produces no results (e.g. zero search matches), it still emits a valid JSON object with an empty array — never plain text. This contract prevents bridge errors.

For the full shape of each command's JSON output, see the [API reference](/api/reference).

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
