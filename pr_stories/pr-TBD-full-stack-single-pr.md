# feat: PR workflow docs, CLI JSON bridge, analytics metrics, web UI, and Docker

Use this as the **GitHub PR description** when the whole stack lands in **one branch / one PR** (docs, Python CLI, analytics service, clible-web, and Docker tooling together).

## Summary

### Documentation (`pr_stories/`)

- README: workflow (topic branch, approve messages and story before push, CI before merge), links to [`notes/git.md`](../notes/git.md), template and draft PR bodies.
- [`TEMPLATE_GOOD_PR_STORY.md`](TEMPLATE_GOOD_PR_STORY.md) and `pr-TBD-*` draft stories for split or combined review.

### CLI (web bridge contract)

- `clible seed list --json` — installed translations as JSON (id, name, language, format).
- `verse`, `search`, `analytics` with `--json`: print the export JSON string directly (no `json.loads` + `print`).
- `analytics.py`: stdlib `json` imported as `json_stdlib` to avoid clashing with the `--json` flag.

### Analytics

- `AnalyticService`: `character_count` and `avg_word_length` on reference/chapter/book text stats; reference tokenization aligned with verse scope via `get_verses`.
- JSON export in `src/clible/ui/export/analysis.py` updated accordingly.

### Web (`src/clible-web/`)

- Express server spawns `clible` with `--json`; optional Gemini routes when `GEMINI_API_KEY` is set (`ai.config.ts`).
- UI: only **installed** translations in the globe menu; selection persisted; multi-verse reader; AI insight and tone rendered with `react-markdown`.

### Docker and tasks

- Image built from **repository root**; Dockerfile installs the CLI from this checkout; `CLIBLE_DATA_DIR` for writable SQLite.
- `Taskfile.yml` and `.dockerignore` use root context; `src/clible-web/README.md` documents build, run, volumes, and seeding.

### Tooling

- `ruff format` applied where needed so `ruff format --check .` passes in CI.

## Files added

- `pr_stories/TEMPLATE_GOOD_PR_STORY.md` (if not already on main) and `pr_stories/pr-TBD-*.md` drafts as listed in README.
- `src/clible-web/ai.config.ts`

## Files modified (high level)

- `pr_stories/README.md`
- `src/clible/commands/seed.py`, `verse.py`, `search.py`, `analytics.py`
- `src/clible/services/analytic_service.py`, `src/clible/ui/export/analysis.py`
- `tests/test_cli/test_seed_commands.py`, `tests/test_services/test_analytic_service.py`
- `src/clible-web/`: `App.tsx`, `server.ts`, `repositories/bibleRepository.ts`, `services/bibleService.ts`, `types/bible.ts`, `vite.config.ts`, `package.json`, `package-lock.json`, `Dockerfile`, `README.md`
- `Taskfile.yml`, `.dockerignore`

## Tests

`uv run pytest -v` — **240** tests, all passing (update the number if the suite grows).

`uv run ruff check .` and `uv run ruff format --check .` — clean.

`cd src/clible-web && npm ci && npm run build` — succeeds.

Optional: `docker build -f src/clible-web/Dockerfile .` from repo root.

## Usage

```bash
# CLI JSON
uv run clible seed list --json
uv run clible verse "John 3:16" --json

# Web dev
cd src/clible-web && npm run dev

# Docker (repo root)
docker build -f src/clible-web/Dockerfile -t clible-web-ci .
docker run --rm -p 3000:3000 -v clible-data:/home/clible/.clible-data clible-web-ci
# Seed inside container, then refresh the app
```

## Notes

- Set `GEMINI_API_KEY` at runtime for AI features; never commit secrets.
- After merge, rename this file to `pr-<number>-full-stack-single-pr.md` per [`pr_stories/README.md`](README.md) naming.
