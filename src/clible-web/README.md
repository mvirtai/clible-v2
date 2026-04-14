<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Clible Web

A modern, offline-first React web interface for the [Clible v2](../../README.md) Bible study CLI tool. Verse lookup, FTS5 full-text search, multi-scope text analytics, AI-powered insights, and multi-user support — all served from a single Docker container alongside the Python CLI engine.

## Features

- **Verse Lookup** — fetch a single verse, a verse range, or a full chapter/book by reference
- **FTS5 Search** — full-text search powered by SQLite FTS5; click any result to inspect the verse
- **Text Analytics** — three analysis scopes per verse:
  - **Reference** — stats for the exact verse/range
  - **Chapter** — stats for the verse's entire chapter
  - **Book** — stats for the verse's entire book
- **AI Tone Analysis** — Gemini-powered tone & style summary (optional, requires `GEMINI_API_KEY`)
- **AI Study Notes** — contextual exegesis per verse (Reader view)
- **Export** — download results in CSV, HTML, JSON, Markdown, TXT, or XML
- **User Auth** — JWT-based login; per-user settings (translation preference, theme)
- **Translation management** — globe menu lists installed translations; install more with `clible seed install <id>`

## Run Locally

**Prerequisites:** Node.js 20+, `clible` CLI installed and at least one translation seeded (`clible seed install web`).

```bash
npm install
cp .env.example .env          # set GEMINI_API_KEY if you want AI features
npm run dev                   # Vite + Express on http://localhost:5173 / :3000
```

## Docker

Build from the **repository root** so the image installs the `clible` CLI from this checkout (not only the version baked into the base image):

```bash
docker build -f src/clible-web/Dockerfile -t clible-web-ci .
```

Or: `task web-docker-build` / `task web-docker-run` (same build).

The image sets `CLIBLE_DATA_DIR=/home/clible/.clible-data` so the SQLite DB is writable (the install-time default under `site-packages` is read-only). Persist data across runs:

```bash
docker run --rm -p 3000:3000 -v clible-data:/home/clible/.clible-data clible-web-ci
```

Seed a translation inside the container (e.g. `docker exec ... clible seed install web`) before using verse search.

### Translations in the web UI

The globe menu lists only **installed** translations (`clible seed list`), loaded via the API bridge (`clible seed list --json`). There is no default selection until you pick one. Install translations with `clible seed install <id>` (or `docker exec` into the container), then refresh the page.

- **Security**: `GEMINI_API_KEY` must be provided at **runtime** only. It is never bundled into the browser client.
- **Run with AI enabled**:

```bash
docker run --rm -p 3000:3000 -e GEMINI_API_KEY="YOUR_KEY" <your-image>
```

- **Run without AI** (default): omit `GEMINI_API_KEY`. The app will still work, but AI features return a friendly error.

#### If you see `API key not valid` (400)

The server is receiving *some* key, but Google rejects it. Check:

1. **Use a current key** from [Google AI Studio](https://aistudio.google.com/apikey) (or Cloud Console with **Generative Language API** enabled for that key).
2. **`.env` format**: use `GEMINI_API_KEY=AIza...` on one line, no spaces around `=`. Avoid pasting the placeholder `MY_GEMINI_API_KEY`.
3. **Cloud API key restrictions**: if the key is restricted to **HTTP referrers** or **IP addresses**, server-side calls from Docker will fail. For local testing, use **None** or restrict by API only (allow Generative Language API).

## Analytics Scopes

After fetching a verse (or clicking a search result), switch to the **Analytics** tab. Use the scope buttons to change what text is analysed:

| Scope | What is analysed | CLI equivalent |
|---|---|---|
| **Reference** | The fetched verse/range | `clible analytics reference "John 3:16"` |
| **Chapter** | The verse's entire chapter | `clible analytics chapter John 3` |
| **Book** | The verse's entire book | `clible analytics book John` |

Metrics are fetched from the CLI engine via the Express API bridge — no JavaScript re-computation.

## Architecture

```
Browser (React/Vite)
  └─▶ /api/*   Express (server.ts)  ──┐
                                      │ child_process → clible CLI
                                      │                 (Python / SQLite / FTS5)
                                      └──────────────────────────────────────────
```

Frontend layers (TypeScript):

| Layer | Path | Responsibility |
|---|---|---|
| Types | `types/` | Shared data shapes (`BibleResponse`, `TextStats`, …) |
| Repository | `repositories/` | HTTP calls to `/api/*` |
| Service | `services/` | Business logic, AI integration, analytics arg-building |
| UI | `App.tsx`, `components/`, `views/` | Render only; no fetch calls |

See [INTEGRATION.md](./INTEGRATION.md) for a deeper dive into the bridge architecture.
