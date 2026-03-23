# clible v2 — Project Overview

**Last updated:** 2026-03-23

This document summarizes the current, implemented architecture and workflows in
clible v2.

---

## What Is clible?

clible is an offline-first command-line Bible study tool. It downloads Bible
XML once, stores parsed verses in SQLite, and serves lookups/analytics locally.

Core goals:

- **Offline-first runtime** after seeding translations
- **Layered architecture** (UI → Services → Repositories → SQLite)
- **Testable design** with dependency injection and isolated service logic

---

## Architecture (current)

```
┌──────────────────────────────────────────────────────────────────────┐
│ UI Layer (Click + Rich)                                              │
│   cli.py, commands/seed.py, commands/verse.py, commands/analytics.py │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────┐
│ Service Layer                                                         │
│   SeedService   VerseService   AnalyticService                        │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────┐
│ Repository Layer                                                      │
│   TranslationRepo   BookRepo   VerseRepo                              │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────┐
│ SQLite                                                                │
│   books, translations, verses, verses_fts (FTS5)                      │
└───────────────────────────────────────────────────────────────────────┘
```

Parser layer used by seeding:

- `USFXParser` (WEB)
- `OSISParser` (KJV, fin-biblia-33-38)
- `BebliaParser` (fin-1992, fin-1776, fin-stlk)

Layer rule reminder: repositories only access SQLite; services orchestrate
business logic; CLI handles input/output only.

---

## Current Implementation Status

### Implemented ✅

| Area | Location | Notes |
|------|----------|-------|
| Config and env overrides | `src/clible/config.py` | `CLIBLE_DB_PATH`, `CLIBLE_DATA_DIR`, etc. |
| DB connection and migrations | `src/clible/db/connection.py`, `src/clible/db/migrations.py` | WAL + FK enabled, migration runner, book seeding |
| Schema migrations | `src/clible/db/migrations/*.sql` | Base schema + FTS5 virtual table/triggers |
| Repositories | `src/clible/db/repositories/` | `TranslationRepo`, `BookRepo`, `VerseRepo` |
| Seeding service | `src/clible/services/seed_service.py` | Catalog, download, parse, store, remove |
| Verse lookup service | `src/clible/services/verse_service.py` | Single verse + single-chapter ranges |
| Analytics service | `src/clible/services/analytic_service.py` | Tokens, n-grams, concordance, translation compare |
| CLI command groups | `src/clible/cli.py`, `src/clible/commands/` | `seed`, `verse`, `analytics` (reference/chapter/book/compare) |
| Data catalogs | `src/clible/data/` | `bible_structure.json`, `translations.json`, stopwords |
| Tests and CI | `tests/`, `.github/workflows/ci.yml` | Repo/service/CLI tests, pytest + ruff |
| Task automation | `Taskfile.yml`, `scripts/create_compare_pr.sh` | lint/test/check, docker tasks, compare PR helper |

### Not implemented yet

| Area | Notes |
|------|-------|
| Export workflows | Markdown/plain text export services and commands |
| Session workflows | Session management from original long-term plan |

---

## Public Interface Snapshot

### Main commands

- `clible seed available|install|list|remove`
- `clible verse "<Book Chapter:Verse|Start-End>" [-t <translation>]`
- `clible analytics reference|chapter|book ...`
- `clible analytics compare "<reference>" [--left <id>] [--right <id>]`

### Compare workflow specifics

- Default pair: `fin-1992` vs `fin17xx`
- `fin17xx` is an alias resolved by CLI to installed `fin-1776` (or first `fin-17*`)
- Fails fast when required translations are missing or both sides resolve to same ID
- Output includes side-by-side text, word-level diff markup, and similarity summary

---

## Database Schema Snapshot

### Base tables (`002_seed_architecture.sql`)

- **books**: canonical metadata (id, name, testament, position, chapters)
- **translations**: installed translation metadata
- **verses**: normalized verse rows with unique constraint on
  `(translation_id, book_id, chapter, verse)`

### Full-text search (`003_add_verse_fts.sql`)

- **verses_fts** virtual table (FTS5) linked to `verses`
- insert/update/delete triggers keep the FTS index synchronized
- used by `VerseRepo.search_text()` and `AnalyticService.concordance()`

---

## File Map (high-value paths)

```
src/clible/
├── cli.py
├── commands/
│   ├── seed.py
│   ├── verse.py
│   └── analytics.py
├── services/
│   ├── seed_service.py
│   ├── verse_service.py
│   └── analytic_service.py
├── db/
│   ├── connection.py
│   ├── migrations.py
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_seed_architecture.sql
│   │   └── 003_add_verse_fts.sql
│   └── repositories/
│       ├── translation_repo.py
│       ├── book_repo.py
│       └── verse_repo.py
├── parsers/
│   ├── usfx_parser.py
│   ├── osis_parser.py
│   ├── osis_book_map.py
│   └── beblia_parser.py
└── data/
    ├── bible_structure.json
    ├── translations.json
    └── stopwords.json
```

---

## Operational Notes

- Seed before lookup/analytics (`clible seed install <id>`).
- Verse references currently support one chapter at a time:
  `"John 3:16"` or `"John 3:16-18"`.
- For compare defaults, install both:
  - `clible seed install fin-1992`
  - `clible seed install fin-1776`
- For PR helper workflow, see README Task runbook (`task pr-compare ...`).

---

## Related Documents

- **README.md** — installation, command usage, troubleshooting, task runbooks
- **PLAN.md** — long-term roadmap (some future areas not implemented yet)
