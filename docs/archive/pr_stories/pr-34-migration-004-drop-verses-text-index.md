# feat: drop redundant verses text index (migration 004)

Short Format (`.cursor/rules/pr-templates.md`). Canonical copy of the GitHub PR description.

- Added migration `004_drop_verses_text_index.sql` to drop redundant B-tree index `idx_verses_search` on `verses.text` (FTS5 on `verses_fts` handles search; the index added storage and write cost without helping FTS queries).
- Added `test_migrations_drop_redundant_verses_text_index` in `tests/test_db/test_get_connection.py` asserting `idx_verses_search` is absent and `idx_verses_lookup` remains after migrations.
- Updated `docs/PROJECT_OVERVIEW.md` schema section, Done table, and file map to include migration 004 and revised index notes.
- Track PR descriptions under `pr_stories/` in git; stop ignoring that directory in `.gitignore`; update `.cursor/rules/pr-stories.mdc` and `how-to-use-rules.mdc` to point at `.cursor/rules/pr-templates.md`.

**Tests:** `uv run pytest -v` — all passing at merge time.

**GitHub:** https://github.com/mvirtai/clible-v2/pull/34

Ready for squash and merge.
