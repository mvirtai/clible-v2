# clible v2 — Development Plan

A complete rebuild of clible, a CLI Bible study tool. This plan is structured as
phases with concrete tickets. Each ticket is a self-contained unit of work with
clear acceptance criteria and learning goals.

**Approach:** Build bottom-up. Data layer first, then services, then UI. Write
tests alongside each layer, not as an afterthought.

**Rules:**

- Do not skip phases. Each phase builds on the previous one.
- Every ticket must have passing tests before moving to the next.
- Commit after each completed ticket. Small, meaningful commits.
- If something feels wrong, stop and refactor before adding more.

---

## Phase 0 — Project Foundation

Set up the project skeleton, tooling, and conventions before writing any
application code. A solid foundation prevents rework later.

### Ticket 0.1: Project structure and configuration

Create the directory layout and configure the project.

```
clible-v2/
├── src/
│   └── clible/
│       ├── __init__.py
│       ├── config.py          # Centralized configuration
│       ├── db/
│       │   ├── __init__.py
│       │   ├── connection.py  # DB connection management
│       │   ├── migrations/    # Numbered SQL migration files
│       │   └── repositories/  # Data access classes
│       ├── api/
│       │   ├── __init__.py
│       │   └── client.py      # HTTP client for bible-api.com
│       ├── services/
│       │   └── __init__.py    # Business logic layer
│       └── ui/
│           └── __init__.py    # Presentation layer
├── tests/
│   ├── conftest.py
│   ├── test_db/
│   ├── test_api/
│   ├── test_services/
│   └── test_ui/
├── data/
│   └── stop_words.json
├── pyproject.toml
├── .cursorrules
├── PLAN.md

├── SKILLS.md
├── AGENTS.md
└── README.md
```

**Acceptance criteria:**

- [ ] `src/clible/` package layout created
- [ ] `pyproject.toml` configured with proper metadata, entry point, and
      dependency groups (runtime, dev, test)
- [ ] `uv sync` installs cleanly
- [ ] `uv run pytest` runs (even if zero tests)

**Learning goals:**

- `src/` layout vs flat layout — why `src/` prevents accidental imports
- `pyproject.toml` dependency groups (`[project.dependencies]` vs
  `[project.optional-dependencies]`)

---

### Ticket 0.2: Configuration module

Create `src/clible/config.py` — a single source of truth for all configurable
values.

**What to put here:**

- `DB_PATH` — path to SQLite database (with sensible default)
- `API_BASE_URL` — bible-api.com base URL
- `TRANSLATIONS` — list of supported translation codes and names
- `DATA_DIR` — path to data directory (exports, stop words)
- `REQUEST_TIMEOUT` — HTTP timeout in seconds
- `REQUEST_DELAY` — delay between API calls (rate limiting)

**Acceptance criteria:**

- [ ] All magic strings and paths from v1 are replaced by config values
- [ ] Config values can be overridden via environment variables (use
      `os.environ.get()` with defaults)
- [ ] One test verifying default config loads correctly

**Learning goals:**

- Configuration management patterns
- Environment variable overrides for different environments (dev, test, docker)

---

### Ticket 0.3: Linting and formatting setup

Add `ruff` for linting and formatting.

**Acceptance criteria:**

- [ ] `ruff` added to dev dependencies
- [ ] `[tool.ruff]` section in `pyproject.toml`
- [ ] All existing code passes `ruff check` and `ruff format --check`

**Learning goals:**

- Why linting matters for professional projects
- Ruff rules and configuration

---

## Phase 1 — Database Layer

Build the data persistence layer from scratch. This is the foundation everything
else depends on.

**Key design decision:** Use the Repository pattern. Instead of one massive
`QueryDB` class with 40+ methods, create focused repository classes:

- `TranslationRepo` — translations table
- `BookRepo` — books table
- `VerseRepo` — queries + verses tables
- `SessionRepo` — sessions + session_queries tables
- `AnalysisRepo` — analysis_history + analysis_results tables
- `CacheRepo` — chapter/verse cache tables

Each repository receives a `sqlite3.Connection` and operates on its own
domain. No repository prints to the console — they return data only.

---

### Ticket 1.1: Database connection and migration system

Create a connection manager and a simple migration runner.

**Migration system design:**

```
src/clible/db/migrations/
├── 001_initial_schema.sql
├── 002_add_cache_tables.sql
└── ...
```

A `migrations` table in SQLite tracks which migrations have been applied.
On startup, the system runs any unapplied migrations in order.

