# clible v2 — Project Overview

**Last updated:** 2026-05-04

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
│   AnalyticService (token stats, n-grams, translation compare)    │
└──────────────┬──────────────────────────────┬───────────────────┘
               │                              │
┌──────────────▼──────────────┐  ┌─────────────▼──────────────────┐
│ Repositories                │  │ Parsers                         │
│   TranslationRepo           │  │   USFXParser, OSISParser        │
│   BookRepo                  │  │   BebliaParser                  │
│   VerseRepo                 │  │   (XML → verse dicts)           │
│                              │  │                                 │
└──────────────┬──────────────┘  └─────────────────────────────────┘
               │
┌──────────────▼──────────────┐
│ SQLite (clible.db)          │
│   books, translations,     │
│   verses, verses_fts        │
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
| **002_seed_architecture.sql** | `src/clible/db/migrations/` | books, translations, verses + lookup indexes |
| **003_add_verse_fts.sql** | `src/clible/db/migrations/` | FTS5 `verses_fts` table + sync triggers |
| **Seed books** | `src/clible/db/seed_books.py` | Fills `books` from bible_structure.json when empty |
| **TranslationRepo** | `src/clible/db/repositories/translation_repo.py` | get_all, get_by_id, exists, create, delete, get_default |
| **BookRepo** | `src/clible/db/repositories/book_repo.py` | get_all, get_by_id, get_by_name, search |
| **VerseRepo** | `src/clible/db/repositories/verse_repo.py` | get_verse, get_verses, save_verses, search_text |
| **USFX parser** | `src/clible/parsers/usfx_parser.py` | parse_file(xml_path) → list of verse dicts |
| **OSIS parser** | `src/clible/parsers/osis_parser.py` | parse_file(xml_path) → list of verse dicts (container + milestone) |
| **Beblia parser** | `src/clible/parsers/beblia_parser.py` | parse_file(xml_path) → list of verse dicts using canonical book numbers |
| **OSIS book map** | `src/clible/parsers/osis_book_map.py` | OSIS book IDs → clible book IDs |
| **SeedService** | `src/clible/services/seed_service.py` | list_available, list_installed, seed_translation, remove_translation |
| **VerseService** | `src/clible/services/verse_service.py` | get_verse/get_verses, chapter/book retrieval, FTS search |
| **AnalyticService** | `src/clible/services/analytic_service.py` | token metrics, n-grams, concordance, translation comparison |
| **CLI** | `src/clible/cli.py`, `commands/` | seed, verse, analytics (reference, chapter, book, compare) |
| **Data files** | `src/clible/data/` | bible_structure.json, translations.json, stopwords.json, progress_quotes.json, sample XML |
| **Tests** | `tests/` | Repos, parsers, services, CLI; in-memory SQLite, mocked HTTP |
| **CI** | `.github/workflows/ci.yml` | uv, ruff, pytest on push/PR |
| **Task automation** | `Taskfile.yml`, `scripts/` | test/lint/check, Docker build/push, compare PR helper |
| **Dependencies** | `pyproject.toml` | click, rich, requests, ruff, pytest, pytest-mock |

### Planned (not yet implemented)

| Area | Notes |
|------|-------|
| **Export** | Markdown, plain text export |
| **Sessions** | Session tracking and saved study workflows from original PLAN.md |

---

## File Map

```
clible-v2/
├── src/clible/
│   ├── cli.py                 # Entry point, seed + verse command groups
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
│   │   ├── beblia_parser.py   # Beblia XML → verse dicts
│   │   ├── osis_book_map.py   # OSIS → clible book ID mapping
│   │   ├── osis_parser.py     # OSIS XML → verse dicts
│   │   └── usfx_parser.py     # USFX XML → verse dicts
│   ├── services/
│   │   ├── analytic_service.py
│   │   ├── seed_service.py
│   │   └── verse_service.py
│   └── data/
│       ├── bible_structure.json   # 66 books metadata
│       ├── translations.json      # Catalog (web, kjv, Finnish translations)
│       ├── progress_quotes.json   # Quotes shown during seed
│       ├── stopwords.json         # Language-specific analytics stopwords
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
├── Taskfile.yml
├── Dockerfile
├── scripts/create_compare_pr.sh
└── .github/workflows/ci.yml
```

