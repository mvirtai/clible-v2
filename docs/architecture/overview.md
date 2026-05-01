# Architecture Overview

clible-v2 is a command-line Bible study tool with an optional web UI. The design prioritises offline operation, testability, and clean layer separation.

---

## System layers

```
┌─────────────────────────────────────────────────────────────┐
│  UI Layer                                                    │
│  cli.py, commands/ (seed, verse, search, analytics, backup) │
│  Click + Rich                                                │
└───────────────────────────┬─────────────────────────────────┘
                            │ calls
┌───────────────────────────▼─────────────────────────────────┐
│  Service Layer                                               │
│  SeedService, VerseService, AnalyticService, BackupService   │
└──────────────┬──────────────────────────────┬───────────────┘
               │ uses                         │ uses
┌──────────────▼──────────────┐  ┌────────────▼──────────────┐
│  Repositories                │  │  Parsers                  │
│  TranslationRepo, BookRepo,  │  │  CombinedParser           │
│  VerseRepo                   │  │  (USFX / OSIS / Beblia /  │
└──────────────┬───────────────┘  │   Zefania → verse dicts)  │
               │                  └───────────────────────────┘
┌──────────────▼──────────────┐
│  SQLite (clible.db)          │
│  books, translations,        │
│  verses, verses_fts (FTS5)   │
└─────────────────────────────┘
```

### Layer responsibilities

| Layer        | Responsibility                                      | Cannot touch                    |
|--------------|-----------------------------------------------------|---------------------------------|
| UI           | Parse user input, display output                    | DB, repos, parsers, HTTP        |
| Services     | Business logic, orchestration                       | UI, Click, Rich                 |
| Repositories | SQL queries, return plain dicts                     | Services, UI, network           |
| Parsers      | Read XML files, return verse dicts                  | DB, UI, services internals      |

These boundaries make each layer testable in isolation. Changing the database schema only touches the repository layer; changing the CLI output format only touches the UI layer.

---

## Web layer

The web app sits alongside the CLI rather than replacing it:

```
Browser (React/Vite)
    │ HTTP
Express server (Node.js/TypeScript)
    │ child_process.spawn
Clible CLI (Python)
    │ sqlite3
SQLite database (clible.db)
```

The Express server is a thin bridge. It sanitises request parameters, spawns `clible` commands with `--json`, parses the stdout, and forwards the result to the browser. It does not duplicate any verse lookup or search logic — that all lives in the Python CLI.

User sessions, authentication, and settings are stored in a separate PostgreSQL database (Neon). Verse data stays in SQLite.

See `docs/architecture/web-architecture.md` for the full web integration details.

---

## Data model

```sql
translations (id TEXT, name TEXT, language TEXT, ...)
books        (id TEXT, name TEXT, ...)
verses       (id INTEGER, translation_id, book_id, chapter, verse, text)
verses_fts   -- FTS5 virtual table over verses.text
_migrations  (name TEXT, applied_at TEXT)
```

Migrations live in `src/clible/db/migrations/` as numbered SQL files. The migration runner applies only those not yet recorded in `_migrations`.

---

## Key patterns

**Repository pattern** — Each repository is a small, focused class. It receives a `sqlite3.Connection` and returns plain `dict` or `TypedDict` values. No single "god" database class.

**Dependency injection** — All dependencies are passed through constructors. No singletons or module-level globals. This makes tests straightforward: inject an in-memory connection or a mock parser.

**Static Bible structure** — The list of 66 books and their chapter counts lives in `src/clible/data/bible_structure.json`. It is bundled with the app; no network call is needed to know the structure of the Bible.

**CombinedParser** — A single parser entry point (`CombinedParser.parse_file`) detects the XML root format and delegates to the appropriate sub-parser. This means the seed service never needs to know which format a translation uses.

---

## Architecture decisions

See `docs/architecture/adr/` for the rationale behind key decisions:

- [ADR-001](adr/001-offline-first-sqlite.md) — Offline-first with SQLite for verse data
- [ADR-002](adr/002-layered-architecture.md) — Strict layer separation
- [ADR-003](adr/003-xml-seed-parsers.md) — XML seed parsers instead of a live API
- [ADR-004](adr/004-postgres-for-user-data.md) — PostgreSQL for user data in the web layer
