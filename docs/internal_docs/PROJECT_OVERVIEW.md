# clible v2 — Project Overview

**Last updated:** 2026-04-12

This document provides a comprehensive picture of the clible v2 application: what it is, its architecture, current implementation status, and where all the pieces live.

---

## What Is clible?

clible is a command-line Bible study tool. The v2 rebuild aims for:

- **Offline-first** — Seed local XML data from [seven1m/open-bibles](https://github.com/seven1m/open-bibles), no API calls during normal use
- **Layered architecture** — Clear separation: UI → Services → Repositories → SQLite
- **Professional quality** — Testable, maintainable, portfolio-ready code

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│ UI Layer                                                        │
│   cli.py, commands/seed.py, commands/verse.py,                   │
│   commands/search.py, commands/analytics.py, commands/backup.py  │
│   (Click + Rich)                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│ Service Layer                                                    │
│   SeedService (install/list/remove), VerseService (lookup/search),│
│   AnalyticService (token stats, n-grams, compare, concordance)   │
└──────────────┬──────────────────────────────┬───────────────────┘
               │                              │
┌──────────────▼──────────────┐  ┌─────────────▼──────────────────┐
│ Repositories                │  │ Parsers                         │
│   TranslationRepo           │  │   USFXParser, OSISParser,        │
│   BookRepo                  │  │   BebliaParser                   │
│   VerseRepo                 │  │   (XML → verse dicts)           │
└──────────────┬──────────────┘  └─────────────────────────────────┘
               │
┌──────────────▼──────────────┐
│ SQLite (clible.db)          │
│   books, translations,      │
│   verses + verses_fts (FTS5)│
└────────────────────────────┘
```

**Layer rules:** Repositories access DB only. Services orchestrate. UI never touches DB or HTTP directly.

---

## Current Implementation Status

### Done ✅

| Component | Location | Notes |
| --------- | -------- | ----- |
| **Config** | `src/clible/config.py` | Config dataclass, env overrides (CLIBLE_*) |
| **DB connection** | `src/clible/db/connection.py` | WAL, foreign_keys, row_factory, migrations, seed_books |
| **Migrations** | `src/clible/db/migrations.py` | `_migrations` table, ordered `.sql` execution |
| **002_seed_architecture.sql** | `src/clible/db/migrations/` | books, translations, verses + indexes |
| **003_add_verse_fts.sql** | `src/clible/db/migrations/` | FTS5 virtual table + triggers for `verses` |
| **004_drop_verses_text_index.sql** | `src/clible/db/migrations/` | Drops redundant B-tree index on `verses.text` |
| **Seed books** | `src/clible/db/seed_books.py` | Fills `books` from bible_structure.json when empty |
| **TranslationRepo** | `src/clible/db/repositories/translation_repo.py` | get_all, get_by_id, exists, create, delete, get_default |
| **BookRepo** | `src/clible/db/repositories/book_repo.py` | get_all, get_by_id, get_by_name, search |
| **VerseRepo** | `src/clible/db/repositories/verse_repo.py` | get_verse, get_verses, get_verses_in_range, save_verses, search_text |
| **USFX parser** | `src/clible/parsers/usfx_parser.py` | parse_file(xml_path) → list of verse dicts |
| **OSIS parser** | `src/clible/parsers/osis_parser.py` | parse_file(xml_path) → list of verse dicts (container + milestone) |
| **Beblia parser** | `src/clible/parsers/beblia_parser.py` | parse_file(xml_path) for BEBLIA XML format |
| **OSIS book map** | `src/clible/parsers/osis_book_map.py` | OSIS book IDs → clible book IDs |
| **SeedService** | `src/clible/services/seed_service.py` | list_available, list_installed, seed_translation, remove_translation |
| **VerseService** | `src/clible/services/verse_service.py` | get_verse/get_verses (single + range), chapter/book retrieval, FTS search |
| **AnalyticService** | `src/clible/services/analytic_service.py` | token metrics, top words, bigrams, trigrams, concordance |
| **CLI** | `src/clible/cli.py`, `commands/` | seed (install/list/available/remove), verse, search, analytics (reference/chapter/book/compare), backup |
| **Export (UI)** | `src/clible/ui/export_cli.py`, `analytics_export.py`, `verse_search_export.py` | Unified `--export` parsing; serializers for analytics + verse/search (no DB in these modules) |
| **Data files** | `src/clible/data/` | bible_structure.json, translations.json, stopwords.json, progress_quotes.json |
| **Tests** | `tests/` | Repos, parsers, services, CLI; in-memory SQLite, mocked HTTP |
| **CI** | `.github/workflows/ci.yml` | uv, ruff, pytest on push/PR |
| **Task automation** | `Taskfile.yml` | lint/test/check + Docker build/push tasks |
| **Dependencies** | `pyproject.toml` | click, rich, requests, ruff, pytest, pytest-mock |
| **Web UI** | `src/clible-web/` | React/Vite + Express bridge; verse lookup, FTS5 search, analytics, export, AI insights, JWT auth |
| **Analytics scopes (web)** | `src/clible-web/services/bibleService.ts` | Reference/Chapter/Book scope arg-building with correct reference parsing |

### Planned (not yet implemented)

| Area | Notes |
| ---- | ----- |
| **Sessions** | From original PLAN.md |

---

## File Map

```text
clible-v2/
├── src/clible-web/                 # Web UI (React/Vite + Express bridge)
│   ├── server.ts                  # Express: API bridge, auth, AI proxy
│   ├── App.tsx                    # Root component; state, routing, analytics
│   ├── components/                # AnalyticsView, ReaderView, SearchView, …
│   ├── services/bibleService.ts   # Analytics scope arg-building, AI calls
│   ├── repositories/              # HTTP calls to /api/*
│   ├── types/                     # Shared TS types (BibleResponse, TextStats, …)
│   ├── views/                     # Full-page views (LoginView)
│   ├── user/                      # SettingsContext, per-user prefs
│   ├── INTEGRATION.md             # Web↔CLI bridge docs (Finnish)
│   └── README.md                  # Setup, features, architecture
├── src/clible/
│   ├── cli.py                 # Entry point, CLI groups
│   ├── config.py              # Configuration (env overrides)
│   ├── commands/
│   │   ├── seed.py            # seed install, list, available, remove
│   │   ├── verse.py           # verse "reference" -t translation
│   │   ├── search.py          # search "query" with scope controls
│   │   ├── analytics.py       # analytics reference/chapter/book/compare
│   │   └── backup.py          # backup gcs, restore-gcs
│   ├── db/
│   │   ├── connection.py      # get_connection, migrations, seed_books
│   │   ├── migrations.py      # run_migrations()
│   │   ├── migrations/
│   │   │   ├── 001_initial_schema.sql   # Placeholder
│   │   │   ├── 002_seed_architecture.sql
│   │   │   ├── 003_add_verse_fts.sql
│   │   │   └── 004_drop_verses_text_index.sql
│   │   ├── seed_books.py      # seed_books_if_empty(conn)
│   │   └── repositories/
│   │       ├── book_repo.py
│   │       ├── translation_repo.py
│   │       └── verse_repo.py
│   ├── parsers/
│   │   ├── beblia_parser.py   # BEBLIA XML → verse dicts
│   │   ├── osis_book_map.py   # OSIS → clible book ID mapping
│   │   ├── osis_parser.py     # OSIS XML → verse dicts
│   │   └── usfx_parser.py     # USFX XML → verse dicts
│   ├── services/
│   │   ├── analytic_service.py
│   │   ├── seed_service.py
│   │   └── verse_service.py
│   ├── ui/
│   │   ├── export_cli.py        # --export key=value parsing (PATH, FILENAME, FORMAT)
│   │   ├── analytics_export.py  # analytics/compare → file formats
│   │   └── verse_search_export.py  # verse lookup + search → file formats
│   └── data/
│       ├── bible_structure.json   # 66 books metadata
│       ├── translations.json      # Catalog (web, kjv, fin-biblia-33-38, fin-1992, ...)
│       ├── stopwords.json         # Language-specific stopword lists (en, fi)
│       ├── progress_quotes.json   # Quotes shown during seed
│       └── eng-web.usfx.xml       # Sample XML
├── tests/
│   ├── conftest.py            # db_conn, repo fixtures
│   ├── test_config.py
│   ├── test_cli/
│   ├── test_data/
│   ├── test_db/
│   ├── test_parsers/
│   ├── test_services/
│   └── fixtures/             # sample.usfx.xml, etc.
├── docs/
│   └── PROJECT_OVERVIEW.md   # This file
├── main.py                   # Launches cli.main()
├── pyproject.toml
└── .github/workflows/ci.yml
```

---

## Database Schema (002_seed_architecture + 003_add_verse_fts + 004_drop_verses_text_index)

**books** — Static reference (66 books)

- `id` TEXT PK (e.g. GEN, JHN)
- `name`, `testament`, `position`, `chapters`

**translations** — Installed Bible translations

- `id` TEXT PK (e.g. web, kjv)
- `name`, `language`, `format`, `source_url`, `installed_at`

**verses** — Actual Bible text

- `id` TEXT PK (UUID)
- `translation_id` FK, `book_id` FK
- `chapter`, `verse`, `text`
- UNIQUE(translation_id, book_id, chapter, verse)

Index: `idx_verses_lookup` (redundant `idx_verses_search` on `text` removed in migration 004; FTS5 covers search)

**verses_fts** — FTS5 index for full-text search

- Virtual table linked to `verses(text)`
- Triggers keep index synced on INSERT/UPDATE/DELETE
- Used by `VerseRepo.search_text()` and analytics concordance

---

## Key Conventions

- **Config:** `get_config()` from `clible.config`; override via `CLIBLE_*` env vars
- **DB:** `get_connection()` or `get_connection(":memory:")`; repos receive `conn` in constructor
- **Repos:** Return TypedDict row types (`BookRow`, `TranslationRow`, `VerseRow`); no sqlite3.Row leakage
- **PEP 561:** `src/clible/py.typed` marks the installable package as carrying inline type information for downstream type checkers
- **Default translation:** `web` if installed, otherwise first installed translation
- **Analytics stopwords:** language picked from `translations.json` (`language` field), fallback `en`
- **Tests:** In-memory SQLite, mocked HTTP; fixtures in `conftest.py`
- **Entry point:** `clible` script (pyproject.toml) or `python main.py`

---

## Related Documents

- **README.md** — User-facing usage and installation
- **PLAN.md** — Original phase plan (API-based; seed path supersedes for now)

---

## What’s Next (Backlog)

Backlog is tracked in:
- `notes/code-review-2026-03-26.md` (what is still change-worthy)
- `plans/future-directions_2026-03-26.plan.md` (feature direction by theme)
- `PLAN.md` (original ticket breakdown / learning order)

High-impact remaining items (as of `2026-04-12`):
- **Extended analytics scopes**: multi-book, Old/New Testament, whole-Bible analysis.
- **Concordance view (web)**: expose the CLI concordance command in the web UI.
- **CLI connection management refactor**: use Click context to keep a single DB connection per command invocation.
- **Export deduplication**: consolidate shared export flow/helpers across verse/search/analytics.
