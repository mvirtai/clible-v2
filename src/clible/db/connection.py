import sqlite3
from pathlib import Path

from clible.config import get_config
from clible.db.migrations import run_migrations
from clible.db.seed_books import seed_books_if_empty

db_path = get_config().db_path


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Return a configured connection to the database.

    Uses config db_path when db_path is not provided (e.g. in production).
    Callers can pass a path (e.g. ':memory:' or a test path) for tests.
    """
    path = db_path if db_path is not None else get_config().db_path
    conn = sqlite3.connect(str(path))

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row

    run_migrations(conn)
    seed_books_if_empty(conn)  # Populate books table from JSON if empty

    return conn
