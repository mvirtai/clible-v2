# PR: Analytics output formats (`--output`)

## Summary

- Added `--output PATH` to all `clible analytics` subcommands: `reference`, `chapter`, `book`, and `compare`.
- Output format is inferred from the file extension: `.json`, `.csv`, `.html`, or `.md` (case-insensitive).
- When exporting succeeds, the CLI prints a green terminal message with the resolved output path and chosen format.

## What changed

- `clible analytics` now branches on `--output`:
  - Without `--output`, the existing Rich tables remain unchanged.
  - With `--output`, results are serialized and written to the requested file format.
- New export module:
  - `src/clible/ui/analytics_export.py` converts analytics result dicts into the supported text formats.
- Updated CLI help text:
  - `src/clible/ui/help_texts.py` documents the new `--output` option for analytics commands.
- Added/extended CLI integration tests:
  - `tests/test_cli/test_analytics_commands.py` verifies file creation and basic format markers for JSON/CSV/MD/HTML, plus a negative test for unsupported extensions.

## How to test locally

- Quality gates:
  - `uv run ruff check .`
  - `uv run pytest -v` — **183 tests**, all passing.

## Usage

```bash
# Analysis (token metrics + top words/bigrams/trigrams)
uv run clible analytics reference "John 3:16" -t fin-1992 --output out.json
uv run clible analytics reference "John 3:16" -t fin-1992 --output out.csv
uv run clible analytics reference "John 3:16" -t fin-1992 --output out.md
uv run clible analytics reference "John 3:16" -t fin-1992 --output out.html

# Comparison (aligned verses + similarity summary)
uv run clible analytics compare "John 3:16-17" --left fin-1992 --right fin-1776 --output out.html
```

## Why this matters

- Makes `clible analytics` results easy to integrate with other tools and workflows by enabling direct export to common interchange formats.
- Keeps the existing interactive Rich UX intact while providing deterministic file-based output when requested.
