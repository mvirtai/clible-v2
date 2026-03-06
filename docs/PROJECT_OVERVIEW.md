# clible v2 — Project Overview

**Last updated:** 2026-03-06

This document describes what is currently implemented in clible v2, where each
subsystem lives, and how the main developer workflows operate.

---

## What Is clible?

clible is a command-line Bible study tool with an offline-first architecture:

- Seed Bible translations from XML sources (USFX, OSIS, BEBLIA)
- Store normalized verse data in SQLite
- Query verses and run text analytics locally

No API calls are needed for verse lookup or analytics after seeding.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│ UI Layer (Click + Rich)                                             │
│   cli.py, commands/seed.py, commands/verse.py, commands/analytics.py │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│ Service Layer                                                        │
│   SeedService, VerseService, AnalyticService                         │
└───────────────┬──────────────────────────────┬───────────────────────┘
                │                              │
┌───────────────▼───────────────┐  ┌───────────▼──────────────────────┐
│ Repositories                  │  │ Parsers                           │
│   TranslationRepo             │  │   USFXParser                      │
│   BookRepo                    │  │   OSISParser                      │
│   VerseRepo                   │  │   BebliaParser                    │
└───────────────┬───────────────┘  └───────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────────────┐
│ SQLite                                                               │
│   books, translations, verses, verses_fts (FTS5), _migrations        │
└───────────────────────────────────────────────────────────────────────┘
```

Layer boundaries are enforced by design:

- UI calls services only
- Services orchestrate repositories/parsers
- Repositories contain SQL only

---

## Current Implementation Status

### Implemented

| Subsystem | Location | Notes |
|-----------|----------|-------|
| Configuration | `src/clible/config.py` | `Config` dataclass + `CLIBLE_*` overrides |
| DB connection | `src/clible/db/connection.py` | WAL mode, FK enforcement, row factory, migrations |
| Migration runner | `src/clible/db/migrations.py` | Ordered SQL execution with `_migrations` tracking |
| Schema migration | `src/clible/db/migrations/002_seed_architecture.sql` | `books`, `translations`, `verses` |
| FTS migration | `src/clible/db/migrations/003_add_verse_fts.sql` | `verses_fts` + insert/update/delete triggers |
| Book seeding | `src/clible/db/seed_books.py` | Seeds `books` from `bible_structure.json` |
| Repositories | `src/clible/db/repositories/` | `BookRepo`, `TranslationRepo`, `VerseRepo` |
| Parsers | `src/clible/parsers/` | USFX, OSIS (including milestone handling), BEBLIA |
| Seed service | `src/clible/services/seed_service.py` | Download → parse → persist translation data |
| Verse service | `src/clible/services/verse_service.py` | Single verse and same-chapter range lookup |
| Analytics service | `src/clible/services/analytic_service.py` | Token metrics, n-grams, concordance, translation compare |
| CLI commands | `src/clible/cli.py`, `src/clible/commands/` | `seed`, `verse`, `analytics` command groups |
| Static data | `src/clible/data/` | `bible_structure.json`, `translations.json`, `stopwords.json`, `progress_quotes.json` |
| Tests | `tests/` | Repository, parser, service, and CLI coverage |
| CI | `.github/workflows/ci.yml` | Ruff + pytest |

### Not implemented yet (from long-term plan)

- Export workflows (markdown/text files)
- Session management workflows
- CLI command surface for full-text concordance/search (service exists, dedicated command not present)

---

## Public CLI Interfaces

### Translation lifecycle

```bash
clible seed available
clible seed install web
clible seed list
clible seed remove web
```

### Verse lookup

```bash
clible verse "John 3:16"
clible verse "John 3:1-6" -t kjv
```

Reference format is:

- single verse: `Book Chapter:Verse`
- same-chapter range: `Book Chapter:Start-End`

### Analytics

```bash
clible analytics reference "John 3:16-18" --top 5
clible analytics chapter John 3
clible analytics book Genesis -t kjv
clible analytics compare "John 3:16-18" --left fin-1992 --right fin17xx
```

`analytics compare` defaults to `--left fin-1992 --right fin17xx`.
`fin17xx` resolves to `fin-1776` (or another installed `fin-17*` translation).

---

## Operational Workflows (Runbook)

### 1. Bootstrap a local DB

```bash
uv sync
uv run clible seed install web
uv run clible seed list
```

### 2. Install Finnish pair for comparison

```bash
uv run clible seed install fin-1992
uv run clible seed install fin-1776
```

### 3. Validate lookup + analytics

```bash
uv run clible verse "John 3:16"
uv run clible analytics reference "John 3:16-18"
uv run clible analytics compare "John 3:16-18"
```

### 4. Remove translation safely

```bash
uv run clible seed remove fin-1776
```

This deletes the translation row and cascades related verses.

---

## File Map

```
clible-v2/
├── src/clible/
│   ├── cli.py
│   ├── config.py
│   ├── commands/
│   │   ├── analytics.py
│   │   ├── seed.py
│   │   └── verse.py
│   ├── db/
│   │   ├── connection.py
│   │   ├── migrations.py
│   │   ├── seed_books.py
│   │   ├── migrations/
│   │   │   ├── 001_initial_schema.sql
│   │   │   ├── 002_seed_architecture.sql
│   │   │   └── 003_add_verse_fts.sql
│   │   └── repositories/
│   │       ├── book_repo.py
│   │       ├── translation_repo.py
│   │       └── verse_repo.py
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
│       ├── progress_quotes.json
│       ├── stopwords.json
│       └── translations.json
├── tests/
│   ├── conftest.py
│   ├── test_cli/
│   ├── test_data/
│   ├── test_db/
│   ├── test_parsers/
│   └── test_services/
├── docs/
│   └── PROJECT_OVERVIEW.md
├── Dockerfile
├── Taskfile.yml
└── pyproject.toml
```

---

## Database Notes

### `books`

Static canonical metadata loaded from `bible_structure.json`.

### `translations`

Installed translation metadata (`id`, `name`, `language`, `format`, `source_url`, `installed_at`).

### `verses`

Normalized verse text with unique key:

`UNIQUE(translation_id, book_id, chapter, verse)`

### `verses_fts` (FTS5 virtual table)

Full-text index for verse text search. Triggers keep FTS rows synchronized on:

- INSERT (`verses_ai`)
- UPDATE (`verses_au`)
- DELETE (`verses_ad`)

---

## Known Constraints and Pitfalls

- Verse range syntax supports a single chapter only (e.g. `John 3:1-6`).
- `analytics compare` requires both translations installed before execution.
- If no translation is passed, default resolution is:
  1. `web` if installed
  2. first installed translation by `installed_at`

---

## Related Documents

- [README.md](../README.md) — user-facing setup, commands, troubleshooting
- [PLAN.md](../PLAN.md) — long-term implementation roadmap
