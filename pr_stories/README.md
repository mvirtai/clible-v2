# PR stories

Version-controlled copies of **GitHub pull request descriptions** for clible-v2.

## Format

Follow **Short Format** or **Long Format** in [`.cursor/rules/pr-templates.md`](../.cursor/rules/pr-templates.md). For routine PRs, Short Format (bullet list, no section headers) is enough.

The structured checklist in [`.cursor/rules/pr-stories.mdc`](../.cursor/rules/pr-stories.mdc) applies when you want sections (Summary, Files changed, Test plan).

<<<<<<< HEAD
**Fill-in template:** [`TEMPLATE_GOOD_PR_STORY.md`](TEMPLATE_GOOD_PR_STORY.md) — Short/Long skeleton, quality checklist, and merge reminders.

**Draft PR bodies (worktree stack):** ready to paste after review — split into three PRs or combine docs + Python using the combined file.

- [`pr-TBD-docs-pr-workflow-template.md`](pr-TBD-docs-pr-workflow-template.md) — docs only (PR A).
- [`pr-TBD-cli-json-and-analytics-text-stats.md`](pr-TBD-cli-json-and-analytics-text-stats.md) — Python CLI + analytics (PR B).
- [`pr-TBD-web-bridge-and-docker.md`](pr-TBD-web-bridge-and-docker.md) — clible-web + Docker (PR C; merge after B).
- [`pr-TBD-combined-docs-and-python-cli-analytics.md`](pr-TBD-combined-docs-and-python-cli-analytics.md) — optional single PR body if A + B are squashed together.

=======
>>>>>>> parent of 8b09888 (docs: add PR story template and workflow notes)
## Naming

- Preferred: `pr-<github-pr-number>-<short-slug>.md` (example: [`pr-34-migration-004-drop-verses-text-index.md`](pr-34-migration-004-drop-verses-text-index.md)).
- If the PR is not opened yet: `<slug>.md` or `pr-TBD-<slug>.md`; rename to include the PR number after `gh pr create`.

## Workflow

1. Implement the branch.
2. Write the PR body using the template; save it in this directory.
3. Paste the same content into the GitHub PR description when opening the PR.
