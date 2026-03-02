# feat: implement Bible data seeding (offline-first)

Adds offline-first Bible data flow: seed translations from XML, then query verses locally without network calls.

## Summary

- **USFX parser** — Parses eng-web.usfx.xml (and other USFX files) into verse dicts. Handles book structure (`<book>`, `<c>`, `<v>`, `<ve/>`), strips footnotes, normalizes whitespace, supports verse ranges (e.g. `15-16` → verse 15).
- **SeedService** — Orchestrates download → parse → save. Loads catalog from `translations.json`, filters verses to canonical 66 books (skips apocrypha, maps NAM→NAH), bulk-inserts in a single transaction. Progress callback for CLI feedback.
- **VerseService** — Parses references ("John 3:16", "1 Corinthians 13:4") and fetches from local DB. Resolves book names via BookRepo (exact or search).
- **CLI** — `clible seed install web`, `clible seed list`, `clible seed available`, `clible seed remove web`; `clible verse "John 3:16"` with `-t`/`--translation` flag. Rich tables and panels.
- **VerseRepo** — `get_verse`, `get_verses`, `save_verses` (bulk with UUIDs). TranslationRepo extended with `create(commit=False)` for transactional seed.
- **Dependencies** — click, rich, requests; hatchling build with entry point `clible`.

## Files added

- `src/clible/parsers/usfx_parser.py`
- `src/clible/services/seed_service.py`, `verse_service.py`
- `src/clible/commands/seed.py`, `verse.py`
- `src/clible/cli.py`
- `src/clible/data/translations.json`, `progress_quotes.json`
- `tests/test_parsers/test_usfx_parser.py`
- `tests/test_services/test_seed_service.py`, `test_verse_service.py`
- `tests/test_cli/test_seed_commands.py`
- `tests/fixtures/sample.usfx.xml`, `sample_with_frt.usfx.xml`

## Files modified

- `src/clible/db/repositories/translation_repo.py` — `create(commit=False)` for seed transaction
- `src/clible/db/repositories/verse_repo.py` — (added if not present)
- `pyproject.toml` — deps, `[project.scripts]`, build-system, hatch wheel config
- `main.py` — delegates to `cli.main`
- `README.md` — installation, commands, config
- `docs/PROJECT_OVERVIEW.md` — current status, file map
- `.gitignore` — internal docs (CONTINUATION_GUIDE, AGENTS, SKILLS, reflections)

## Tests

- 66 tests. Repos, parsers, services, CLI. In-memory SQLite, mocked `requests.get` for seed.
- `uv run pytest -v` passes. `ruff check` clean.

## Usage

```bash
uv run clible seed install web
uv run clible verse "John 3:16"
```