**Acceptance criteria:**

- [ ] `get_connection(db_path)` function returns a configured connection
      (WAL mode, foreign keys ON, row_factory set)
- [ ] `run_migrations(conn)` applies unapplied `.sql` files in order
- [ ] Migration state tracked in a `_migrations` table
- [ ] Tests: fresh DB gets all migrations, already-migrated DB skips them

**Learning goals:**

- SQLite WAL mode and why it matters
- Database migration concepts (schema evolution over time)
- Why `CREATE TABLE IF NOT EXISTS` on every startup is fragile

---

### Ticket 1.2: Initial schema migration (001)

Write `001_initial_schema.sql` containing the core tables.

**Tables:**

- `translations` (id, abbreviation, name, note)
- `books` (id, name)
- `users` (id, name, created_at)

Keep it minimal. Add tables in later migrations as needed.

**Acceptance criteria:**

- [ ] Migration file creates tables with proper types and constraints
- [ ] UUIDs used for primary keys (generated in application layer)
- [ ] Tests verify table creation and constraints

**Learning goals:**

- SQL DDL (CREATE TABLE, constraints, PRIMARY KEY, NOT NULL)
- Schema design decisions (when to normalize vs. denormalize)

---

### Ticket 1.3: Query and verse schema migration (002)

Write `002_query_verse_tables.sql`.

**Tables:**

- `queries` (id, reference, translation_id FK, created_at)
- `verses` (id, query_id FK, book_id FK, chapter, verse, text)

**Acceptance criteria:**

- [ ] Foreign keys reference correct parent tables
- [ ] Indexes on frequently queried columns (query_id in verses)
- [ ] Tests verify FK constraints work (inserting verse without query fails)

**Learning goals:**

- Foreign keys in SQLite (and why `PRAGMA foreign_keys = ON` is needed)
- Indexing strategy basics

---

### Ticket 1.4: Session schema migration (003)

Write `003_session_tables.sql`.

**Tables:**

- `sessions` (id, user_id FK, name, scope, is_saved, created_at)
- `session_queries` (session_id FK, query_id FK — composite PK)

**Acceptance criteria:**

- [ ] Junction table with composite primary key
- [ ] Cascading behavior defined (what happens when session is deleted?)
- [ ] Tests for session CRUD through repository

**Learning goals:**

- Many-to-many relationships via junction tables
- CASCADE vs RESTRICT delete behavior

---

### Ticket 1.5: Translation repository

Create `TranslationRepo` with methods:

- `get_or_create(abbreviation, name, note) -> str` (returns ID)
- `get_by_abbreviation(abbr) -> dict | None`
- `list_all() -> list[dict]`

**Acceptance criteria:**

- [ ] Pure data access — no prints, no logging side effects
- [ ] Returns plain dicts (not sqlite3.Row)
- [ ] Full test coverage with in-memory SQLite

**Learning goals:**

- Repository pattern — why separating data access from business logic matters
- Testing with in-memory SQLite databases

---

### Ticket 1.6: Book repository

Create `BookRepo`:

- `get_or_create(name) -> str`
- `list_all() -> list[str]`
- `get_distribution() -> list[tuple[str, int]]`

**Acceptance criteria:**

- [ ] Same patterns as TranslationRepo
- [ ] Full test coverage

---

### Ticket 1.7: Verse repository

Create `VerseRepo`:

- `save_query(verse_data: dict) -> str` (returns query ID)
- `get_query(query_id) -> dict | None`
- `list_queries() -> list[dict]`
- `search_word(word) -> list[dict]`
- `get_verses_by_book(book_name) -> list[dict]`
- `get_verses_by_query_ids(ids) -> list[dict]`

This is the core repository — take time to get it right.

**Acceptance criteria:**

- [ ] `save_query` handles translation lookup/creation via TranslationRepo
- [ ] Word search is case-insensitive
- [ ] Tests cover saving, retrieving, listing, and searching

**Learning goals:**

- Composing repositories (VerseRepo uses TranslationRepo and BookRepo)
- SQL LIKE patterns for text search
- Transaction management (save_query inserts into multiple tables)

---

### Ticket 1.8: Session repository

Create `SessionRepo`:

- `create(user_id, name, scope, is_temporary) -> str`
- `get(session_id) -> dict | None`
- `list_for_user(user_id) -> list[dict]`
- `add_query(session_id, query_id)`
- `get_session_verses(session_id) -> list[dict]`
- `delete(session_id) -> bool`
- `save(session_id)` (mark as permanent)

