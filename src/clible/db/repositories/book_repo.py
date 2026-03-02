"""Book repository and related types.

- DB and bible_structure.json store testament as string ("OT", "NT"). Only BookRepo
  converts these to Testament enum when building BookRow. Seed and JSON stay string-based.
"""

import sqlite3
from enum import Enum
from typing import TypedDict


class Testament(str, Enum):
    """Canonical section of the Bible. Values match DB/JSON (OT, NT, DEU)."""

    OT = "OT"  # Old Testament
    NT = "NT"  # New Testament
    DEU = "DEU"  # Deuterocanonical / Apocrypha (for future use)


class BookRow(TypedDict):
    """Type for a single book as returned by BookRepo. testament is converted from DB string."""

    id: str
    name: str
    testament: Testament
    position: int
    chapters: int


def _row_to_book(row: sqlite3.Row) -> BookRow:
    """Convert a DB row to BookRow. Translates testament string to Testament enum."""
    return {
        "id": row["id"],
        "name": row["name"],
        "testament": Testament(row["testament"]),
        "position": row["position"],
        "chapters": row["chapters"],
    }


class BookRepo:
    """Read-only access to the books table. Returns BookRow (with Testament enum)."""

    def __init__(self, conn: sqlite3.Connection):
        """Initialize BookRepo with a SQLite connection."""
        self.conn = conn

    def get_all(self) -> list[BookRow]:
        """Get all books, ordered by position in the Bible.

        Returns:
            List of BookRow dicts. Empty list if none found.
        """
        cursor = self.conn.execute("SELECT * FROM books ORDER BY position")
        return [_row_to_book(row) for row in cursor.fetchall()]

    def get_by_id(self, book_id: str) -> BookRow | None:
        """Get a single book by id (e.g. GEN, JHN). Returns None if not found."""
        row = self.conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,),
        ).fetchone()
        return _row_to_book(row) if row else None

    def get_by_name(self, name: str) -> BookRow | None:
        """Get a single book by exact name (e.g. Genesis, John). Returns None if not found."""
        row = self.conn.execute(
            "SELECT * FROM books WHERE name = ?",
            (name,),
        ).fetchone()
        return _row_to_book(row) if row else None

    def search(self, term: str) -> list[BookRow]:
        """Search books by id or name (case-insensitive partial match).

        Returns:
            List of matching BookRow dicts, ordered by position.
        """
        pattern = f"%{term}%"
        cursor = self.conn.execute(
            """
            SELECT * FROM books
            WHERE id LIKE ? OR name LIKE ?
            ORDER BY position
            """,
            (pattern, pattern),
        )
        return [_row_to_book(row) for row in cursor.fetchall()]
