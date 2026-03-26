# Pull Request Templates

Two PR story formats based on clible v1 patterns and professional conventions.

---

## Short Format (Feature PR)

For routine feature work, bug fixes, refactors — one ticket or one clear change.

**Structure:** Bullet list of changes, no section headers.

**Example:**

```markdown
- Added Config dataclass with environment variable overrides (src/clible/config.py).
- Created test verifying default config loads correctly (tests/test_config.py).
- Set up .env.example and .envrc for local dev (direnv).
- Updated .gitignore to exclude .env.
- Disabled pytest --cov until pytest-cov is added (pyproject.toml).
- Added reflection template and notes (reflections/).
```

**When to use:**

- Single ticket completion
- Small to medium scope
- No breaking changes
- Straightforward feature/fix

---

## Long Format (Release or Complex PR)

For releases, multi-ticket work, architectural changes, or when extra context helps reviewers.

**Structure:**

```markdown
# PR: <Title>

## Summary

One or two sentences: what this PR does and why.

## Purpose

- Bullet: reason or goal
- Bullet: context or background
- Bullet: related ticket/issue

## Changes in This PR

### 1. Category (e.g. Config Module)
- Change detail
- Change detail

### 2. Category (e.g. Tests)
- Change detail

### 3. Category (e.g. Documentation)
- Change detail

## Files Changed

- file/path – description
- file/path – description

## Test Plan

- [x] Test 1 (e.g. `uv run pytest` passes)
- [x] Test 2 (e.g. no linter errors)
- [ ] Manual test (if applicable)

## Notes

- Optional: caveats, follow-ups, design decisions.
- Optional: disabled features, TODOs for later tickets.

## Related Documentation

- Link to PLAN.md ticket
- Link to other docs/PRs if relevant

---

**Ready for [Squash and Merge | Merge Commit].**
```

**When to use:**

- Release prep (e.g. v0.1.0 batch)
- Multiple tickets bundled
- Breaking changes
- Architectural refactor
- Needs detailed explanation for future reference

---

## Tips

1. **Title:** Use Conventional Commits prefix (`feat:`, `fix:`, `refactor:`, `docs:`).
2. **Scope:** Match the branch scope (e.g. `feat/config-module` → "Configuration module (Ticket 0.2)").
3. **Checkboxes:** Use `- [x]` for completed, `- [ ]` for pending (helps reviewers see test status).
4. **Squash and Merge:** Mention merge strategy at the end if repo uses squash (clible-v2 does).
5. **No AI mentions:** PR body should look human-written (same as commits).

---

## Commit Message (for reference)

Commit format (from `.cursorrules` and `AGENTS.md`):

```
<type>: <subject>

<body: what and why, bullet list of changes>

<footer: optional ticket refs, breaking changes>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`.

Example:

```
feat: add configuration module (Ticket 0.2)

Centralized application configuration with environment variable overrides.
All settings (DB path, API URL, translations, timeouts) can be overridden
via CLIBLE_* env vars for dev, test, and Docker environments.

Changes:
- Config dataclass with defaults and env var support (src/clible/config.py)
- Test verifying default config loads correctly (tests/test_config.py)
- Env file examples and direnv setup (.env.example, .envrc)
- Updated .gitignore to exclude .env
- Disabled pytest --cov until pytest-cov is added (pyproject.toml)

Learning goals: configuration patterns, env var overrides per environment.
```
