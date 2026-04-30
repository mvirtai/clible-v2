# Architecture and Conventions Guide

**For AI assistants:** Read this document before writing or changing code. It defines architecture, layer boundaries, and conventions. Use it when working on clible v2 for implementation, refactors, or code review.

**Project rules** are in **`.cursor/rules/`** as `.mdc` files (scoped by topic and file globs). See `.cursor/rules/how-to-use-rules.mdc` for when each rule applies and how to @-mention them.

When working on a specific PR or feature, **check the `plans/` folder** for per-PR implementation plans (step-by-step or task breakdown). Use the relevant plan if one exists for the current work.

---

## What This Project Is

clible is a **command-line Bible study tool**. The v2 rebuild is **offline-first**:

- **Data source:** Bible text comes from **seeded XML files**, not from any live API. Translations are listed in `src/clible/data/translations.json`; `clible seed install <id>` downloads XML from GitHub (e.g. [seven1m/open-bibles](https://github.com/seven1m/open-bibles), [Beblia/Holy-Bible-XML-Format](https://github.com/Beblia/Holy-Bible-XML-Format)) and parses them into SQLite.
- **No bible-api.com** — The project does not use bible-api.com or any external verse API. Ignore any legacy `api_base_url` or API client references in config/plan docs.
- **Focus:** Layered architecture, clear separation of concerns, thorough testing. See `docs/PROJECT_OVERVIEW.md` and `ROADMAP.md` for current status and direction.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ UI Layer                                                         │
│   cli.py, commands/ (seed, verse, search, analytics, backup)      │
│   Click + Rich                                                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │ calls
┌───────────────────────────────▼─────────────────────────────────┐
│ Service Layer                                                    │
│   SeedService, VerseService, AnalyticService, backup (GCS)        │
└──────────────┬──────────────────────────────┬────────────────────┘
               │ uses                         │ uses
┌──────────────▼──────────────┐  ┌────────────▼────────────────────┐
│ Repositories                 │  │ Parsers                          │
│   TranslationRepo, BookRepo, │  │   USFXParser, OSISParser,        │
│   VerseRepo                  │  │   BebliaParser (XML → verse dicts)│
└──────────────┬──────────────┘  └──────────────────────────────────┘
               │
┌──────────────▼──────────────┐
│ SQLite (clible.db)          │
│   books, translations,      │
│   verses, verses_fts (FTS5) │
└────────────────────────────┘
```

### Layer Rules

| Layer        | Can access              | Cannot access              |
|--------------|-------------------------|----------------------------|
| UI           | Services                | Repos, DB, parsers, HTTP   |
| Services     | Repos, parsers, storage | UI, Click, Rich            |
| Repositories | SQLite connection       | Services, UI, network      |
| Parsers      | File system (read XML)  | DB, UI, services internals |

Boundaries ensure each layer is testable in isolation and changes do not ripple across the codebase.

---

## Key Design Decisions

### 1. Repository pattern

Repositories are small, domain-focused classes. They receive a `sqlite3.Connection` and return plain dicts (or TypedDict). No single “god” DB class.

### 2. Dependency injection

Dependencies are passed in constructors. No singletons or global app state. Services receive repos (and parsers where needed); tests inject mocks easily.

### 3. SQL migrations

Numbered SQL files in `src/clible/db/migrations/`. The `_migrations` table records applied migrations; only unapplied ones run on startup.

### 4. Static Bible structure

Book/chapter metadata lives in `data/bible_structure.json`. No network calls to discover structure.

### 5. Services own business logic

Repositories do CRUD only. Parsers turn XML into verse dicts. All orchestration, validation, and business rules live in the service layer.

### 6. Click subcommands

Verb-noun CLI: `clible seed install web`, `clible verse "John 3:16"`, `clible search "grace"`, `clible analytics reference "John 1:1"`, `clible backup`.

---

## Naming Conventions

| Thing          | Convention              | Example                          |
|----------------|-------------------------|----------------------------------|
| Files          | snake_case              | `verse_repo.py`                  |
| Classes        | PascalCase              | `VerseService`                   |
| Functions      | snake_case              | `get_or_create`                  |
| Constants      | UPPER_SNAKE_CASE        | `API_BASE_URL`                   |
| Test files     | `test_` prefix          | `test_verse_repo.py`             |
| Test functions | `test_` prefix          | `test_search_is_case_insensitive`|
| Migrations     | `NNN_description.sql`   | `001_initial_schema.sql`         |
| Commit messages| Conventional Commits    | `feat: add verse search`         |

---

## File and Module Conventions

- One substantial class per file for repos and services.
- Utility functions can share a file (`utils.py`, `config.py`).
- `__init__.py`: empty or public API imports only. No circular imports.

---

## Error Handling

- **Repositories:** Raise on constraint violations; return `None` for “not found”.
- **Services:** Catch repo/parser errors and turn them into user-meaningful results or re-raise with context.
- **UI:** Catch service exceptions; show user-friendly messages, never raw tracebacks.

---

## Testing

- **Unit tests** for repos and services (in-memory SQLite, mocked HTTP where applicable).
- **Integration tests** for flows (e.g. seed → verse lookup, search).
- **No real HTTP** in tests — mock any requests. Fixtures in `conftest.py`.
- **Testing real-time:** Write tests alongside code, not after. Untested code is incomplete. 
- **CI**: GitHub Actions runs tests and linters on every PR. They must pass before merging. Run tests locally with `uv run pytest -v` and lint with `uv run ruff check .`, also `uv run ruff format --check .` for formatting.

---

## What NOT to Do

1. Do not import UI (e.g. `console`) in repositories or services.
2. Do not use f-strings in SQL; use parameterized queries only.
3. Do not add dependencies without justification; prefer stdlib when reasonable.
4. Do not write tests after the fact; tests accompany the implementation.
5. Do not use global mutable state or singletons.
6. Do not put business logic in the CLI; CLI calls services and renders only.
7. Do not commit failing tests.
8. Do not generate large code blocks without explanation; the developer must be able to explain the code.
9. Write a single function, class, or module without adding verbose DOCSTRINGS or comments. The code should be self-explanatory. If it’s not, refactor for clarity or add a brief comment explaining the “why” (not the “what”).
10. Leave marks of AI assistance in the codebase (e.g. “generated by GPT” comments, or code that clearly looks like it was copy-pasted from an AI without understanding). The code should look like it was written by a careful, thoughtful developer who understands every line.

---

## Quick Reference (Tooling & Commands)

| Task        | Command                    |
|-------------|----------------------------|
| Install deps| `uv sync --all-groups`     |
| Run tests   | `uv run pytest -v`         |
| Lint        | `uv run ruff check .`      |
| Format check| `uv run ruff format --check .` |
| CLI help    | `uv run clible --help`     |
| Verse       | `uv run clible verse "John 3:16"` |
| Search      | `uv run clible search "grace"`   |
| Seed install| `uv run clible seed install web` (downloads XML, then verse works) |

- **Python:** 3.12+.
- **Package manager:** uv.
- **DB:** SQLite at `src/clible/data/clible.db` by default; override with `CLIBLE_DB_PATH`.
- **Seed:** XML is fetched from GitHub during `seed install`; normal use (verse, search, analytics) is offline.
- **Backup:** Optional GCS backup; set `CLIBLE_GCS_BUCKET` (see `docs/guides/deployment.md`).
- **Git:** Use `git switch` for branches, `git restore` for files; `git checkout` is legacy (see `.cursor/rules/git-commits.mdc`). After squash and merge, delete the feature branch and use `git switch main` to return to main, `git fetch --all` to update local main and `git reset --hard origin/main` to sync with remote.

---

## Related Documents

- **docs/PROJECT_OVERVIEW.md** — Current implementation status, file map, schema.
- **ROADMAP.md** — Current status and feature direction. Replaces the legacy `PLAN.md`.
- **docs/architecture/overview.md** — Architecture layers, patterns, and decision index.
- **docs/architecture/adr/** — Architecture Decision Records for key design choices.
- **docs/api/openapi.yml** — OpenAPI 3.1 specification for the web API.
- **docs/guides/** — Development guide, deployment guide, search flow.
- **plans/** — Per-PR implementation plans (task breakdowns, step-by-step). Check when working on a feature that has a plan there. Not version-controlled (in .gitignore).
- **.cursor/rules/** — Project rules by topic (`.mdc` with frontmatter). Always-on: `project-context.mdc`, `architecture.mdc`. File-scoped: `python-style.mdc`, `database.mdc`, `testing.mdc`. See `how-to-use-rules.mdc` for usage.
