import sqlite3

from clible.db.connection import get_connection


def test_get_connection():
    conn = get_connection()
    assert conn is not None

    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode")
    assert cursor.fetchone()[0] == "wal"

    cursor.execute("PRAGMA foreign_keys")
    assert cursor.fetchone()[0] == 1

    assert conn.row_factory is sqlite3.Row
