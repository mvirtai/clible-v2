# Instructions to Beta Testers

## What this app is

This repository is a local version of **Clible Web**, a browser-based interface for the **Clible v2** Bible study CLI engine.

It is not just a website. This app combines:

- a React/Vite frontend for search, verse lookup, analytics, AI notes, and exports
- an Express backend (`server.ts`) that receives browser requests on `/api/*`
- the Python `clible` CLI engine as the actual data and analytics source
- SQLite-backed Bible data and translation installs managed by the CLI

The browser UI sends requests to the local server, and the server runs the `clible` CLI as a child process to fetch verses, search text, build analytics, and return results.

## How it works

1. You open the app in a browser.
2. The React frontend renders the UI and calls `/api/*` endpoints.
3. The Express server in `src/clible-web/server.ts` receives those requests.
4. The server uses the `clible` Python CLI tool to perform the real work.
5. The CLI reads from the local translation database and returns JSON back to the browser.

That means the web app is a friendly interface on top of the existing CLI engine — not a separate copy of the Bible logic.

## What you can do with the CLI part

The CLI engine supports:

- verse lookup by reference or range
- search across installed Bible translations
- analytics scoped to a verse, chapter, or book
- translation installation and listing via `clible seed`
- AI-powered tone summaries and study notes when `GEMINI_API_KEY` is provided

If you want to use the CLI directly, the command is provided by the same source tree and can be run as `clible` once the Python environment is initialized.

## How to initialize the repo

### Recommended: use `uv sync`

This repository includes `uv.lock`, so the intended Python environment manager is `uv`.

From the repository root:

```bash
uv sync
```

That will install the Python dependencies and create the locked environment for the project.

### If you do not have `uv`

Install it first. On many systems:

```bash
python -m pip install uv
```

Then run:

```bash
uv sync
```

### Then install the web dependencies

From the repository root:

```bash
task web-install
```

If you do not have `task` installed, go into `src/clible-web` and run:

```bash
cd src/clible-web
npm install
```

## Environment file convention

This repo uses a `.env` file as the primary local configuration source. The expected convention is:

- copy `.env.example` to `.env`
- set runtime values there
- do not commit `.env`

Important runtime environment variables:

- `GEMINI_API_KEY` — enables AI features such as tone analysis and study notes
- `SESSION_SECRET` — secures user sessions when the server runs

The Taskfile and Docker commands will load `.env` if it exists.

## Running the app locally

### Non-Docker local run

From `src/clible-web`:

```bash
npm run dev
```

This starts the Vite frontend and the Express API server together.

### Docker-based run (recommended for non-programmers)

From the repository root, build and run the Docker image:

```bash
docker build -f src/clible-web/Dockerfile -t clible-web-ci .

docker run --rm -p 3000:3000 -v clible-data:/home/clible/.clible-data --env-file .env clible-web-ci
```

Or use the built-in Taskfile shortcut:

```bash
task web-docker-run
```

This is often the easiest path for testers who are not developers, because Docker packages the web UI and CLI bridge together.

## What to test first

- Open the app at `http://localhost:3000`
- Try a verse lookup or search
- Click a search result and confirm the verse text and analytics appear
- Use the Analytics tab to switch between reference, chapter, and book scope
- If `GEMINI_API_KEY` is set, verify AI tone/study note behavior

## Version note

This repository currently targets **Clible v2.0.0** as the release brand.

- The root `VERSION` file shows `2.0.0-beta`
- The web UI may display `v2.0.0-WEB`
- The Python package metadata in `pyproject.toml` is version `0.2.0`, which is the package build version and is separate from the product release name

If you bump the release later, update the root `VERSION` file and any user-facing docs that refer to `2.0.0`.

## Useful Taskfile tasks

- `task web-install` — install the web dependencies
- `task web-docker-run` — build and run the web app in Docker
- `task lint` — run Python lint checks
- `task test` — run Python tests

If you are not comfortable with the command line, focus on Docker and the browser experience first.
