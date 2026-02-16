from pathlib import Path
import sqlite3
from clible.config import get_config
from clible.db.migrations import run_migrations

db_path = get_config().db_path


def get_connection() -> sqlite3.Connection:
    """Return a configured connection to the database."""
    conn = sqlite3.connect(str(db_path))

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row

    # Run migrations
    migrations_dir = get_config().data_dir / "migrations"
    run_migrations(conn, migrations_dir)

    return conn
