import sqlite3
from pathlib import Path


def run_migrations(conn: sqlite3.Connection, migrations_dir: Path | None = None) -> None:
    """Apply all not-yet-applied migration files in order.

    Creates the _migrations table if missing, then for each .sql file in
    migrations_dir (sorted by filename), runs it only if its name is not
    already in _migrations, and records the name after a successful run.
    """
    cursor = conn.cursor()
    if migrations_dir is None:
        migrations_dir = Path(__file__).resolve().parent / "migrations"

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    applied = {row[0] for row in cursor.execute("SELECT name FROM _migrations").fetchall()}
    migration_files = sorted(migrations_dir.glob("*.sql"), key=lambda p: p.name)

    for path in migration_files:
        if path.name in applied:
            continue
        with open(path, encoding="utf-8") as f:
            sql = f.read().strip()
        if sql:
            cursor.executescript(sql)
        cursor.execute(
            "INSERT INTO _migrations (name) VALUES (?)",
            (path.name,),
        )
        applied.add(path.name)

    conn.commit()
