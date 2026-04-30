# refactor: remove duplicate parser paths and keep CombinedParser as single seed parser

This PR removes duplicate XML parser implementations and aligns runtime, tests, and docs around one parser path (`CombinedParser`) for seed workflows.

## Summary

- Removed parallel parser architecture (`factory` + per-format parser classes) to avoid dual maintenance of the same parsing rules.
- Kept `CombinedParser` as the single production parser for USFX, OSIS, BEBLIA, and ZEFANIA XML parsing.
- Updated parser package exports to expose `CombinedParser` instead of `create_parser`.
- Removed redundant parser-specific tests and retained parser coverage through `test_combined_parser`.
- Updated project documentation to reflect current parser architecture and file layout.

## Files added

- `pr_stories/pr-TBD-combined-parser-consolidation.md` — PR description for this change.

## Files modified

- `src/clible/parsers/__init__.py` — exports `CombinedParser` and `XMLParserProtocol`.
- `docs/PROJECT_OVERVIEW.md` — parser architecture and file map updated.
- `docs/internal_docs/PROJECT_OVERVIEW.md` — parser architecture and file map updated.
- `docs/internal_docs/CONTINUATION_GUIDE.md` — parser milestone updated to `CombinedParser`.

## Files removed

- `src/clible/parsers/factory.py`
- `src/clible/parsers/usfx_parser.py`
- `src/clible/parsers/osis_parser.py`
- `src/clible/parsers/beblia_parser.py`
- `src/clible/parsers/zefania_parser.py`
- `tests/test_parsers/test_factory.py`
- `tests/test_parsers/test_usfx_parser.py`
- `tests/test_parsers/test_osis_parser.py`
- `tests/test_parsers/test_beblia_parser.py`
- `tests/test_parsers/test_zefania_parser.py`

## Tests

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
```

- `uv run ruff check .` — passed
- `uv run ruff format --check .` — passed
- `uv run pytest -q` — **219 passed**
