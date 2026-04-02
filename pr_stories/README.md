# PR stories

Version-controlled copies of **GitHub pull request descriptions** for clible-v2.

## Format

Follow **Short Format** or **Long Format** in [`.cursor/rules/pr-templates.md`](../.cursor/rules/pr-templates.md). For routine PRs, Short Format (bullet list, no section headers) is enough.

The structured checklist in [`.cursor/rules/pr-stories.mdc`](../.cursor/rules/pr-stories.mdc) applies when you want sections (Summary, Files changed, Test plan).

**Fill-in template:** [`TEMPLATE_GOOD_PR_STORY.md`](TEMPLATE_GOOD_PR_STORY.md) — Short/Long skeleton, quality checklist, and merge reminders.

**Draft PR bodies (worktree stack):** ready to paste after review — split into three PRs or combine docs + Python using the combined PR body file.

- [`pr-TBD-full-stack-single-pr.md`](pr-TBD-full-stack-single-pr.md) — **whole branch** (docs + CLI + analytics + web + Docker) in one PR description.
- [`pr-TBD-docs-pr-workflow-template.md`](pr-TBD-docs-pr-workflow-template.md) — docs only (PR A).
- [`pr-TBD-cli-json-and-analytics-text-stats.md`](pr-TBD-cli-json-and-analytics-text-stats.md) — Python CLI + analytics (PR B).
- [`pr-TBD-web-bridge-and-docker.md`](pr-TBD-web-bridge-and-docker.md) — clible-web + Docker (PR C; merge after B).
- [`pr-TBD-combined-docs-and-python-cli-analytics.md`](pr-TBD-combined-docs-and-python-cli-analytics.md) — combined PR body if A + B are squashed together.

## Naming

- Preferred: `pr-<github-pr-number>-<short-slug>.md` (example: [`pr-34-migration-004-drop-verses-text-index.md`](pr-34-migration-004-drop-verses-text-index.md)).
- If the PR is not opened yet: `<slug>.md` or `pr-TBD-<slug>.md`; rename to include the PR number after `gh pr create`.

## Workflow

1. Implement on a **topic branch** (one concern per PR). Commits: conventional, tests green locally (`uv run pytest -v`, ruff).
2. **Approve** proposed commit messages and PR story text (no push / no `gh pr create` until you approve).
3. Save the final story here; paste the same into GitHub when opening the PR.
4. **CI** must pass on GitHub before merge; **merge** is done by you on GitHub (e.g. squash-and-merge).

Multi-topic workflow (several PRs over time): see [`notes/git.md`](../notes/git.md) — section *Multi-topic commit and PR strategy*.
