# Development Guide

How to set up, run, test, and continue development on clible-v2.

---

## Quick start

```bash
cd /home/vivaldev/code/clible-v2
uv sync --all-groups
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

If tests pass and lint is clean, you are ready to continue.

---

## Daily workflow

```bash
# Install / sync dependencies (after pulling changes)
uv sync --all-groups

# Run all tests
uv run pytest -v

# Lint
uv run ruff check .

# Format check
uv run ruff format --check .

# Auto-format
uv run ruff format .

# Try the CLI
uv run clible seed install web
uv run clible verse "John 3:16"
uv run clible search "grace"
```

---

## Project structure

```
src/clible/           Python CLI
  cli.py              Entry point (Click group)
  commands/           seed, verse, search, analytics, backup
  services/           SeedService, VerseService, AnalyticService
  db/
    migrations/       Numbered SQL files (001_initial_schema.sql, …)
    repositories/     TranslationRepo, BookRepo, VerseRepo
  parsers/            CombinedParser (USFX / OSIS / Beblia / Zefania)
  data/               translations.json, bible_structure.json
  ui/                 Export formatters, display helpers

src/clible-web/       Web app
  server.ts           Express API bridge
  auth/               Session-based authentication
  user/               User settings routes
  db/                 PostgreSQL migrations and pool
  src/                React + Vite frontend

tests/                pytest test suite
  test_db/            Repository tests
  test_services/      Service tests
  test_parsers/       Parser tests
  fixtures/           Sample XML files for parser tests

docs/                 Project documentation (you are here)
infra/terraform/      GCP Workload Identity Federation setup
.github/workflows/    CI/CD pipelines
```

---

## Architecture layers

```
UI (cli.py, commands/) → Services → Repositories → SQLite
                ↕
           Parsers (XML → verse dicts)
```

**Rules:**
- UI calls services only. Never imports repos or DB directly.
- Services coordinate repos and parsers. No UI imports.
- Repositories receive a `sqlite3.Connection`, return plain dicts. No printing or network.
- Parsers read XML files and return verse dicts. No DB access.

See `AGENTS.md` and `docs/architecture/overview.md` for the full picture.

---

## Adding a migration

1. Create a new file in `src/clible/db/migrations/` with the next number: `NNN_description.sql`
2. Write idempotent SQL (e.g. `CREATE TABLE IF NOT EXISTS …`)
3. The migration runner picks it up automatically on next startup

---

## Adding a new translation

Translations are listed in `src/clible/data/translations.json`. Each entry needs:

```json
{
  "id": "short-id",
  "name": "Display Name",
  "language": "eng",
  "format": "usfx",
  "filename": "eng-example.usfx.xml",
  "url": "https://raw.githubusercontent.com/.../eng-example.usfx.xml",
  "size_mb": 1.2
}
```

After adding it: `clible seed install short-id`

Supported XML formats: USFX, OSIS, Beblia, Zefania. The `CombinedParser` detects the format automatically.

---

## Testing conventions

- Write tests alongside implementation — untested code is considered incomplete
- Use in-memory SQLite for repo and service tests: `get_connection(":memory:")`
- Mock HTTP calls — no real network in tests
- Fixtures live in `tests/conftest.py`
- Test files follow `test_<module>.py` naming

```bash
# Run a specific test file
uv run pytest tests/test_db/test_verse_repo.py -v

# Run with coverage (once pytest-cov is configured)
uv run pytest --cov=src/clible --cov-report=term-missing
```

---

## When resuming after a break

1. Read `docs/PROJECT_OVERVIEW.md` for current status and what is done
2. Read `ROADMAP.md` for what comes next
3. Check `AGENTS.md` for architecture rules before touching any layer boundaries
4. Run tests to confirm baseline is green

---

## Commands reference

| Task                    | Command                                         |
|------------------------|--------------------------------------------------|
| Install deps            | `uv sync --all-groups`                          |
| Run tests               | `uv run pytest -v`                              |
| Lint                    | `uv run ruff check .`                           |
| Format check            | `uv run ruff format --check .`                  |
| Auto-format             | `uv run ruff format .`                          |
| CLI help                | `uv run clible --help`                          |
| Seed a translation      | `uv run clible seed install web`                |
| Fetch a verse           | `uv run clible verse "John 3:16"`               |
| Search                  | `uv run clible search "grace"`                  |
| Analytics               | `uv run clible analytics reference "John 1:1"`  |
| GCS backup              | `uv run clible backup gcs`                      |
| Run web (dev)           | `cd src/clible-web && npm run dev`              |
| Build web               | `cd src/clible-web && npm run build`            |
| Run web (Docker)        | `task web-docker-run`                           |

---

## Commit conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add reading plan support
fix: correct FTS5 empty-result JSON shape
refactor: extract verse formatting to ui layer
test: add VerseRepo search edge cases
docs: update deployment guide
```

Use `git switch` for branches, `git restore` for files. See `.cursor/rules/git-commits.mdc` for the full convention.
