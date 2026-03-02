# clible v2 — Project Overview

**Last updated:** 2026-03-02

This document provides a comprehensive picture of the clible v2 application: what it is, its architecture, current implementation status, and where all the pieces live.

---

## What Is clible?

clible is a command-line Bible study tool. The v2 rebuild aims for:

- **Offline-first** — Seed local XML data from [seven1m/open-bibles](https://github.com/seven1m/open-bibles), no API calls during normal use
- **Layered architecture** — Clear separation: UI → Services → Repositories → SQLite
- **Professional quality** — Testable, maintainable, portfolio-ready code

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ UI Layer                                                        │
│   cli.py, commands/seed.py, commands/verse.py (Click + Rich)    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│ Service Layer                                                    │
│   SeedService (install, list, remove)  VerseService (lookup)     │
└──────────────┬──────────────────────────────┬───────────────────┘
               │                              │
┌──────────────▼──────────────┐  ┌─────────────▼──────────────────┐
│ Repositories                │  │ Parsers                         │
│   TranslationRepo           │  │   USFXParser, OSISParser        │
│   BookRepo                 │  │   (XML → verse dicts)           │
│   VerseRepo                │  │                                 │
└──────────────┬──────────────┘  └─────────────────────────────────┘
               │
┌──────────────▼──────────────┐
│ SQLite (clible.db)          │
│   books, translations,     │
│   verses                    │
└────────────────────────────┘
```

**Layer rules:** Repositories access DB only. Services orchestrate. UI never touches DB or HTTP directly.

---

## Current Implementation Status

### Done ✅

| Component | Location | Notes |
|-----------|----------|-------|
| **Config** | `src/clible/config.py` | Config dataclass, env overrides (CLIBLE_*) |
| **DB connection** | `src/clible/db/connection.py` | WAL, foreign_keys, row_factory, migrations, seed_books |
| **Migrations** | `src/clible/db/migrations.py` | `_migrations` table, ordered `.sql` execution |
| **002_seed_architecture.sql** | `src/clible/db/migrations/` | books, translations, verses + indexes |
| **Seed books** | `src/clible/db/seed_books.py` | Fills `books` from bible_structure.json when empty |
| **TranslationRepo** | `src/clible/db/repositories/translation_repo.py` | get_all, get_by_id, exists, create, delete, get_default |
| **BookRepo** | `src/clible/db/repositories/book_repo.py` | get_all, get_by_id, get_by_name, search |
| **VerseRepo** | `src/clible/db/repositories/verse_repo.py` | get_verse, get_verses, save_verses |
| **USFX parser** | `src/clible/parsers/usfx_parser.py` | parse_file(xml_path) → list of verse dicts |
| **OSIS parser** | `src/clible/parsers/osis_parser.py` | parse_file(xml_path) → list of verse dicts (container + milestone) |
| **OSIS book map** | `src/clible/parsers/osis_book_map.py` | OSIS book IDs → clible book IDs |
| **SeedService** | `src/clible/services/seed_service.py` | list_available, list_installed, seed_translation, remove_translation |
| **VerseService** | `src/clible/services/verse_service.py` | get_verse(reference, translation_id) |
| **CLI** | `src/clible/cli.py`, `commands/` | seed (install, list, available, remove), verse |
| **Data files** | `src/clible/data/` | bible_structure.json, translations.json, progress_quotes.json, eng-web.usfx.xml |
| **Tests** | `tests/` | Repos, parsers, services, CLI; in-memory SQLite, mocked HTTP |
| **CI** | `.github/workflows/ci.yml` | uv, ruff, pytest on push/PR |
| **Dependencies** | `pyproject.toml` | click, rich, requests, ruff, pytest, pytest-mock |

### Planned (not yet implemented)

| Area | Notes |
|------|-------|
| **Search** | Full-text search across verses |
| **Export** | Markdown, plain text export |
| **Sessions / analytics** | From original PLAN.md |

---

## File Map

```
clible-v2/
├── src/clible/
│   ├── cli.py                 # Entry point, seed + verse command groups
│   ├── config.py              # Configuration (env overrides)
│   ├── commands/
│   │   ├── seed.py            # seed install, list, available, remove
│   │   └── verse.py           # verse "reference" -t translation
│   ├── db/
│   │   ├── connection.py      # get_connection, migrations, seed_books
│   │   ├── migrations.py      # run_migrations()
│   │   ├── migrations/
│   │   │   ├── 001_initial_schema.sql   # Placeholder
│   │   │   └── 002_seed_architecture.sql
│   │   ├── seed_books.py      # seed_books_if_empty(conn)
│   │   └── repositories/
│   │       ├── book_repo.py
│   │       ├── translation_repo.py
│   │       └── verse_repo.py
│   ├── parsers/
│   │   ├── osis_book_map.py   # OSIS → clible book ID mapping
│   │   ├── osis_parser.py     # OSIS XML → verse dicts
│   │   └── usfx_parser.py     # USFX XML → verse dicts
│   ├── services/
│   │   ├── seed_service.py
│   │   └── verse_service.py
│   └── data/
│       ├── bible_structure.json   # 66 books metadata
│       ├── translations.json      # Catalog (web, kjv, fin-biblia)
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

## Database Schema (002_seed_architecture)

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

Indexes: `idx_verses_lookup`, `idx_verses_search`

---

## Key Conventions

- **Config:** `get_config()` from `clible.config`; override via `CLIBLE_*` env vars
- **DB:** `get_connection()` or `get_connection(":memory:")`; repos receive `conn` in constructor
- **Repos:** Return plain dicts (or TypedDict like BookRow); no sqlite3.Row leakage
- **Tests:** In-memory SQLite, mocked HTTP; fixtures in `conftest.py`
- **Entry point:** `clible` script (pyproject.toml) or `python main.py`

---

## Related Documents

- **README.md** — User-facing usage and installation
- **PLAN.md** — Original phase plan (API-based; seed path supersedes for now)
