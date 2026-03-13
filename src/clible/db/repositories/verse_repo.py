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

    def get_verses_in_range(
        self,
        translation_id: str,
        book_id: str,
        chapter: int,
        verse_start: int,
        verse_end: int,
    ) -> list[dict]:
        """Get verses in a chapter for the given verse range (inclusive), ordered by verse.

        Returns empty list if none found.
        """
        cursor = self.conn.execute(
            """
            SELECT * FROM verses
            WHERE translation_id = ? AND book_id = ? AND chapter = ?
              AND verse >= ? AND verse <= ?
            ORDER BY verse
            """,
            (translation_id, book_id, chapter, verse_start, verse_end),
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

    def get_book_verses(self, translation_id: str, book_id: str) -> list[dict]:
        """Get all verses in a book, ordered by chapter and verse.

        Args:
            translation_id: Translation ID.
            book_id: Book ID (e.g. GEN, JHN).

        Returns:
            List of all verses in the book, ordered by chapter then verse.
        """
        cursor = self.conn.execute(
            """
            SELECT * FROM verses
            WHERE translation_id = ? AND book_id = ?
            ORDER BY chapter, verse
            """,
            (translation_id, book_id),
        )
        return [dict(row) for row in cursor.fetchall()]

    # IDEA (AI): The FTS search is currently basic. SQLite's FTS5 supports
    # powerful features like snippet() for extracting relevant text fragments
    # and highlight() for adding markers to matches directly in the SQL query.
    # Leveraging these could simplify the UI-side highlighting logic.
    def search_text(self, word: str, translation_id: str | None = None) -> list[dict]:
        """Search verses by word using FTS5 index for efficient full-text search.

        Args:
            word: The word to search for (case-insensitive).
            translation_id: Optional translation ID to filter by.
                If None, searches all translations.

        Returns:
            List of verse dicts that contain the specified word,
            ordered by book/chapter/verse.
        """
        query = """
            SELECT v.*
            FROM verses_fts f
            JOIN verses v ON v.rowid = f.rowid
            WHERE f.text MATCH ?
        """
        params = [word]

        if translation_id:
            query += " AND v.translation_id = ?"
            params.append(translation_id)

        query += " ORDER BY v.book_id, v.chapter, v.verse"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
