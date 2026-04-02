# Template: good PR story (copy and replace placeholders)

Use this when creating **`pr_stories/pr-<n>-<slug>.md`** (or `pr-TBD-<slug>.md` before the PR exists). Paste the **same** content into the GitHub PR description after you approve it.

Pick **Short** or **Long** below; Short is enough for routine PRs. See also [`.cursor/rules/pr-templates.md`](../.cursor/rules/pr-templates.md) and [`.cursor/rules/pr-stories.mdc`](../.cursor/rules/pr-stories.mdc).

---

## Option A — Short format (routine PR)

Replace the bullets with real paths and behavior. No section headers required.

```markdown
- <One clear bullet per logical change; mention area, e.g. service vs CLI.>
- <New or changed tests (file path).>
- <Docs or config only if touched.>
```

**Example (filled):**

- Extended verse reference parsing to allow optional end verse (`John 3:16-18`) in `verse_service.py`.
- `get_verses(...)` returns an ordered list; CLI prints each verse in `commands/verse.py`.
- Tests: range, single verse unchanged, invalid range (`tests/test_services/test_verse_service.py`, CLI tests).

---

## Option B — Long format (release, architecture, or reviewers need context)

```markdown
# feat: <short summary in imperative mood>

<One or two sentences: what this PR does and what it builds on (prior PR, ticket, or main).>

## Summary

- <Main change 1 — repos / services / parsers / CLI as applicable>
- <Main change 2>
- <Tests and tooling (pytest, ruff)>

## Files added

- `<path>` — <one line>
- `<path>` — <one line>

## Files modified

- `<path>` — <what changed>
- `<path>` — <what changed>

## Tests

`uv run pytest -v` — **N tests**, all passing (update N before merge).

`uv run ruff check .` and `uv run ruff format --check .` — clean.

## Usage (optional)

```bash
uv run clible <command> "<example>"
```

## Notes (optional)

- <Follow-ups, caveats, or out-of-scope items for a later PR.>
```

---

## Quality checklist (before you approve and push)

- [ ] Title line uses **Conventional Commits** (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, …).
- [ ] Summary matches the **actual diff** (no copy-paste drift).
- [ ] New files and important edits are **named** so a reviewer can skim.
- [ ] **Tests** section states how to run them and that they pass locally; update counts when final.
- [ ] **CI** on GitHub is green before merge; red CI is not “good enough to merge”.
- [ ] No merge strategy text that contradicts repo policy (clible-v2: **Squash and merge** is typical); **you** perform merge on GitHub.
- [ ] Professional tone; no tooling/vendor meta in the body (same as commits).

---

## After merge

Rename file if needed: `pr-TBD-<slug>.md` → `pr-<github-pr-number>-<slug>.md`. Delete the remote branch and sync local `main` per `notes/git.md` / `.cursor/rules/git-commits.mdc`.
