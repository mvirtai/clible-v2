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
