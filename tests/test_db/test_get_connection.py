import sqlite3

from clible.db.connection import get_connection


def test_get_connection(tmp_path):
    """Verify get_connection returns a properly configured SQLite connection.

    Uses a temporary file DB (not :memory:) so we can verify WAL mode works.
    """
    test_db = tmp_path / "test.db"
    conn = get_connection(test_db)
    assert conn is not None

    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode")
    assert cursor.fetchone()[0] == "wal"

    cursor.execute("PRAGMA foreign_keys")
    assert cursor.fetchone()[0] == 1

    assert conn.row_factory is sqlite3.Row

    conn.close()


def test_migrations_drop_redundant_verses_text_index(tmp_path):
    """Migration 004 removes idx_verses_search; FTS5 (verses_fts) handles text search."""
    conn = get_connection(tmp_path / "test.db")
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='verses' ORDER BY name"
    ).fetchall()
    names = [r[0] for r in rows]
    assert "idx_verses_search" not in names
    assert "idx_verses_lookup" in names
    conn.close()
