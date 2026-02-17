# clible/db/seed_books.py
import sqlite3
from pathlib import Path
import json


def seed_books_if_empty(conn: sqlite3.Connection):
    """Populate books table from bible_structure.json if it's empty."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] > 0:
        return  # Already seeded

    json_path = Path(__file__).resolve().parent.parent / "data" / "bible_structure.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    for book in data["books"]:
        conn.execute(
            "INSERT INTO books (id, name, testament, position, chapters) VALUES (?, ?, ?, ?, ?)",
            (
                book["id"],
                book["name"],
                book["testament"],
                book["position"],
                book["chapters"],
            ),
        )
    conn.commit()
