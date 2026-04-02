# feat: Web bridge, installed translations, and Docker from repo root

This PR adds an Express-based **clible-web** server that spawns the `clible` CLI with `--json`, lists **installed** translations from the host environment, renders AI insight/tone output as **Markdown**, and ships a **Docker** image built from the **repository root** so the image installs the CLI from the current checkout. Requires a prior merge (or rebase) of the Python PR that implements `seed list --json` and stable `--json` stdout.

## Summary

- **Server:** Bridge routes call `clible` via `spawn` with `--json` for verse, search, analytics, and `seed list`; optional Gemini routes when `GEMINI_API_KEY` is set.
- **Config:** Central prompts and model IDs in `ai.config.ts`.
- **UI:** Globe menu shows only installed translations; persist selection in `localStorage`; block search/analytics until a translation is chosen; reader supports multi-verse display; AI insight and tone use `react-markdown` with styled components.
- **Deps:** Add `react-markdown` (and lockfile updates).
- **Docker:** Build context = repo root; `Dockerfile` copies `pyproject.toml` + `src/clible` and `pip install`s the package; `CLIBLE_DATA_DIR` for writable SQLite; `Taskfile.yml` / `.dockerignore` / `src/clible-web/README.md` document build, run, and volume for data persistence.

## Files added

- `src/clible-web/ai.config.ts` — Gemini models and prompt builders.

## Files modified

- `src/clible-web/server.ts`, `repositories/bibleRepository.ts`, `services/bibleService.ts`, `types/bible.ts`, `vite.config.ts`, `App.tsx`
- `src/clible-web/package.json`, `package-lock.json`
- `src/clible-web/Dockerfile`, `src/clible-web/README.md`
- `Taskfile.yml`, `.dockerignore`

## Tests

Python tests are unchanged by this PR unless CI runs repo-wide checks.

**Local / CI for this PR:**

- `cd src/clible-web && npm ci && npm run build`
- `uv run ruff check .` and `uv run ruff format --check .` at repo root
- Optional: `docker build -f src/clible-web/Dockerfile -t clible-web-ci .` from repo root

Update **N** for full suite: `uv run pytest -v` — **N tests**, all passing (after Python PR is on `main` or merged into this branch).

## Usage

```bash
# Local web (after npm install in src/clible-web)
cd src/clible-web && npm run dev

# Docker (repo root)
docker build -f src/clible-web/Dockerfile -t clible-web-ci .
docker run --rm -p 3000:3000 -v clible-data:/home/clible/.clible-data clible-web-ci
# Then seed inside container: docker exec … clible seed install web
```

## Notes

- **Security:** Do not commit `GEMINI_API_KEY`; pass at runtime for AI features.
- Merge the **Python CLI + analytics** PR first, or rebase this branch onto `main` after it lands.

## Combining with other PRs

- **Web + Docker** are intentionally one story: same runtime path (CLI in image + UI). Do not split Docker to a fourth PR unless you have a strong reason.
