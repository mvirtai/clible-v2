# refactor: improve Docker security and build hygiene

Hardens the Docker image for production readiness: non-root runtime user, user-owned venv, BuildKit cache mounts, and cleaner dependency separation. Also cleans up `.dockerignore`, fixes `.envrc` syntax, and moves dev-only tools out of production dependencies.

## Summary

- **Dockerfile (runtime)** — Created a dedicated non-root user (`clible`, UID/GID 10001) with explicit IDs for predictable ownership across Docker, CI, and Kubernetes. The wheel is installed into a user-owned venv instead of system site-packages, so the runtime container never requires root privileges.
- **Dockerfile (builder)** — Added BuildKit cache mount (`--mount=type=cache`) for the uv cache directory, reducing rebuild times. Changed `--all-groups` to `--group dev` since only dev tools are needed for the check stage. Updated syntax directive to `1.7`. Translated Finnish comments to English.
- **pyproject.toml** — Moved `ruff` from production `dependencies` to the `dev` dependency group where it belongs. Removed `pylance` (IDE extension, not a runtime dependency).
- **.dockerignore** — Extended exclusions: `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.coverage`, `htmlcov/`, `plans/`, `outputs/`, and demo cast files. Keeps the build context smaller and avoids leaking local artifacts.
- **.envrc** — Replaced `dotenv_if_exists` with `source_env_if_exists` (correct direnv built-in).
- **PR stories & templates** — Added historical PR stories to `pr_stories/` and a PR template rule at `.cursor/rules/pr-templates.md`.

## Files added

- `pr_stories/*.md` — Nine historical PR story documents for project reference.
- `.cursor/rules/pr-templates.md` — Short and long PR description templates with usage guidance.

## Files modified

- `Dockerfile` — Non-root user, user venv, cache mount, dev-only sync, English comments.
- `.dockerignore` — Extended exclusion list for cache dirs, coverage, plans, demos.
- `.envrc` — Fixed direnv function name.
- `pyproject.toml` — Moved `ruff` to dev group, removed `pylance`.
- `uv.lock` — Regenerated to match updated dependencies.

## Tests

No test files changed. Existing suite runs inside the builder stage as before:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -v
```

## Usage

Build and verify the hardened image:

```bash
# Build (uses BuildKit by default with Docker 23+)
docker build -t clible:latest .

# Verify non-root runtime user
docker run --rm clible:latest --help
docker run --rm --entrypoint id clible:latest
# uid=10001(clible) gid=10001(clible) groups=10001(clible)
```

## Notes

- The previous `pip upgrade` workaround for CVE-2025-8869 is no longer needed since the runtime stage uses a fresh venv with its own pip, not the system pip.
- `pylance` was likely added by accident (it is a VS Code extension package, not useful at runtime).

---

**Ready for Squash and Merge.**
