# clible v2 — Project Overview

**Last updated:** 2026-03-30

This document describes the current state of clible v2: architecture, implemented
features, key codepaths, and developer-facing constraints.

---

## What clible Is

clible is an offline-first command-line Bible study tool.

Core flow:
1. Install a translation once (`clible seed install <id>`)
2. Query and analyze verses locally from SQLite (`clible verse`, `clible analytics`)

No runtime API calls are required after a translation is seeded.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│ UI layer (Click + Rich)                                           │
│   cli.py, commands/seed.py, commands/verse.py, commands/analytics.py
└───────────────────────────────┬────────────────────────────────────┘
                                │
┌───────────────────────────────▼────────────────────────────────────┐
│ Service layer                                                      │
│   SeedService, VerseService, AnalyticService                       │
└──────────────┬──────────────────────────────┬──────────────────────┘
               │                              │
┌──────────────▼──────────────┐  ┌────────────▼──────────────────────┐
│ Repositories                │  │ Parsers                            │
│   TranslationRepo           │  │   USFXParser, OSISParser,         │
│   BookRepo                  │  │   BebliaParser (XML -> verse rows)│
│   VerseRepo                 │  │                                    │
└──────────────┬──────────────┘  └────────────────────────────────────┘
               │
┌──────────────▼──────────────┐
│ SQLite (clible.db)          │
│   books, translations,      │
│   verses + verses_fts       │
└─────────────────────────────┘
```

Layer boundaries:
- UI calls services only.
- Services coordinate repositories/parsers.
- Repositories access SQLite only.
- Parsers convert XML to plain verse dicts.

---

## Current Implementation Status

### Implemented

| Area | Location | Notes |
|------|----------|-------|
| CLI entrypoint | `src/clible/cli.py` | Command groups: `seed`, `analytics`, plus `verse` |
| Translation seeding | `src/clible/commands/seed.py`, `services/seed_service.py` | Install/list/available/remove |
| Verse lookup | `src/clible/commands/verse.py`, `services/verse_service.py` | Single verse + same-chapter ranges (`John 3:16-18`) |
| Text analytics | `src/clible/commands/analytics.py`, `services/analytic_service.py` | Reference/chapter/book analysis + translation comparison |
| Translation comparison | `commands/analytics.py`, `services/analytic_service.py` | Side-by-side diff and similarity summary |
| Supported XML formats | `src/clible/parsers/` | USFX, OSIS, BEBLIA |
| DB connection + migrations | `src/clible/db/connection.py`, `db/migrations.py` | WAL, foreign keys, row factory, ordered SQL migrations |
| Full-text search index | `src/clible/db/migrations/003_add_verse_fts.sql` | FTS5 table + triggers synced with `verses` |
| Core repositories | `src/clible/db/repositories/` | `TranslationRepo`, `BookRepo`, `VerseRepo` |
| Data catalogs | `src/clible/data/` | `bible_structure.json`, `translations.json`, `stopwords.json` |
| Test suite | `tests/` | Repo/service/parser/CLI coverage with in-memory SQLite and mocked HTTP |

### Partially implemented or pending

| Area | Status |
|------|--------|
| Dedicated CLI search command | Pending (FTS-backed repo/service methods exist) |
| Export workflows | Pending |
| Session workflows | Pending |

---

## Public CLI Interfaces

### Translation management

- `clible seed available`
- `clible seed install <translation_id>`
- `clible seed list`
- `clible seed remove <translation_id>`

Supported translation formats in current catalog:
- USFX: `web`
- OSIS: `kjv`, `fin-biblia-33-38`
- BEBLIA: `fin-1992`, `fin-1776`, `fin-stlk`

### Verse lookup

- `clible verse "John 3:16"`
- `clible verse "John 3:16-18" -t fin-1992`

Constraints:
- Reference must match `Book Chapter:Verse` or `Book Chapter:Start-End`.
- Ranges are same-chapter only.
- If `-t/--translation` is omitted, default translation resolution is:
  1) `web` if installed
  2) otherwise first installed translation

### Analytics

- `clible analytics reference "John 3:16-18" [-t ID] [--top N]`
- `clible analytics chapter John 3 [-t ID] [--top N]`
- `clible analytics book John [-t ID] [--top N]`
- `clible analytics compare "John 3:16-18" [--left ID] [--right ID]`

Notes:
- Stopword filtering is language-aware via `data/stopwords.json` (`en`, `fi`).
- `compare` accepts alias `fin17xx`/`fin-17xx`, resolving to `fin-1776` (or another
  installed `fin-17*` translation).

---

## Database and Search Model

### Main schema (migration `002_seed_architecture.sql`)

- `books`: canonical metadata for 66 books
- `translations`: installed translation metadata
- `verses`: verse text rows with uniqueness on `(translation_id, book_id, chapter, verse)`

### Full-text search (migration `003_add_verse_fts.sql`)

- `verses_fts` (FTS5 virtual table) indexes `verses.text`
- Triggers keep index synchronized on insert/update/delete

Current usage:
- Repository/service search codepaths exist (`VerseRepo.search_text`,
  `VerseService.search_text`, `AnalyticService.concordance`)
- No dedicated CLI command is wired yet

---

## Key Codepaths

- Seed install:
  `commands/seed.py -> SeedService.seed_translation -> parser.parse_file -> TranslationRepo.create + VerseRepo.save_verses`
- Verse lookup:
  `commands/verse.py -> VerseService.get_verses -> VerseRepo.get_verses_in_range`
- Analytics:
  `commands/analytics.py -> AnalyticService.analyze_*`
- Translation comparison:
  `commands/analytics.py::compare -> AnalyticService.compare_translations`

---

## Repository Map (high signal)

```
src/clible/
├── cli.py
├── commands/
│   ├── seed.py
│   ├── verse.py
│   └── analytics.py
├── db/
│   ├── connection.py
│   ├── migrations.py
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_seed_architecture.sql
│   │   └── 003_add_verse_fts.sql
│   ├── seed_books.py
│   └── repositories/
│       ├── book_repo.py
│       ├── translation_repo.py
│       └── verse_repo.py
├── parsers/
│   ├── usfx_parser.py
│   ├── osis_parser.py
│   ├── osis_book_map.py
│   └── beblia_parser.py
├── services/
│   ├── seed_service.py
│   ├── verse_service.py
│   └── analytic_service.py
└── data/
    ├── bible_structure.json
    ├── translations.json
    ├── stopwords.json
    └── progress_quotes.json
```

---

## Related Documents

- **README.md** — setup, command usage, troubleshooting
- **PLAN.md** — long-range implementation roadmap
