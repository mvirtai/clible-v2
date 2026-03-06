# clible v2 — Project Overview

**Last updated:** 2026-03-06

This document summarizes current architecture, public CLI interfaces, and operational guidance for developers.

---

## What Is clible?

clible is an offline-first command-line Bible study tool.

Core behavior:

- Install translations from XML catalogs (`seed install`)
- Query local verses (`verse`)
- Run text analytics and translation comparison (`analytics`)

After seeding, normal verse/analytics usage is local SQLite reads.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│ CLI Layer (Click + Rich)                                          │
│   cli.py, commands/seed.py, commands/verse.py, commands/analytics.py │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ Service Layer                                                      │
│   SeedService   VerseService   AnalyticService                     │
└──────────────┬──────────────────────────┬──────────────────────────┘
               │                          │
┌──────────────▼──────────────┐  ┌────────▼─────────────────────────┐
│ Repositories                │  │ Parsers                          │
│ TranslationRepo             │  │ USFXParser                       │
│ BookRepo                    │  │ OSISParser                       │
│ VerseRepo                   │  │ BebliaParser                     │
└──────────────┬──────────────┘  └──────────────────────────────────┘
               │
┌──────────────▼─────────────────────────────────────────────────────┐
│ SQLite (books, translations, verses, verses_fts)                  │
└────────────────────────────────────────────────────────────────────┘
```

Layer rule: CLI calls services; services coordinate repositories/parsers; repositories only access SQLite.

---

## Public CLI Interface (current)

| Area | Command | Purpose |
|------|---------|---------|
| Translations | `clible seed available` | List catalog translations |
| Translations | `clible seed install <id>` | Download + parse + persist translation |
| Translations | `clible seed list` | List installed translations |
| Translations | `clible seed remove <id>` | Uninstall translation (verses cascade) |
| Verse lookup | `clible verse "John 3:16"` | Single verse lookup |
| Verse lookup | `clible verse "John 3:1-6"` | Inclusive verse range in one chapter |
| Analytics | `clible analytics reference "<ref>"` | Analyze one verse/range reference |
| Analytics | `clible analytics chapter <Book> <chapter>` | Analyze chapter tokens/n-grams |
| Analytics | `clible analytics book <Book>` | Analyze whole book |
| Comparison | `clible analytics compare "<ref>"` | Side-by-side translation diff + similarity |

### Important interface constraints

- Reference parser accepts:
  - `"Book Chapter:Verse"`
  - `"Book Chapter:Start-End"` (same chapter)
- Default translation resolution when `-t/--translation` is omitted:
  1) use `web` if installed, else
  2) first installed translation (`installed_at`)
- `analytics compare` default pair is `--left fin-1992 --right fin17xx`
  - `fin17xx` is an alias resolved to `fin-1776` (or another installed `fin-17*`)

---

## Current Implementation Status

### Done ✅

| Component | Location | Notes |
|-----------|----------|-------|
| Config | `src/clible/config.py` | Env overrides (`CLIBLE_DB_PATH`, `CLIBLE_DATA_DIR`) |
| DB connection | `src/clible/db/connection.py` | WAL, foreign keys, row factory, migrations, seed books |
| Migrations | `src/clible/db/migrations.py` + `db/migrations/*.sql` | Ordered SQL + `_migrations` tracking |
| Verse FTS index | `003_add_verse_fts.sql` | FTS5 table + sync triggers for inserts/updates/deletes |
| Repositories | `src/clible/db/repositories/` | TranslationRepo, BookRepo, VerseRepo |
| Parsers | `src/clible/parsers/` | USFX, OSIS, BEBLIA support |
| Seed service | `src/clible/services/seed_service.py` | Catalog list/install/remove with parser selection by format |
| Verse service | `src/clible/services/verse_service.py` | Single verse + range + chapter + book retrieval |
| Analytics service | `src/clible/services/analytic_service.py` | Token stats, n-grams, concordance, translation comparison |
| CLI commands | `src/clible/commands/` | `seed`, `verse`, `analytics` groups |
| Data files | `src/clible/data/` | bible structure, translation catalog, stopwords |
| Tests | `tests/` | Repository/service/CLI coverage with temporary or in-memory SQLite |

### Planned / partial

| Area | Status |
|------|--------|
| CLI search command | FTS exists in repository/service, dedicated CLI command not exposed |
| Export workflows | Not implemented yet |
| Session workflows | Not implemented yet |

---

## Operational Runbooks

### Bootstrap a new local environment

```bash
uv sync
uv run clible seed available
uv run clible seed install web
uv run clible verse "John 3:16"
```

### Enable Finnish comparison workflow

```bash
uv run clible seed install fin-1992
uv run clible seed install fin-1776
uv run clible analytics compare "John 3:16-18"
```

### Use an isolated database (safe experiments)

```bash
export CLIBLE_DB_PATH=/tmp/clible-dev.db
uv run clible seed install web
uv run clible verse "John 1:1"
```

---

## Troubleshooting and Common Pitfalls

- **Comparison failed: missing translations**
  - Install missing IDs first (`fin-1992`, `fin-1776` for default compare flow).
- **Verse(s) not found**
  - Validate reference format and ensure translation is installed (`clible seed list`).
- **Unknown translation during install**
  - Use IDs shown by `clible seed available`.
- **Unexpected translation used without `-t`**
  - Remember default selection prefers `web`; otherwise first installed translation.

---

## File Map

```
clible-v2/
├── src/clible/
│   ├── cli.py
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
│   │   ├── seed_books.py
│   │   └── repositories/
│   │       ├── translation_repo.py
│   │       ├── book_repo.py
│   │       └── verse_repo.py
│   ├── parsers/
│   │   ├── usfx_parser.py
│   │   ├── osis_parser.py
│   │   ├── osis_book_map.py
│   │   └── beblia_parser.py
│   ├── services/
│   │   ├── seed_service.py
│   │   ├── verse_service.py
│   │   └── analytic_service.py
│   └── data/
│       ├── bible_structure.json
│       ├── translations.json
│       ├── stopwords.json
│       └── progress_quotes.json
├── tests/
├── docs/
│   └── PROJECT_OVERVIEW.md
├── README.md
└── pyproject.toml
```

---

## Database Schema Notes

Main tables:

- `books` — canonical 66-book metadata
- `translations` — installed translation metadata
- `verses` — verse text rows (`UNIQUE(translation_id, book_id, chapter, verse)`)

Search indexing:

- `verses_fts` (FTS5 virtual table)
- Triggers keep FTS index synchronized on insert/update/delete

---

## Related Documents

- **README.md** — Setup, usage, quick workflows
- **PLAN.md** — Long-range roadmap (some items superseded by offline seed implementation)
