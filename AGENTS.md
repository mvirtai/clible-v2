# Architecture and Conventions Guide

This document explains the architectural decisions, patterns, and conventions
used in clible v2. Read it before writing code so changes stay aligned with the
current architecture.

---

## What This Project Is

clible is a command-line Bible study tool. It seeds local XML translations from
public Bible data sources, stores verses in SQLite, and provides tools for
lookup, text analytics, and translation comparison.

This is a **v2 rebuild** of an existing project (ssh: <git@github.com>/mvirtai:clible) The developer already knows
what the app does. The focus is on building it with proper architecture,
clean separation of concerns, and thorough testing.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                   UI Layer                       │
│         (Click CLI + Rich rendering)             │
│                                                  │
│  cli.py          commands/                       │
└──────────────────────┬──────────────────────────┘
                       │ calls
┌──────────────────────▼──────────────────────────┐
│                Service Layer                     │
│            (Business logic)                      │
│                                                  │
│  SeedService    VerseService    AnalyticService  │
└───────┬──────────────────────────┬──────────────┘
        │ uses                     │ uses
┌───────▼────────┐    ┌───────────▼──────────────┐
│  Repositories  │    │   Parsers + seed data    │
│  (Data access) │    │   (XML -> verse dicts)   │
│                │    │                          │
│  VerseRepo     │    │  USFXParser              │
│ TranslationRepo│    │  OSISParser              │
│  BookRepo      │    │  BebliaParser            │
│                │    └──────────────────────────┘
└───────┬────────┘
        │
┌───────▼────────┐
│    SQLite       │
│   (clible.db)   │
└─────────────────┘
```

### Layer Rules

| Layer        | Can access              | Cannot access           |
|--------------|-------------------------|-------------------------|
| UI           | Services                | DB query logic, parser internals |
| Services     | Repos, parsers, seed downloads | UI, Click, Rich |
| Repositories | SQLite connection       | Services, network, UI   |
| Parsers      | XML files               | DB, network, UI         |

These boundaries exist so that:

- Each layer can be tested independently
- Changes in one layer don't ripple through the entire codebase
- The UI framework can be swapped without touching business logic

---

## Key Design Decisions

### 1. Repository pattern instead of a single DB class

**Problem in v1:** One `QueryDB` class with 900+ lines and 40+ methods
handling translations, books, verses, sessions, caching, and analysis. Hard
to test, hard to navigate, hard to modify.

**v2 approach:** Separate repository classes, each focused on one domain.
Repositories receive a `sqlite3.Connection` and return plain `dict` objects.

```python
class VerseRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_verse(
        self,
        translation_id: str,
        book_id: str,
        chapter: int,
        verse: int,
    ) -> dict | None:
        """Get one verse. Returns None if it is not installed."""
        ...
```

### 2. Dependency injection instead of singletons

**Problem in v1:** `AppState` singleton accessed from everywhere. Any module
could read or write global state. Made testing require careful singleton
reset, and made data flow invisible.

**v2 approach:** Dependencies are passed via constructor arguments.

```python
class VerseService:
    def __init__(
        self,
        verse_repo: VerseRepo,
        book_repo: BookRepo,
        translation_repo: TranslationRepo,
    ):
        self.verse_repo = verse_repo
        self.book_repo = book_repo
        self.translation_repo = translation_repo
