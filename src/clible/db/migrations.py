import sqlite3
from pathlib import Path


def run_migrations(conn: sqlite3.Connection, migrations_dir: Path | None = None):
    """Run all migrations on the database."""
    cursor = conn.cursor()
    if migrations_dir is None:
        migrations_dir = Path(__file__).resolve().parent / "migrations"
    for migration_file in migrations_dir.glob("*.sql"):
        with open(migration_file, "r") as f:
            cursor.execute(f.read())
    conn.commit()
