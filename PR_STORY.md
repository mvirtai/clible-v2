# feat: support verse ranges in verse command (multi-verse lookup)

Extends verse search so a single reference can return multiple consecutive verses from the same chapter. Builds on the existing verse lookup added in the previous PR (Bible data seeding / offline-first).

## Summary

- **Reference parsing** — `_parse_reference` now supports both single verses and ranges, e.g. `"John 3:16"`, `"John 3:16-18"`, `"John 3:1-6"`. It normalizes whitespace, validates `end >= start`, and returns `(book_name, chapter, verse_start, verse_end)`; invalid or reversed ranges return `None`.
- **VerseRepo** — New `get_verses_in_range(translation_id, book_id, chapter, verse_start, verse_end)` encapsulates the SQL for inclusive verse ranges, returning plain dicts ordered by verse number.
- **VerseService** — Keeps `get_verse(reference, translation_id)` for single-verse callers and adds `get_verses(reference, translation_id)` returning a list (length 1 for single reference, N for a range). Both share the same parsing and book/translation resolution.
- **CLI** — The `verse` command uses `get_verses` and renders each verse in its own Rich `Panel`. Single references show one panel; ranges show multiple panels in order.

## Files added

- `tests/test_cli/test_verse_commands.py` — CLI integration tests for the verse command, including range behavior.

## Files modified

- `src/clible/services/verse_service.py` — Extended `_REFERENCE_PATTERN` and `_parse_reference` for ranges; added `get_verses`; refactored book lookup (exact name then `search()` without duplicate calls).
- `src/clible/db/repositories/verse_repo.py` — Added `get_verses_in_range`; `get_verse` and `get_verses` unchanged as pure DB helpers.
- `src/clible/commands/verse.py` — Uses `get_verses`, updated help and error message for ranges; iterates over verses when rendering panels.
- `tests/test_db/test_repositories/test_verse_repo.py` — Tests for `get_verses_in_range` (subset ordering, empty range).
- `tests/test_services/test_verse_service.py` — Tests for range parsing and `get_verses` (single vs range, invalid range, no translation).

## Tests

- `uv run pytest tests/test_db/test_repositories/test_verse_repo.py tests/test_services/test_verse_service.py tests/test_cli/test_verse_commands.py -v`
- Full suite: `uv run pytest -v` — **98 tests**, all passing.

## Usage

```bash
# Single verse (unchanged)
uv run clible verse "John 3:16" -t kjv

# Multi-verse range (new)
uv run clible verse "John 3:1-6" -t kjv
```
