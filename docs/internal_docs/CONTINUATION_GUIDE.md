# clible v2 — Continuation Guide

**Last updated:** 2026-03-02

This guide helps you continue development after a break. It lists prioritized tasks, how to run things, and where to look.

---

## Quick Start (After a Break)

```bash
cd /home/vivaldev/code/clible-v2
uv sync --all-groups
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

If tests pass and lint is clean, you are ready to continue.

---

## Recommended Order of Work

Follow the seed implementation plan. Each step builds on the previous one.

### 1. ~~Add missing repo tests~~ ✅ Done

**Why:** TranslationRepo and BookRepo have no tests. This violates project rules and risks regressions.

**Tasks:**
- Create `tests/test_db/test_translation_repo.py` — test get_all, get_by_id, exists, create, delete, get_default
- Create `tests/test_db/test_book_repo.py` — test get_all, get_by_id, get_by_name, search
- Add `conftest.py` with `db_conn` and repo fixtures (in-memory SQLite + app migrations)

**Reference:** AGENTS.md testing conventions; use `get_connection(":memory:")` so migrations run.

---

### 2. ~~VerseRepo~~ ✅ Done

**Why:** Core for storing and retrieving verses. Seed flow depends on it.

**Location:** `src/clible/db/repositories/verse_repo.py` (create new)

**Required methods:**
- `get_verse(translation_id, book_id, chapter, verse) -> dict | None`
- `get_verses(translation_id, book_id, chapter) -> list[dict]`
- `save_verses(verses: list[dict]) -> int` — bulk insert, returns count

**Verse dict shape:** `{id, translation_id, book_id, chapter, verse, text}`

**Tests:** `tests/test_db/test_verse_repo.py`

**See:** `notes/seed-implementation-plan.md` lines 175–185

---

### 3. ~~Data files~~ ✅ Done

**Why:** SeedService needs metadata for downloads and progress display.

**Create:**
- `src/clible/data/translations.json` — Catalog: web, kjv, fin-biblia with `name`, `language`, `format`, `filename`, `url`, `size_mb`
- `src/clible/data/progress_quotes.json` — Array of `{text, reference}` for seed progress

**Structure:** See `notes/seed-implementation-plan.md` lines 115–147

---

### 4. ~~Combined XML parser~~ ✅ Done

**Why:** Converts all supported XML formats to verse dicts for bulk insert with one parser path.

**Create:**
- `src/clible/parsers/__init__.py`
- `src/clible/parsers/combined_parser.py` — `CombinedParser.parse_file(xml_path) -> list[dict]`
- `src/clible/parsers/osis_book_map.py` — OSIS book-code normalization map
- `tests/fixtures/sample.usfx.xml` — Minimal John 1:1-5 for tests
- `tests/test_parsers/test_combined_parser.py`

**Output shape:** `{book_id, chapter, verse, text}` (book_id = GEN, JHN, etc.)

**Implementation:** Use `xml.etree.ElementTree` (stdlib). Detect root format and parse USFX/OSIS/BEBLIA/ZEFANIA to `{book_id, chapter, verse, text}`. Skip non-canonical content and inline note/reference text when needed.

**Reference:** `src/clible/data/eng-web.usfx.xml` — structure: `<book id="GEN">`, `<c id="1"/>`, `<v id="1"/>` with text before `<ve/>`

---

### 5. ~~SeedService~~ ✅ Done

**Why:** Orchestrates download → parse → save.

**Create:**
- `src/clible/services/seed_service.py`
- `tests/test_services/test_seed_service.py`

**Constructor:** `SeedService(translation_repo, verse_repo, book_repo, parser)`

**Methods:**
- `seed_translation(translation_id) -> dict` — stats
- `list_available() -> list[dict]`
- `list_installed() -> list[dict]`
- `remove_translation(translation_id)`

**Flow:** Load from translations.json → download XML (requests) → parse → transaction: insert translation + bulk save_verses.

**Dependencies:** Add `requests` to pyproject.toml when implementing.

---

### 6. ~~CLI entry point and seed commands~~ ✅ Done

**Why:** User-facing interface.

**Tasks:**
- Add `click`, `rich` to pyproject.toml
- Create `src/clible/cli.py` — main group, `seed` subcommand group
- Create `src/clible/commands/seed.py` — install, list, available, remove
- Configure entry point in pyproject.toml: `clible = clible.cli:main` (or similar)
- Remove or replace `main.py` placeholder

**Target:** `clible seed install web`, `clible seed list`, etc.

---

### 7. ~~Integration and polish~~ ✅ Done

- End-to-end: seed → fetch verse from local DB
- Add progress bar with Rich during seed
- Add `--translation` to fetch commands when they exist
- Update README with installation and usage

---

## Commands Cheat Sheet

| Action | Command |
|--------|---------|
| Run tests | `uv run pytest -v` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Lint + format check | `uv run ruff check . && uv run ruff format --check .` |
| Install deps | `uv sync --all-groups` |

---

## Important Files to Re-read

When resuming work, read these first:

1. **docs/PROJECT_OVERVIEW.md** — Current status and file map
2. **notes/seed-implementation-plan.md** (first ~200 lines) — Architecture and component specs
3. **notes/seed-where-we-are.md** — Quick status (update it as you progress)
4. **AGENTS.md** — Architecture boundaries, testing rules
5. **.cursorrules** — Critical rules (tests mandatory, no AI hints, follow plan)

---

## Decision Log

| Decision | Rationale |
|----------|-----------|
| Offline-first | No API dependency; faster, works offline |
| USFX first | Simplest XML format; covers WEB |
| WEB default | Public domain, lingua generalis |
| books from JSON | Static data; no migration needed for 66 books |
| Separate test migrations | Tests independent of app schema evolution |

---

## When Stuck

1. Check `notes/seed-implementation-plan.md` for the component spec
2. Look at `TranslationRepo` and `BookRepo` as reference implementations
3. Run tests after each small change
4. One logical commit per ticket
5. If a task feels too big, split it into smaller steps
