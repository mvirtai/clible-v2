# docs: PR story template and workflow notes

This PR adds versioned guidance for writing PR descriptions and tightens the `pr_stories/` workflow (topic branch, approve messages and story before push, CI before merge). It does not change application behavior.

## Summary

- Extend [`pr_stories/README.md`](README.md): link to [`TEMPLATE_GOOD_PR_STORY.md`](TEMPLATE_GOOD_PR_STORY.md), approval gate, CI, merge on GitHub; pointer to [`notes/git.md`](../notes/git.md) multi-topic workflow.
- Add [`pr_stories/TEMPLATE_GOOD_PR_STORY.md`](TEMPLATE_GOOD_PR_STORY.md): short/long skeletons, quality checklist, post-merge rename hint.

## Files added

- `pr_stories/TEMPLATE_GOOD_PR_STORY.md` — Fill-in template and checklist for PR bodies.

## Files modified

- `pr_stories/README.md` — Workflow steps and template link.

## Tests

Not applicable (documentation only).

`uv run pytest -v` — unchanged behavior; run to confirm no accidental code changes on the branch.

`uv run ruff check .` and `uv run ruff format --check .` — clean.

## Combining with other PRs

If you prefer **fewer PRs**, squash the docs commit into the same branch as the **Python CLI + analytics** PR and use [`pr-TBD-combined-docs-and-python-cli-analytics.md`](pr-TBD-combined-docs-and-python-cli-analytics.md) as the single PR body instead of opening this PR separately.

## Usage

N/A
