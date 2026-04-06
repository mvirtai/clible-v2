# clible v2 — Project Overview

**Last updated:** 2026-04-06

This document describes the current clible v2 implementation: architecture, active codepaths, public CLI workflows, and the present roadmap.

---

## What Is clible?

clible is an offline-first command-line Bible study tool.

Core workflow:
1. Install translations by downloading XML once (`seed install`).
2. Parse and normalize verse data into SQLite.
3. Run local verse lookup and analytics from the database.

Primary goals:
- **Offline-first usage** after seeding
- **Layered architecture** (UI → Services → Repositories → SQLite)
- **Professional code quality** (testability, explicit boundaries, clean CLI UX)

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│ UI Layer (Click + Rich)                                           │
│   cli.py, commands/seed.py, commands/verse.py, commands/analytics.py │
└───────────────────────────────┬────────────────────────────────────┘
                                │
┌───────────────────────────────▼────────────────────────────────────┐
│ Service Layer                                                       │
│   SeedService  VerseService  AnalyticService                       │
└──────────────┬──────────────────────────────┬──────────────────────┘
               │                              │
┌──────────────▼──────────────┐  ┌────────────▼──────────────────────┐
│ Repositories                │  │ Parsers                            │
│   TranslationRepo           │  │   USFXParser, OSISParser,          │
│   BookRepo                  │  │   BebliaParser (XML → verse dicts) │
│   VerseRepo                 │  │                                    │
└──────────────┬──────────────┘  └────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────────┐
│ SQLite (clible.db)                                                  │
│   books, translations, verses, verses_fts (FTS5) + sync triggers    │
└──────────────────────────────────────────────────────────────────────┘
```

**Boundary rule:** UI calls services; services orchestrate repositories/parsers; repositories only access SQLite.

---

## Public CLI Interfaces (Current)

### Translation management
- `clible seed available`
- `clible seed install <translation_id>`
- `clible seed list`
- `clible seed remove <translation_id>`

Supported source formats:
- **USFX:** `web`
- **OSIS:** `kjv`, `fin-biblia-33-38`
- **BEBLIA:** `fin-1992`, `fin-1776`, `fin-stlk`

### Verse lookup
- `clible verse "John 3:16"`
- `clible verse "John 3:16-18"`
- `clible verse "1 Corinthians 13:4" -t web`

Reference constraints:
- Valid forms: `Book Chapter:Verse` and same-chapter ranges `Book Chapter:Verse-Verse`
- Cross-chapter ranges are not currently supported

### Text analytics
- `clible analytics reference "John 3:16-18" [-t <translation>] [--top N]`
- `clible analytics chapter John 3 [-t <translation>] [--top N]`
- `clible analytics book John [-t <translation>] [--top N]`
- `clible analytics compare "John 3:16-18" [--left <id>] [--right <id>]`

`analytics compare` defaults to `fin-1992` vs `fin17xx` (`fin17xx` resolves to installed `fin-1776`, or another installed `fin-17*` translation).

---

## Current Implementation Status

### Implemented ✅

| Component | Location | Notes |
|-----------|----------|-------|
| **Config** | `src/clible/config.py` | `Config` dataclass + `CLIBLE_*` env overrides |
| **DB connection** | `src/clible/db/connection.py` | WAL, foreign keys, row factory, migrations, `seed_books_if_empty` |
| **Migration runner** | `src/clible/db/migrations.py` | `_migrations` table + ordered `.sql` execution |
| **Schema migrations** | `src/clible/db/migrations/` | `001_initial_schema.sql`, `002_seed_architecture.sql`, `003_add_verse_fts.sql` |
| **Books seeding** | `src/clible/db/seed_books.py` | Seeds static books metadata from `bible_structure.json` |
| **Repositories** | `src/clible/db/repositories/` | `TranslationRepo`, `BookRepo`, `VerseRepo` |
| **Parsers** | `src/clible/parsers/` | `USFXParser`, `OSISParser`, `BebliaParser`, `osis_book_map.py` |
| **Seed service** | `src/clible/services/seed_service.py` | Download + parse + save translations |
| **Verse service** | `src/clible/services/verse_service.py` | Reference parsing, default translation resolution, range/chapter/book lookup, text search |
| **Analytic service** | `src/clible/services/analytic_service.py` | Token metrics, n-grams, concordance, translation comparison |
| **CLI commands** | `src/clible/commands/` | `seed`, `verse`, `analytics` (including `compare`) |
| **Data files** | `src/clible/data/` | `bible_structure.json`, `translations.json`, `stopwords.json`, `progress_quotes.json` |
| **Test suite** | `tests/` | Repository/service/parser/CLI coverage with in-memory SQLite and mocked network |

### Pending / partially planned

| Area | Status |
|------|--------|
| **Export workflows** | Not implemented yet (`markdown`/`text` export commands absent) |
| **Session workflows** | Not implemented yet in v2 |
| **Original API-client-first path in PLAN** | Superseded in practice by offline seeding workflow |

---

## File Map

```
clible-v2/
├── src/clible/
│   ├── cli.py
│   ├── config.py
│   ├── commands/
│   │   ├── seed.py
│   │   ├── verse.py
│   │   └── analytics.py
│   ├── db/
│   │   ├── connection.py
│   │   ├── migrations.py
│   │   ├── migrations/
│   │   │   ├── 001_initial_schema.sql
│   │   │   ├── 002_seed_architecture.sql
│   │   │   └── 003_add_verse_fts.sql
│   │   ├── repositories/
│   │   │   ├── book_repo.py
│   │   │   ├── translation_repo.py
│   │   │   └── verse_repo.py
│   │   └── seed_books.py
│   ├── parsers/
│   │   ├── beblia_parser.py
│   │   ├── osis_book_map.py
│   │   ├── osis_parser.py
│   │   └── usfx_parser.py
│   ├── services/
│   │   ├── analytic_service.py
│   │   ├── seed_service.py
│   │   └── verse_service.py
│   └── data/
│       ├── bible_structure.json
│       ├── translations.json
│       ├── stopwords.json
│       └── progress_quotes.json
├── tests/
│   ├── test_cli/
│   ├── test_db/
│   ├── test_parsers/
│   ├── test_services/
│   └── fixtures/
├── docs/
│   └── PROJECT_OVERVIEW.md
├── README.md
├── PLAN.md
└── pyproject.toml
```

---

## Database Schema Snapshot

### Core tables (`002_seed_architecture.sql`)

**books**
- `id` TEXT PK (e.g. `GEN`, `JHN`)
- `name`, `testament`, `position`, `chapters`

**translations**
- `id` TEXT PK (e.g. `web`, `fin-1992`)
- `name`, `language`, `format`, `source_url`, `installed_at`

**verses**
- `id` TEXT PK (UUID generated in Python)
- `translation_id` FK → `translations(id)` with `ON DELETE CASCADE`
- `book_id` FK → `books(id)`
- `chapter`, `verse`, `text`
- `UNIQUE(translation_id, book_id, chapter, verse)`

### Full-text search (`003_add_verse_fts.sql`)

- `verses_fts` virtual table (FTS5) indexed on verse text
- Insert/update/delete triggers (`verses_ai`, `verses_au`, `verses_ad`) keep FTS index synchronized with `verses`

---

## Operational Notes

- `seed install` is the only networked runtime path (downloads source XML).
- Verse lookup and analytics read local SQLite only.
- Default translation resolution:
  1. Use requested `-t/--translation` when provided.
  2. Otherwise prefer installed `web`.
  3. Fallback to first installed translation.
- For Finnish comparison workflows, install both:
  - `fin-1992`
  - `fin-1776` (used by `fin17xx` alias)

---

## Related Documents

- **README.md** — setup, commands, runbook, troubleshooting
- **PLAN.md** — original phased plan (parts superseded by current implementation choices)