---

## Database Schema

### 002_seed_architecture

**books** — Static reference (66 books)
- `id` TEXT PK (e.g. GEN, JHN)
- `name`, `testament`, `position`, `chapters`

**translations** — Installed Bible translations
- `id` TEXT PK (e.g. web, kjv, fin-1992)
- `name`, `language`, `format`, `source_url`, `installed_at`

**verses** — Actual Bible text
- `id` TEXT PK (UUID)
- `translation_id` FK, `book_id` FK
- `chapter`, `verse`, `text`
- UNIQUE(translation_id, book_id, chapter, verse)

Indexes: `idx_verses_lookup`, `idx_verses_search`

### 003_add_verse_fts

**verses_fts** — SQLite FTS5 virtual table for full-text search
- Stores indexed verse text using `content='verses'`
- Rebuilt once during migration
- Kept in sync by insert, delete, and update triggers

`VerseRepo.search_text()` queries this table and can optionally filter by
translation ID.

---

## Core Workflows

### Seed a translation

```bash
clible seed available
clible seed install web
clible seed install fin-1992
```

`SeedService` loads `translations.json`, downloads the XML file, chooses the
parser from the catalog format (`USFX`, `OSIS`, or `BEBLIA`), filters parsed
verses to known book IDs, saves the translation row, and bulk-inserts verses.

Supported catalog IDs currently include:

- `web` — World English Bible, USFX
- `kjv` — King James Version, OSIS
- `fin-biblia-33-38` — Finnish 1933/1938 Bible, OSIS
- `fin-1992`, `fin-1776`, `fin-stlk` — Finnish Beblia XML translations

### Look up verses

```bash
clible verse "John 3:16"
clible verse "John 3:16-18" -t web
```

`VerseService` accepts references in `Book Chapter:Verse` or
`Book Chapter:Start-End` format. It resolves exact book names first, then uses
book search as a fallback. If no translation is passed, the first installed
translation from `TranslationRepo.get_default()` is used.

### Analyze text

```bash
clible analytics reference "John 3:16-18" --top 5
clible analytics chapter John 3 -t kjv
clible analytics book Genesis -t web
```

`AnalyticService` calculates token count, unique token count, type-token ratio,
top words, top bigrams, and top trigrams. Stopwords come from
`src/clible/data/stopwords.json`; the CLI resolves the language from
`translations.json`.

### Compare Finnish translations

```bash
clible seed install fin-1992
clible seed install fin-1776
clible analytics compare "John 3:16-18"
```

`analytics compare` defaults to `fin-1992` vs `fin17xx`. The `fin17xx` and
`fin-17xx` aliases resolve to `fin-1776` when installed. The service aligns
verses by `(book_id, chapter, verse)`, marks missing sides, computes per-verse
similarity from sequence ratio plus token overlap, and returns aggregate
summary metrics.

### Developer and release checks

```bash
task check
task d-build
task d-push
```

`task check` runs Ruff linting, Ruff format check, and pytest. Docker tasks
build a runtime image tagged as both `latest` and the current Git commit. The
target image repository defaults to `docker.io/mvirtai/clible-v2` and can be
overridden with `CLIBLE_DOCKER_REPO`.

---

## Common Pitfalls

| Symptom | Resolution |
|---------|------------|
| `Verse(s) not found.` | Install a translation with `clible seed install <id>` and verify the reference format. |
| `Comparison failed. Missing translation(s): fin17xx` | Install `fin-1776`; the default right-side compare argument is an alias. |
| `Unknown translation` during seed | Run `clible seed available` and use an ID from `translations.json`. |
| No analytics results for a valid reference | Confirm the selected translation is installed and contains the requested book/chapter/verse range. |

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
