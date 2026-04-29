# fix(web): restore analytics bridge JSON flow and harden AI fallback

This PR fixes a web analytics regression where native analytics calls returned 500 due to a CLI option mismatch. It also improves resilience so missing AI configuration no longer breaks otherwise successful analytics results in the web UI.

## Summary

- Fixed `analytics chapter` and `analytics book` command option wiring by adding the missing `--stdout-export` click option, matching the function signatures and web bridge expectations.
- Preserved native analytics results in the web app when AI tone analysis is unavailable (`503` / missing `GEMINI_API_KEY`) by isolating AI tone into its own `try/catch`.
- Added regression tests for `analytics chapter --json` and `analytics book --json` to prevent future breakage in `/api/clible?cmd=analytics` web integration.
- Verified full project checks still pass after the fix.

## Files added

- No new files were added in this fix-focused PR.

## Files modified

- `src/clible/commands/analytics.py` - Added `--stdout-export` option decorators for `chapter` and `book` subcommands to align Click parsing with callback parameters.
- `src/clible-web/App.tsx` - Updated analytics flow to treat AI tone failure as non-fatal and keep native analytics charts/stats available.
- `tests/test_cli/test_analytics_commands.py` - Added JSON regression tests for chapter/book analytics subcommands used by web bridge.

## Tests

- `task check` - Passed (`ruff check`, `ruff format --check`, `pytest -v`).
- Full suite: **281 tests**, all passing.
- Coverage gate remains passing (>= 80%).

## Usage

```bash
# Reproduce native analytics output expected by web bridge
uv run clible analytics chapter "PSA" 1 --translation fin-1992 --top 10 --json

# Full project verification
task check
```
