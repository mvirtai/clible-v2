import sqlite3
import uuid


class VerseRepo:
    """CRUD operations for the verses table."""

    def __init__(self, conn: sqlite3.Connection):
        """Initialize VerseRepo with a SQLite connection."""
        self.conn = conn

    def get_verse(
        self,
        translation_id: str,
        book_id: str,
        chapter: int,
        verse: int,
    ) -> dict | None:
        """Get a single verse by translation, book, chapter, and verse.

        Returns None if not found.
        """
        row = self.conn.execute(
            """
            SELECT * FROM verses
            WHERE translation_id = ? AND book_id = ? AND chapter = ? AND verse = ?
            """,
            (translation_id, book_id, chapter, verse),
        ).fetchone()
        return dict(row) if row else None

    def get_verses(
        self,
        translation_id: str,
        book_id: str,
        chapter: int,
    ) -> list[dict]:
        """Get all verses in a chapter, ordered by verse number.

        Returns empty list if none found.
        """
        cursor = self.conn.execute(
            """
            SELECT * FROM verses
            WHERE translation_id = ? AND book_id = ? AND chapter = ?
            ORDER BY verse
            """,
            (translation_id, book_id, chapter),
        )
        return [dict(row) for row in cursor.fetchall()]

    def save_verses(self, verses: list[dict], translation_id: str) -> int:
        """Bulk insert verses for a translation.

        Each verse dict must have: book_id, chapter, verse, text.
        Generates id (UUID) for each row. Returns number of verses inserted.
        """
        rows = []
        for v in verses:
            rows.append(
                {
                    "id": str(uuid.uuid4()),
                    "translation_id": translation_id,
                    "book_id": v["book_id"],
                    "chapter": v["chapter"],
                    "verse": v["verse"],
                    "text": v["text"],
                }
            )
        with self.conn:
            cursor = self.conn.executemany(
                """
                INSERT INTO verses (id, translation_id, book_id, chapter, verse, text)
                VALUES (:id, :translation_id, :book_id, :chapter, :verse, :text)
                """,
                rows,
            )
        return cursor.rowcount
