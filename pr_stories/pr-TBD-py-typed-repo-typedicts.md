# feat: add PEP 561 marker and TypedDict row types for repos

This PR completes private tasks **T-PY-TYPED** and **T-TYPEDICTS**: the installable package is marked as typed for downstream tools, and translation/verse repositories expose explicit `TypedDict` shapes instead of untyped `dict` returns.

## Summary

- Added empty `src/clible/py.typed` (PEP 561); verified it is included in the built wheel (`clible/py.typed`).
- Introduced `TranslationRow` and `_row_to_translation()` in `translation_repo.py`; all read methods return `TranslationRow` / `list[TranslationRow]` / optional forms.
- Introduced `VerseRow`, `VerseSeed`, and `_row_to_verse()` in `verse_repo.py`; search and CRUD paths return `VerseRow` lists or singles; `save_verses` accepts `list[VerseSeed]`.
- Updated `VerseService` to use `BookRow`, `VerseRow` in return types and dropped `TYPE_CHECKING`-only repo imports in favor of normal imports with `from __future__ import annotations`.
- Documented PEP 561 and repo row types under **Key Conventions** in `docs/PROJECT_OVERVIEW.md`.
- Added `tests/test_package/test_py_typed.py` asserting the marker exists via `importlib.resources.files("clible")`.

## Files added

- `src/clible/py.typed` — PEP 561 package marker (empty file).
- `tests/test_package/test_py_typed.py` — packaging test for `py.typed`.
- `pr_stories/pr-TBD-py-typed-repo-typedicts.md` — this PR description (rename to `pr-<number>-py-typed-repo-typedicts.md` after opening the PR).

## Files modified

- `src/clible/db/repositories/translation_repo.py` — `TranslationRow`, row helper, typed return signatures.
- `src/clible/db/repositories/verse_repo.py` — `VerseRow`, `VerseSeed`, row helper, typed return/input signatures.
- `src/clible/services/verse_service.py` — aligned return types with repo/service contracts.
- `docs/PROJECT_OVERVIEW.md` — Key Conventions: TypedDict rows + PEP 561 note.

## Tests

- `uv run pytest -v` — **238 tests**, all passing.
- `uv run ruff check .` and `uv run ruff format --check .` — clean.
- `uv build` — wheel contains `clible/py.typed`.

## Usage

No CLI or runtime behavior change. Type checkers and IDEs can use published types when depending on this package; repository methods are annotated with concrete row shapes.
