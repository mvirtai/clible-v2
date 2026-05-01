# feat(verse): chapter & book lookup; refactor: SQL-scoped FTS search

Short Format (`.cursor/rules/pr-templates.md`). Paste into the GitHub PR description; rename this file to `pr-<number>-verse-chapter-book-and-sql-search-scope.md` after you open the PR and add the link below.

- Extended `VerseService.get_verses` to resolve chapter references (e.g. `John 3`) and book-only references (e.g. `John`) via existing parser scopes, delegating to `get_chapter_verses` / `get_book_verses`.
- Updated `clible verse` with `--page` and `--page-size` (chapter/book only; `0` shows all); export still writes the full passage, not a single page.
- Refreshed `VERSE_HELP` and added CLI and service tests (`tests/test_cli/test_verse_commands.py`, `tests/test_services/test_verse_service.py`).
- Moved FTS search scope filtering into `VerseRepo.search_text` (SQL `WHERE` for testament, book, chapter, and verse range) and removed the Python-side `filter_verses_by_scope` path from `VerseService.search_text`; added repository tests for scoped queries (`tests/test_db/test_repositories/test_verse_repo.py`).

**Tests:** `uv run pytest -v` — all passing before push.

**GitHub:** _(add PR URL after `gh pr create`)_

Ready for squash and merge.