```

This means:
- Tests can inject mocks easily
- Data flow is visible in the constructor
- No hidden global state

### 3. SQL migrations instead of CREATE IF NOT EXISTS

**Problem in v1:** Every app startup runs all CREATE TABLE statements. If
you need to add a column or change a constraint, there's no safe mechanism.

**v2 approach:** Numbered SQL files in `src/clible/db/migrations/`. A
`_migrations` table tracks which have been applied. On startup, only
unapplied migrations run.

### 4. Static Bible structure instead of runtime probing

**Problem in v1:** `calculate_max_chapter()` could make many sequential
network calls with delays to figure out how many chapters a book has. This is
public, static data.

**v2 approach:** Ship a `data/bible_structure.json` with all 66 books, their
chapter counts, and verse counts per chapter. Simple dictionary lookup instead
of network calls.

### 5. Offline seeding instead of runtime verse fetching

**Problem in v1:** Normal use depended on remote verse lookups, making the CLI
slower and less reliable when offline.

**v2 approach:** `SeedService` downloads catalog XML once, chooses the parser
from `translations.json`, validates known book IDs, and stores verses locally.
Verse lookup and analytics then read from SQLite without network calls.

### 6. Services own business logic, not repositories

**Problem in v1:** `queries.py` (the DB layer) imported `console` from the
UI module and printed directly. Caching logic lived inside `api.py`. Business
rules were scattered.

**v2 approach:** Repositories only do CRUD. Parsers only turn XML into verse
dicts. Orchestration, validation, seeding rules, and analytics live in the
service layer.

### 7. Click subcommands instead of while-True menu loop

**Problem in v1:** A `while True` loop with numbered menu choices. Not
composable, not scriptable, mixes control flow with business logic.

**v2 approach:** Click command groups with a clean verb-noun structure:
```
clible seed install web
clible verse "John 3:16"
clible analytics reference "John 3:16-18"
clible analytics compare "John 3:16-18"
```

An optional interactive mode can be added later for users who prefer menus.

---

## Naming Conventions

| Thing          | Convention              | Example                          |
|----------------|-------------------------|----------------------------------|
| Files          | snake_case              | `verse_repo.py`                  |
| Classes        | PascalCase              | `VerseService`                   |
| Functions      | snake_case              | `get_or_create`                  |
| Constants      | UPPER_SNAKE_CASE        | `SUPPORTED_FORMATS`              |
| Test files     | `test_` prefix          | `test_verse_repo.py`             |
| Test functions | `test_` prefix          | `test_search_is_case_insensitive`|
| Migrations     | `NNN_description.sql`   | `001_initial_schema.sql`         |
| Commit messages| Conventional Commits    | `feat: add verse search`         |

---

## File and Module Conventions

- One class per file when the class is substantial (repositories, services)
- Utility functions can share a file (`utils.py`, `config.py`)
- `__init__.py` files should be empty or contain only public API imports
- No circular imports — if you have one, the architecture is wrong

---

## Error Handling Strategy

- **Repositories:** Raise exceptions for constraint violations. Return `None`
  for "not found" cases.
- **Parsers:** Return normalized verse dictionaries or raise parse errors for
  invalid XML.
- **Services:** Catch repository, parser, and seed-download exceptions.
  Translate them into user-meaningful results or re-raise with context.
- **UI:** Catch service exceptions. Display user-friendly error messages.
  Never show raw tracebacks.

---

## Testing Conventions

- **Unit tests** for repositories and services (fast, isolated)
- **Integration tests** for full workflows (seed → lookup → analytics)
- **No real HTTP** in any test — mock seed downloads
- **In-memory SQLite** for database tests
- **Fixtures** in `conftest.py` for shared test setup:

```python
# tests/conftest.py
@pytest.fixture
def db_conn():
    """In-memory SQLite connection with migrations applied."""
    conn = sqlite3.connect(":memory:")
    run_migrations(conn)
    yield conn
    conn.close()

@pytest.fixture
def verse_repo(db_conn):
    return VerseRepo(db_conn)
```

---

## What NOT to Do

These are explicit anti-patterns. If you find yourself doing any of these,
stop and reconsider.

1. **Do not import UI modules in repositories or services.**
   No `from app.ui import console` in the data layer.

2. **Do not use f-strings in SQL queries.**
   Always use parameterized queries: `cursor.execute("... WHERE id = ?", (id,))`

3. **Do not add dependencies without justification.**
   Ask: "Can the standard library do this?" If yes, use stdlib.

4. **Do not write tests after the fact.**
   Tests are written alongside the code, as part of the same ticket.

5. **Do not use global mutable state.**
   No singletons, no module-level mutable variables.

6. **Do not put business logic in the CLI layer.**
   The CLI layer may build dependencies, then calls services and renders
   results.

7. **Do not commit broken tests.**
   If tests fail, fix them before committing.

8. **Do not generate massive code blocks without explanation.**
   This is a learning project. The developer must understand every line.
