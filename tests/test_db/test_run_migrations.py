"""Tests for the migration runner (run_migrations).

We use a dedicated test migrations directory (tests/test_db/migrations/) so that:
- Tests do not depend on the real app migrations (src/clible/db/migrations/).
- We control exactly which .sql files exist and what they do.
- The same behaviour can be asserted in any environment.

Flow under test:
1. run_migrations(conn, migrations_dir) creates _migrations if missing.
2. It runs each .sql file in sorted order by filename.
3. After each file it records the filename in _migrations so it is not run again.
4. A second call with the same conn should not re-apply migrations (idempotent).
"""

import sqlite3
from pathlib import Path

from clible.db.migrations import run_migrations

# Directory next to this test file containing one or more .sql migration files.
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def test_fresh_database_gets_all_migrations():
    """A new in-memory DB should run every migration and record it in _migrations."""
    conn = sqlite3.connect(":memory:")
    run_migrations(conn, MIGRATIONS_DIR)

    rows = conn.execute("SELECT name FROM _migrations ORDER BY id").fetchall()
    assert len(rows) >= 1, "At least one migration should be recorded"
    assert rows[0][0] == "001_minimal.sql"

    # Side-effect of our test migration: dummy table exists
    conn.execute("SELECT 1 FROM _test_dummy LIMIT 1")


def test_already_migrated_database_skips_migrations():
    """Running run_migrations again on the same DB must not re-apply or duplicate rows."""
    conn = sqlite3.connect(":memory:")
    run_migrations(conn, MIGRATIONS_DIR)
    count_after_first = conn.execute("SELECT COUNT(*) FROM _migrations").fetchone()[0]

    run_migrations(conn, MIGRATIONS_DIR)
    count_after_second = conn.execute("SELECT COUNT(*) FROM _migrations").fetchone()[0]

    assert count_after_second == count_after_first, (
        "Second run must not add new rows to _migrations"
    )
