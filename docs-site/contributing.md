# Contributing

Thanks for considering a contribution. clible is a small, opinionated codebase with strict architectural rules — read this page before opening a PR.

## Local setup

```bash
git clone https://github.com/vivaldev/clible-v2.git
cd clible-v2
uv sync --all-groups
uv run pytest -v
```

If tests pass and `uv run ruff check .` is clean, you are ready to make changes.

## Branching

```bash
git switch -c feat/short-description
# … make changes …
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
git push -u origin HEAD
```

Open a pull request against `main` once CI is green.

## Commit conventions

The project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add reading-plan command
fix: correct FTS5 empty-result JSON shape
refactor: extract verse formatting to ui layer
test:  add VerseRepo search edge cases
docs:  update deployment guide
```

Use `git switch` for branches and `git restore` for files. The legacy `git checkout` command is discouraged.

## Architectural rules

These boundaries are enforced by code review. Read [the architecture overview](/architecture/overview) before proposing changes that span layers.

- UI calls services only — never repos, never the database, never HTTP.
- Services orchestrate repos and parsers — they never import `click` or `rich`.
- Repositories receive a `sqlite3.Connection` and return plain dicts — they never print or make network calls.
- Parsers read XML and return verse dicts — they never touch the database.

## Testing rules

- Tests accompany the implementation. Untested code is incomplete.
- Use in-memory SQLite for repo and service tests: `get_connection(":memory:")`.
- Mock HTTP calls. No real network in tests.
- Fixtures live in `tests/conftest.py`.
- Test files follow `test_<module>.py` naming.

```bash
# Run a specific test file
uv run pytest tests/test_db/test_verse_repo.py -v

# Run with coverage
uv run pytest --cov=src/clible --cov-report=term-missing
```

## Documentation

If your change affects the user-facing CLI or the web API, update the docs in this site (`docs-site/`). The architecture and ADR documents are append-only — for a significant design shift, add a new ADR rather than editing an existing one.

## Code style

- Python: 3.12+, `ruff` for linting and formatting (`uv run ruff format .`).
- TypeScript: tsc check via `npm run lint` in `src/clible-web`.
- Comments: explain *why*, not *what*. Avoid narration of the obvious.

## Reporting issues

Open a GitHub issue with:

1. What you expected to happen
2. What actually happened (with copy-paste output where possible)
3. The command or steps to reproduce
4. Your OS and Python version
