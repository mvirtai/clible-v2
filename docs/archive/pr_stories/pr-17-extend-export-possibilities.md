# feat: extend exporting possibilities across verse, search, and analytics

This PR replaces and generalizes the previous analytics-only `--output` approach with a unified `--export` / `-exp` flag available on `verse`, `search`, and all `analytics` subcommands. It also adds `txt` and `xml` formats alongside the existing `csv`, `html`, `json`, and `md`.

## Summary

- Unified export syntax across commands: `--export "PATH=...,FILENAME=...,FORMAT=..."` (comma- or space-separated, case-insensitive keys).
- Supported formats: `csv`, `html`, `json`, `md`, `txt`, `xml`.
- Defaults when omitted: `PATH=.`, `FILENAME=export_YYYYMMDD_HHMMSS`, `FORMAT=md`.
- `analytics compare` HTML export matches the search export layout:
  - Centered verse titles with full book name and acronym reference (e.g. `Luke 1:3` + `(LUK 1:3)`).
  - No `Left` / `Right` labels in HTML (kept for terminal/text export only).
  - Translation IDs (e.g. `fin-1992`, `greek`) shown as small centered headers for each verse text.
- New UI modules:
  - `export_cli.py` — parses `--export` key=value pairs.
  - `analytics_export.py` — serializers for analytics/compare results.
  - `verse_search_export.py` — serializers for verse lookup and search results.
- Updated CLI commands to wire `--export` / `-exp`:
  - `verse.py` — single verse and range lookups.
  - `search.py` — full-text search with scope controls.
  - `analytics.py` — reference, chapter, book, and compare.
- Updated help text in `help_texts.py` for root CLI and all affected commands.
- Root CLI help now mentions export availability without duplicating format details.

## Files added

- `src/clible/ui/export_cli.py` — `--export` argument parsing and validation.
- `src/clible/ui/verse_search_export.py` — serializers for verse and search payloads.
- `tests/test_ui/test_export_cli.py` — unit tests for export parsing.
- `tests/test_ui/test_verse_search_export.py` — unit tests for verse/search serializers.
- `tests/test_ui/__init__.py` — package marker.

## Files modified

- `src/clible/ui/analytics_export.py` — added `txt` and `xml` serializers; aligned API with verse/search export.
- `src/clible/commands/verse.py` — added `-exp` / `--export` option and export branch.
- `src/clible/commands/search.py` — added `-exp` / `--export` option and export branch.
- `src/clible/commands/analytics.py` — replaced `--output` with `--export` and extended to all subcommands.
- `src/clible/ui/help_texts.py` — added export mention to root help; updated verse/search/analytics helps.
- `tests/test_cli/test_verse_commands.py` — added export integration tests.
- `tests/test_cli/test_search_commands.py` — added export integration tests.
- `tests/test_cli/test_analytics_commands.py` — updated for `--export` and added new format tests.
- `.gitignore` — added `outputs/` to ignore test export artifacts.

## Tests

Quality gates and test count:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -v  # 229 tests, all passing
```

## Usage

```bash
# Verse lookup exports
uv run clible verse "John 3:16" --export "FORMAT=json"
uv run clible verse "Genesis 1:1-5" --export "PATH=./out,FILENAME=genesis,FORMAT=txt"

# Search exports
uv run clible search grace --scope book --reference John --export "FORMAT=csv"
uv run clible search love --export "PATH=~/exports,FILENAME=love_search,FORMAT=html"

# Analytics exports (all subcommands)
uv run clible analytics reference "John 3:16" --export "FORMAT=xml"
uv run clible analytics chapter John 3 --export "FORMAT=md"
uv run clible analytics book John --export "FORMAT=json"
uv run clible analytics compare "John 3:16" --left web --right kjv --export "FORMAT=html"

# Compact flag alias
uv run clible verse "Psalm 23:1" -exp "FILENAME=ps23,FORMAT=md"
```
