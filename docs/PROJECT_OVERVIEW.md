# clible v2 — Project Overview

**Last updated:** 2026-03-16

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
│   cli.py, commands/seed.py, commands/verse.py,                 │
│   commands/analytics.py (Click + Rich)                         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│ Service Layer                                                    │
│   SeedService (install, list, remove)                            │
│   VerseService (lookup + ranges + chapter/book access)           │
│   AnalyticService (metrics, n-grams, comparison)                 │
└──────────────┬──────────────────────────────┬───────────────────┘
               │                              │
┌──────────────▼──────────────┐  ┌─────────────▼──────────────────┐
│ Repositories                │  │ Parsers                         │
│   TranslationRepo           │  │   USFXParser, OSISParser,       │
│   BookRepo                  │  │   BebliaParser                  │
│   VerseRepo (+ FTS search)  │  │   (XML → verse dicts)           │
└──────────────┬──────────────┘  └─────────────────────────────────┘
               │
┌──────────────▼──────────────┐
│ SQLite (clible.db)          │
│   books, translations,       │
│   verses, verses_fts (FTS5) │
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
| **003_add_verse_fts.sql** | `src/clible/db/migrations/` | FTS5 table + triggers to keep verse search index in sync |
| **Seed books** | `src/clible/db/seed_books.py` | Fills `books` from bible_structure.json when empty |
| **TranslationRepo** | `src/clible/db/repositories/translation_repo.py` | get_all, get_by_id, exists, create, delete, get_default |
| **BookRepo** | `src/clible/db/repositories/book_repo.py` | get_all, get_by_id, get_by_name, search |
| **VerseRepo** | `src/clible/db/repositories/verse_repo.py` | get_verse, get_verses, get_verses_in_range, get_book_verses, search_text, save_verses |
| **USFX parser** | `src/clible/parsers/usfx_parser.py` | parse_file(xml_path) → list of verse dicts |
| **OSIS parser** | `src/clible/parsers/osis_parser.py` | parse_file(xml_path) → list of verse dicts (container + milestone) |
| **BEBLIA parser** | `src/clible/parsers/beblia_parser.py` | parse_file(xml_path) for BEBLIA XML translations |
| **OSIS book map** | `src/clible/parsers/osis_book_map.py` | OSIS book IDs → clible book IDs |
| **SeedService** | `src/clible/services/seed_service.py` | list_available, list_installed, seed_translation, remove_translation |
| **VerseService** | `src/clible/services/verse_service.py` | get_verse, get_verses (single + range), chapter/book retrieval, FTS-backed text search |
| **AnalyticService** | `src/clible/services/analytic_service.py` | token stats, top-N words, bigrams, trigrams, translation comparison |
| **CLI** | `src/clible/cli.py`, `commands/` | seed, verse, analytics (reference/chapter/book/compare) |
| **Data files** | `src/clible/data/` | bible_structure.json, translations.json, stopwords.json, progress_quotes.json, eng-web.usfx.xml |
| **Tests** | `tests/` | Repos, parsers, services, CLI (including range lookup and compare); in-memory SQLite, mocked HTTP |
| **CI** | `.github/workflows/ci.yml` | uv, ruff, pytest on push/PR |
| **Task automation** | `Taskfile.yml`, `scripts/` | Lint/test/build tasks + `pr-compare` helper for compare feature PR drafts |
| **Dependencies** | `pyproject.toml` | click, rich, requests, ruff, pytest, pytest-mock |

### Planned (not yet implemented)

| Area | Notes |
|------|-------|
| **Concordance CLI command** | Repository/service support exists via FTS; no dedicated user command yet |
| **Export** | Markdown, plain text export |
| **Sessions** | From original PLAN.md |

---

## File Map

```
clible-v2/
├── src/clible/
│   ├── cli.py                 # Entry point, seed + verse + analytics command groups
│   ├── config.py              # Configuration (env overrides)
│   ├── commands/
│   │   ├── analytics.py       # analytics reference/chapter/book/compare
│   │   ├── seed.py            # seed install, list, available, remove
│   │   └── verse.py           # verse "reference" -t translation
│   ├── db/
│   │   ├── connection.py      # get_connection, migrations, seed_books
│   │   ├── migrations.py      # run_migrations()
│   │   ├── migrations/
│   │   │   ├── 001_initial_schema.sql   # Placeholder
│   │   │   ├── 002_seed_architecture.sql
│   │   │   └── 003_add_verse_fts.sql
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
│   └── data/
│       ├── bible_structure.json   # 66 books metadata
│       ├── translations.json      # Catalog (USFX, OSIS, BEBLIA)
│       ├── stopwords.json         # Language-specific stopword lists (en, fi)
│       ├── progress_quotes.json   # Quotes shown during seed
│       └── eng-web.usfx.xml       # Sample XML
├── tests/
│   ├── conftest.py            # db_conn, repo fixtures
│   ├── test_config.py
│   ├── test_cli/
│   ├── test_db/
│   ├── test_parsers/
│   ├── test_services/
│   └── fixtures/             # sample.usfx.xml, etc.
├── docs/
│   └── PROJECT_OVERVIEW.md   # This file
├── scripts/
│   └── create_compare_pr.sh   # PR helper script used by Taskfile
├── Taskfile.yml
├── main.py                   # Launches cli.main()
├── pyproject.toml
└── .github/workflows/ci.yml
```

---

## Database Schema (002 + 003)

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

**verses_fts** — Full-text index (FTS5 virtual table)
- `text` indexed from `verses.text`
- Triggers keep the index in sync on INSERT/UPDATE/DELETE

Indexes: `idx_verses_lookup`, `idx_verses_search` + FTS5 virtual index

---

## Key Conventions

- **Config:** `get_config()` from `clible.config`; override via `CLIBLE_*` env vars
- **DB:** `get_connection()` or `get_connection(":memory:")`; repos receive `conn` in constructor
- **Repos:** Return plain dicts (or TypedDict like BookRow); no sqlite3.Row leakage
- **Default translation behavior:** prefer `web` when installed, otherwise first installed translation
- **Tests:** In-memory SQLite, mocked HTTP; fixtures in `conftest.py`
- **Entry point:** `clible` script (pyproject.toml) or `python main.py`

---

## Related Documents

- **README.md** — User-facing usage and installation
- **PLAN.md** — Original phase plan (API-based; seed path supersedes for now)
