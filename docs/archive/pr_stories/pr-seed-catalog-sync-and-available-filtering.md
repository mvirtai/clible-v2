# feat: sync translation catalog and filter `seed available`

This PR makes it possible to discover *all* supported Bible translation sources (USFX/OSIS/BEBLIA/ZEFANIA) directly from upstream catalogs, and improves CLI UX when the catalog grows large by adding filtering and search to `clible seed available`.

## Summary

- **Catalog sync** — Adds a translation catalog sync service that discovers supported upstream XML files and merges them into `src/clible/data/translations.json`.
- **New CLI command** — Introduces `clible seed sync-catalog` to regenerate the local catalog from upstream.
- **Expanded catalog** — Updates `src/clible/data/translations.json` with the newly discovered set of translation IDs for the four supported formats.
- **Better UX** — Extends `clible seed available` with `--format`, `--language`, `--query`, `--limit`, and `--offset` so the user can quickly find the right translation.
- **Accurate sizes** — Populates `size_mb` from upstream GitHub blob metadata so the “Size (MB)” column in `clible seed available` is meaningful.

## Files added

- `src/clible/services/translation_catalog_sync.py` — Discovers upstream supported XML files and merges results into the local catalog.
- `tests/test_services/test_translation_catalog_sync.py` — Unit tests for format inference and catalog merge logic.

## Files modified

- `src/clible/commands/seed.py` — Adds filtering/pagination/search to `seed available`; adds `sync-catalog` command wiring.
- `src/clible/cli.py` — Registers the new `seed sync-catalog` subcommand.
- `src/clible/ui/help_texts.py` — Updates help for `seed available` with the new options.
- `src/clible/data/translations.json` — Synced catalog contents so `seed available` can list all supported formats.
- `README.md` — Mentions ZEFANIA support in the seed docs.
- `tests/test_cli/test_seed_commands.py` — Updates CLI tests to use deterministic filters (and adds a ZEFANIA-specific test).

## Tests

- `uv run pytest -v` — **208 tests**, all passing.
- Includes additional CLI coverage for `clible seed available` filtering (`--language`, default `--limit`, and `--offset` edge case).

## Usage

```bash
# Regenerate catalog from upstream (optional if you already have an up-to-date translations.json)
uv run clible seed sync-catalog

# List (default shows up to 50 after filtering)
uv run clible seed available

# Find only ZEFANIA translations
uv run clible seed available --format ZEFANIA --limit 0

# Search by ID or name
uv run clible seed available --query web --limit 0

# Language filter + pagination
uv run clible seed available --language fi --limit 50 --offset 0
```