**Acceptance criteria:**

- [ ] All CRUD operations tested
- [ ] Delete cascades properly to junction table
- [ ] User ownership verified in tests

---

### Ticket 1.9: Cache repository

Create `CacheRepo`:

- `get_max_chapter(book, translation) -> int | None`
- `set_max_chapter(book, translation, value)`
- `get_max_verse(book, chapter, translation) -> int | None`
- `set_max_verse(book, chapter, translation, value)`

Also add `004_cache_tables.sql` migration.

**Acceptance criteria:**

- [ ] INSERT OR REPLACE used for upserts
- [ ] Tests verify cache hit and cache miss scenarios

**Learning goals:**

- Caching patterns at the database level
- SQL UPSERT (INSERT OR REPLACE / ON CONFLICT)

---

## Phase 2 — API Client

Build a clean, focused HTTP client that only does one thing: talk to
bible-api.com.

---

### Ticket 2.1: Bible API client

Create `src/clible/api/client.py` with a `BibleClient` class:

- `fetch_verse(book, chapter, verses, translation) -> dict`
- `fetch_chapter(book, chapter, translation) -> dict`
- `fetch_random(translation) -> dict`
- `fetch_book_list() -> list[dict]`

**Design rules:**

- No caching logic — that belongs in the service layer
- No database access
- Rate limiting via `time.sleep()` between requests
- All errors return `None` or raise typed exceptions (not silent failures)
- Timeout from config

**Acceptance criteria:**

- [ ] Clean HTTP client with no side effects beyond network calls
- [ ] Custom exception classes (`APIError`, `APITimeout`, `APINotFound`)
- [ ] Tests with mocked `requests` (no real HTTP calls in tests)
- [ ] Response data normalized to a consistent dict shape

**Learning goals:**

- HTTP client design (separation from business logic)
- Mocking HTTP calls with `pytest-mock` or `responses` library
- Custom exception hierarchies

---

### Ticket 2.2: Static book/chapter/verse metadata

Instead of brute-forcing max chapter counts from the API (up to 150 requests
per book!), ship a static JSON file with known Bible structure.

Create `data/bible_structure.json`:

```json
{
  "Genesis": {"chapters": 50, "verses": [31, 25, 24, ...]},
  "Exodus": {"chapters": 40, "verses": [22, 25, 22, ...]},
  ...
}
```

This data is public knowledge and doesn't change. Fetch it once from a
reference source and save it.

**Acceptance criteria:**

- [ ] JSON file with all 66 books, chapter counts, and verse counts per chapter
- [ ] Utility function to load and query this data
- [ ] Tests verify structure completeness
- [ ] `calculate_max_chapter` and `calculate_max_verse` become simple lookups

**Learning goals:**

- When static data is better than dynamic API calls
- Trading disk space for performance and reliability

---

## Phase 3 — Service Layer

Business logic lives here. Services coordinate between repositories, the API
client, and each other. The UI layer only talks to services.

---

### Ticket 3.1: Verse service

Create `VerseService`:

- `fetch_and_save(book, chapter, verses, translation) -> dict`
  - Check DB cache first (via VerseRepo)
  - Fall back to API client
  - Save to DB after successful fetch
- `get_saved_queries() -> list[dict]`
- `search(word) -> list[dict]`

**Acceptance criteria:**

- [ ] Cache-first fetch logic with API fallback
- [ ] Service receives repo and client as constructor arguments (dependency
      injection — no global singletons)
- [ ] Tests verify cache hit skips API, cache miss calls API

**Learning goals:**

- Service layer pattern
- Dependency injection (passing dependencies, not importing globals)
- Cache-aside pattern

---

### Ticket 3.2: Session service

Create `SessionService`:

- `start(user_id, name, scope) -> str`
- `resume(session_id, user_id) -> bool`
- `end(session_id)`
- `save(session_id)`
- `delete(session_id, user_id) -> bool`
- `list_for_user(user_id) -> list[dict]`
- `get_session_verses(session_id) -> list[dict]`

**Design:** Receives `SessionRepo` via constructor. No singleton state.
User ownership checks happen here.

**Acceptance criteria:**

- [ ] All operations validated (user owns session, session exists, etc.)
- [ ] No global state — context passed explicitly
- [ ] Tests cover happy path and error cases (wrong user, missing session)

**Learning goals:**

