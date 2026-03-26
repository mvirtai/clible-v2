# PR stories

Version-controlled copies of **GitHub pull request descriptions** for clible-v2.

## Format

Follow **Short Format** or **Long Format** in [`.cursor/rules/pr-templates.md`](../.cursor/rules/pr-templates.md). For routine PRs, Short Format (bullet list, no section headers) is enough.

The structured checklist in [`.cursor/rules/pr-stories.mdc`](../.cursor/rules/pr-stories.mdc) applies when you want sections (Summary, Files changed, Test plan).

## Naming

- Preferred: `pr-<github-pr-number>-<short-slug>.md` (example: `pr-34-migration-004-drop-verses-text-index.md`).
- If the PR is not opened yet: `<slug>.md` or `pr-TBD-<slug>.md`; rename when the PR number is known.

## Workflow

1. Implement the branch.
2. Write the PR body using the template; save it in this directory.
3. Paste the same content into the GitHub PR description when opening the PR.
