# docs + feat: PR workflow template, JSON CLI bridge, and analytics metrics

Use this **single PR body** when you squash **documentation** (`pr_stories` template + README workflow) and **Python** changes (CLI `--json`, analytics metrics) into **one pull request** to reduce PR count. If you prefer three separate PRs, use [`pr-TBD-docs-pr-workflow-template.md`](pr-TBD-docs-pr-workflow-template.md) and [`pr-TBD-cli-json-and-analytics-text-stats.md`](pr-TBD-cli-json-and-analytics-text-stats.md) instead.

## Summary

### Documentation

- Add [`pr_stories/TEMPLATE_GOOD_PR_STORY.md`](TEMPLATE_GOOD_PR_STORY.md) and extend [`pr_stories/README.md`](README.md) with template link, approval-before-push workflow, CI-before-merge, and link to [`notes/git.md`](../notes/git.md).

### CLI and analytics

- `clible seed list --json` for installed translations JSON.
- Verse, search, analytics `--json`: print export JSON string without re-parsing; `json_stdlib` alias in analytics command.
- `AnalyticService`: `character_count`, `avg_word_length`; reference stats via `get_verses` scope; export JSON updated.
- Tests: `tests/test_cli/test_seed_commands.py`, `tests/test_services/test_analytic_service.py`.

## Files added

- `pr_stories/TEMPLATE_GOOD_PR_STORY.md`
- (None else unless your branch adds new modules.)

## Files modified

- `pr_stories/README.md`
- `src/clible/commands/seed.py`, `verse.py`, `search.py`, `analytics.py`
- `src/clible/services/analytic_service.py`, `src/clible/ui/export/analysis.py`
- `tests/test_cli/test_seed_commands.py`, `tests/test_services/test_analytic_service.py`

## Tests

`uv run pytest -v` — **N tests**, all passing (fill N before merge).

`uv run ruff check .` and `uv run ruff format --check .` — clean.

## Usage

```bash
uv run clible seed list --json
uv run clible analytics reference "John 1:1" --json
```

## Notes

- The **web + Docker** PR still depends on this behavior; open it after this merges (or rebase the web branch).
