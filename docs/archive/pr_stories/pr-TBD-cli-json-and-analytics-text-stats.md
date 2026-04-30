# feat: JSON bridge for CLI and richer text analytics

This PR prepares the **Python CLI** for a subprocess bridge (stdout JSON only): `clible seed list --json`, and consistent `--json` output for verse, search, and analytics commands. It also extends **text analytics** with character count and average word length, with reference scope aligned to resolved verses.

Merge **before** the clible-web + Docker PR that spawns `clible` with `--json`, or rebase the web branch onto `main` after this merges.

## Summary

- **CLI:** `clible seed list --json` prints installed translations as JSON (id, name, language, format).
- **CLI:** For `--json` on verse, search, and analytics, print the export JSON string directly (avoid `json.loads` + `print` round-trip).
- **CLI:** Rename stdlib `json` import to `json_stdlib` in `analytics.py` where it conflicts with the `--json` flag name.
- **Analytics:** `AnalyticService` adds `character_count` and `avg_word_length` to reference/chapter/book stats; reference tokenization uses `get_verses` scope.
- **Export:** Analysis JSON includes new fields where applicable.
- **Tests:** `tests/test_cli/test_seed_commands.py` (seed list JSON); `tests/test_services/test_analytic_service.py` (new metrics).

## Files added

- None (unless your branch adds new test fixtures).

## Files modified

- `src/clible/commands/seed.py` — `--json` on `list`.
- `src/clible/commands/verse.py`, `search.py`, `analytics.py` — raw JSON stdout; import alias in analytics command.
- `src/clible/services/analytic_service.py` — metrics and verse-aligned reference stats.
- `src/clible/ui/export/analysis.py` — JSON payload fields.
- `tests/test_cli/test_seed_commands.py`, `tests/test_services/test_analytic_service.py`.

## Tests

`uv run pytest -v` — update **N** before merge; all passing.

`uv run ruff check .` and `uv run ruff format --check .` — clean.

## Usage

```bash
uv run clible seed list --json
uv run clible verse "John 3:16" --json
uv run clible search grace --json
uv run clible analytics reference "John 1:1" --json
```

## Notes

- Web UI and Docker are **out of scope** for this PR; they belong in a follow-up PR that depends on this behavior.

## Combining with other PRs

- You may merge the **docs-only** PR first, or squash the docs commit into this branch and use [`pr-TBD-combined-docs-and-python-cli-analytics.md`](pr-TBD-combined-docs-and-python-cli-analytics.md) as the PR description.
