# feat: add side-by-side Finnish translation comparison with diffs

Adds a new analytics command for comparing Finnish translations side-by-side:
`fin-1992` vs `fin17xx` (alias to `fin-1776`).

## Summary

- **New CLI command** — `clible analytics compare "<reference>"` renders two translations in parallel columns, plus a word-level diff column and per-verse similarity percentages.
- **Alias support** — `fin17xx` and `fin-17xx` are resolved to an installed `fin-1776` (or another installed `fin-17*` translation if present).
- **Similarity analytics** — Added service-level comparison logic that:
  - aligns verses by `(book_id, chapter, verse)`
  - computes per-verse similarity (sequence + token overlap)
  - reports exact match rate, average similarity, most similar verse, and top shared vocabulary
- **Error handling** — Clear CLI error messages for missing translations, empty compare results, and invalid same-translation comparisons.
- **Docs update** — README now includes examples for the new compare command.

## Files added

- `tests/test_cli/test_analytics_commands.py` — CLI integration tests for `analytics compare` success and failure paths.

## Files modified

- `src/clible/commands/analytics.py`
  - Added `compare` command
  - Added translation alias resolver for `fin17xx`
  - Added side-by-side rendering and word-level diff visualization
  - Added similarity summary panel output
- `src/clible/services/analytic_service.py`
  - Added `compare_translations(reference, translation_a, translation_b)`
  - Added verse alignment helper and token-overlap helper
  - Added aggregate similarity summary generation
- `src/clible/cli.py`
  - Registered new command: `analytics compare`
- `tests/test_services/test_analytic_service.py`
  - Added tests for compare summary metrics, missing verse alignment, and empty result handling
- `README.md`
  - Added `analytics compare` usage examples and output description

## Tests

- `uv run pytest tests/test_services/test_analytic_service.py tests/test_cli/test_analytics_commands.py -v`
- `uv run ruff check src/clible/services/analytic_service.py src/clible/commands/analytics.py src/clible/cli.py tests/test_services/test_analytic_service.py tests/test_cli/test_analytics_commands.py`
- `uv run ruff format --check src/clible/services/analytic_service.py src/clible/commands/analytics.py src/clible/cli.py tests/test_services/test_analytic_service.py tests/test_cli/test_analytics_commands.py`

## Usage

```bash
# Default compare target:
# left=fin-1992, right=fin17xx (alias to fin-1776)
uv run clible analytics compare "John 3:16-18"

# Explicit compare translations
uv run clible analytics compare "Psalm 23:1-4" --left fin-1992 --right fin17xx
```