- Authorization checks at the service layer
- Explicit state vs. global singletons

---

### Ticket 3.3: Analytics service

Create `AnalyticsService`:

- `word_frequency(verses, top_n) -> list[tuple[str, int]]`
- `bigrams(verses, top_n) -> list[tuple[str, int]]`
- `trigrams(verses, top_n) -> list[tuple[str, int]]`
- `vocabulary_stats(verses) -> dict`

**Design:** Pure functions that operate on lists of verse dicts. No database
access, no side effects. Load stop words from config path.

**Acceptance criteria:**

- [ ] Stop word filtering works
- [ ] Pure functions — easy to test with hardcoded input
- [ ] Results sorted by frequency descending

**Learning goals:**

- Pure functions vs. stateful methods
- Text processing basics (tokenization, n-grams)

---

### Ticket 3.4: Translation comparison service

Create comparison logic:

- `compare_translations(book, chapter, verses, trans_a, trans_b) -> dict`
  - Fetches both translations (using VerseService for cache-first logic)
  - Returns aligned verse pairs

**Acceptance criteria:**

- [ ] Handles cases where verse counts differ between translations
- [ ] Tests with mocked verse data

---

### Ticket 3.5: Export service

Create `ExportService`:

- `to_markdown(verses, reference, translation) -> str`
- `to_text(verses, reference, translation) -> str`
- `save_to_file(content, filename, format) -> Path`

**Design:** Returns strings. File I/O is a separate step. This makes testing
trivial.

**Acceptance criteria:**

- [ ] Markdown output is well-formatted
- [ ] File saving uses config DATA_DIR
- [ ] Tests verify output format without touching filesystem

---

## Phase 4 — User Interface

Build the presentation layer. This is the last layer — everything it needs
already exists in the service layer.

**Decision point:** Choose between:

- **Option A: Textual TUI** — Full interactive app (like cmdboard). Richer UX,
  keyboard-driven, panels and screens.
- **Option B: Click + Rich** — Traditional CLI with subcommands. Simpler, more
  composable, pipe-friendly.

Recommendation: Start with **Option B** (Click + Rich) for the core CLI, then
optionally add a Textual dashboard mode later. This gives you a working tool
faster and teaches CLI design fundamentals.

---

### Ticket 4.1: CLI entry point and basic structure

Set up Click-based CLI with command groups:

```
clible fetch verse "John 3:16" --translation web
clible fetch chapter "John 3" --translation kjv
clible fetch random
clible search "grace"
clible sessions list
clible sessions start "Evening study"
clible export markdown --query-id abc123
```

**Acceptance criteria:**

- [ ] `clible --help` shows all command groups
- [ ] Entry point configured in `pyproject.toml`
- [ ] Commands are stubs that print placeholder messages

**Learning goals:**

- Click command groups and subcommands
- CLI UX design (verb-noun pattern)

---

### Ticket 4.2: Rich output formatting

Create `src/clible/ui/display.py` with rendering functions:

- `render_verses(data)` — formatted verse panel
- `render_query_list(queries)` — table of saved queries
- `render_search_results(results, word)` — highlighted search results
- `render_frequency(results)` — word frequency table
- `render_comparison(data)` — side-by-side translation table

**Design rule:** Display functions take data and return Rich renderables.
They do not fetch data or manage state. Print happens at the CLI layer.

**Acceptance criteria:**

- [ ] Each function produces a Rich Panel, Table, or Group
- [ ] No data fetching inside display functions
- [ ] Visual output reviewed manually for readability

---

### Ticket 4.3: Wire up fetch commands

Connect `clible fetch` commands to VerseService and display functions.

**Acceptance criteria:**

- [ ] `clible fetch verse "John 3:16"` fetches and displays
- [ ] `clible fetch chapter "John 3"` works
- [ ] `clible fetch random` works
- [ ] `--translation` flag changes translation
- [ ] Errors show user-friendly messages (not tracebacks)

---

### Ticket 4.4: Wire up search and analytics commands

Connect search, word frequency, phrase analysis commands.

**Acceptance criteria:**

- [ ] `clible search "word"` searches and displays with highlighting
- [ ] `clible analytics frequency` shows word frequency
- [ ] `clible analytics phrases` shows bigrams and trigrams

---

### Ticket 4.5: Wire up session commands

Connect session management commands.

**Acceptance criteria:**

