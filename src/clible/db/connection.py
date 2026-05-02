import sqlite3
from pathlib import Path
import re as _re

from clible.config import get_config
from clible.db.migrations import run_migrations
from clible.db.seed_books import seed_books_if_empty


def _regexp_fn(pattern: str, value: str | None) -> bool:
    if value is None:
        return False
    return bool(_re.search(pattern, value, _re.IGNORECASE))


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Return a configured connection to the database.

    Uses config db_path when db_path is not provided (e.g. in production).
    Callers can pass a path (e.g. ':memory:' or a test path) for tests.
    """
    path = db_path if db_path is not None else get_config().db_path
    conn = sqlite3.connect(str(path))
    conn.create_function("REGEXP", 2, _regexp_fn)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row

    # TODO: skip migrations/seed if schema version is already current
    run_migrations(conn)
    seed_books_if_empty(conn)  # Populate books table from JSON if empty

    return conn