- [ ] `clible sessions start "name"` creates and reports
- [ ] `clible sessions list` shows all sessions
- [ ] `clible sessions resume <id>` resumes session
- [ ] Session context persists across commands (consider a state file)

---

### Ticket 4.6: Wire up export commands

Connect export functionality.

**Acceptance criteria:**

- [ ] `clible export markdown` exports saved verses
- [ ] `clible export text` exports as plain text
- [ ] Output path printed after export

---

### Ticket 4.7: Interactive mode (optional enhancement)

Add a `clible interactive` command that launches a menu-driven loop (like v1)
using Rich prompts instead of raw `input()`.

**Acceptance criteria:**

- [ ] Menu loop with rich-formatted menus
- [ ] All features accessible from interactive mode
- [ ] `q` or `Ctrl+C` exits cleanly

---

## Phase 5 — Testing and Quality

Ensure the project is solid and presentable.

---

### Ticket 5.1: Integration tests

Write end-to-end tests that exercise full workflows:

- Fetch → Save → Search → Export
- Create session → Add queries → List → Delete

**Acceptance criteria:**

- [ ] At least 5 integration tests covering main workflows
- [ ] Use in-memory SQLite and mocked HTTP
- [ ] Tests document expected behavior

---

### Ticket 5.2: Test coverage check

Add `pytest-cov` and measure coverage.

**Acceptance criteria:**

- [ ] Coverage report in CI output
- [ ] Core modules (db, services) above 80% coverage
- [ ] Untested code identified and documented

---

### Ticket 5.3: Error handling audit

Review all error paths:

- API failures (timeout, 404, 500, no connection)
- Invalid user input (bad references, empty strings)
- Database errors (locked, corrupt)

**Acceptance criteria:**

- [ ] No unhandled exceptions reach the user
- [ ] Errors show helpful messages
- [ ] Tests for key error scenarios

---

## Phase 6 — DevOps and Packaging

Make the project deployable and maintainable.

---

### Ticket 6.1: Dockerfile

Multi-stage Docker build:

- Builder stage: install deps, run tests
- Runtime stage: minimal image with just the app

**Acceptance criteria:**

- [ ] `docker build` succeeds and runs tests
- [ ] `docker run` starts clible
- [ ] Database persists via volume mount

---

### Ticket 6.2: GitHub Actions CI

Basic CI pipeline:

- On push/PR: lint (ruff), test (pytest), build (docker)

**Acceptance criteria:**

- [ ] CI runs on every push to main and on PRs
- [ ] Failures block merge
- [ ] Badge in README

---

### Ticket 6.3: README

Write a clean, professional README:

- What it is (1 paragraph)
- Screenshot or demo
- Installation
- Usage examples
- Architecture overview (1 diagram or description)
- Contributing

**Acceptance criteria:**

- [ ] README is concise, not bloated
- [ ] Installation instructions work from scratch
- [ ] No mention of AI tools

---

## Phase Summary

| Phase | Tickets | Focus                | Key Learning                        |
| ----- | ------- | -------------------- | ----------------------------------- |
| 0     | 0.1–0.3 | Project setup        | Project structure, config, tooling  |
| 1     | 1.1–1.9 | Database layer       | SQL, migrations, repository pattern |
| 2     | 2.1–2.2 | API client           | HTTP clients, mocking, exceptions   |
| 3     | 3.1–3.5 | Service layer        | Business logic, DI, pure functions  |
| 4     | 4.1–4.7 | User interface       | CLI design, Rich rendering          |
| 5     | 5.1–5.3 | Testing and quality  | Integration tests, coverage, errors |
| 6     | 6.1–6.3 | DevOps and packaging | Docker, CI/CD, documentation        |

**Estimated effort:** 25–30 tickets across 6 phases. At a steady pace of
1–2 tickets per session, this is roughly 3–5 weeks of focused work.

---

## Working Rules

1. **One ticket at a time.** Finish it, test it, commit it.
2. **Tests are not optional.** Every ticket has tests. Write them first or
   alongside — never "later."
3. **Refactor continuously.** If something from an earlier ticket looks wrong
   now, fix it. Don't accumulate debt.
4. **Ask why.** If an agent suggests a pattern, ask it to explain. If you
   can't explain it in your own words, don't use it.
5. **Commit messages matter.** Use conventional format: `feat:`, `fix:`,
   `refactor:`, `test:`, `docs:`. Keep them short and meaningful.
6. **No shortcuts.** The goal is learning, not speed. A well-understood
   10-line function beats a mysterious 50-line one.
