import sqlite3
import uuid
from typing import TypedDict


class VerseRow(TypedDict):
    """Row shape for the verses table as returned by VerseRepo."""

    id: str
    translation_id: str
    book_id: str
    chapter: int
    verse: int
    text: str


class VerseSeed(TypedDict):
    """Input verse fields for bulk insert (``save_verses``)."""

    book_id: str
    chapter: int
    verse: int
    text: str


def _row_to_verse(row: sqlite3.Row) -> VerseRow:
    return {
        "id": row["id"],
        "translation_id": row["translation_id"],
        "book_id": row["book_id"],
        "chapter": row["chapter"],
        "verse": row["verse"],
        "text": row["text"],
    }


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
    ) -> VerseRow | None:
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
        return _row_to_verse(row) if row else None

    def get_verses(
        self,
        translation_id: str,
        book_id: str,
        chapter: int,
    ) -> list[VerseRow]:
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
        return [_row_to_verse(row) for row in cursor.fetchall()]

    def get_verses_in_range(
        self,
        translation_id: str,
        book_id: str,
        chapter: int,
        verse_start: int,
        verse_end: int,
    ) -> list[VerseRow]:
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
        return [_row_to_verse(row) for row in cursor.fetchall()]

    def save_verses(self, verses: list[VerseSeed], translation_id: str) -> int:
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

    def get_book_verses(self, translation_id: str, book_id: str) -> list[VerseRow]:
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
        return [_row_to_verse(row) for row in cursor.fetchall()]

    # TODO: use FTS5 snippet()/highlight() to simplify UI-side highlighting
    def search_text(
        self,
        word: str,
        translation_id: str | None = None,
        *,
        book_ids: tuple[str, ...] | None = None,
        book_id: str | None = None,
        chapter: int | None = None,
        verse_min: int | None = None,
        verse_max: int | None = None,
    ) -> list[VerseRow]:
        """Search verses by word using FTS5, with optional scope filters in SQL.

        Args:
            word: The word to search for (case-insensitive).
            translation_id: If set, restrict to this translation.
            book_ids: If set, restrict to these book ids (e.g. testament scope).
            book_id: Single-book scope, or with ``chapter`` for chapter/verse scope.
            chapter: Restrict to this chapter (with ``book_id``).
            verse_min, verse_max: Inclusive verse range (with ``book_id`` and ``chapter``).

        Returns:
            Verse rows ordered by book, chapter, verse.
        """
        if book_ids is not None and len(book_ids) == 0:
            return []

        query = """
            SELECT v.*
            FROM verses_fts f
            JOIN verses v ON v.rowid = f.rowid
            WHERE f.text MATCH ?
        """
        params: list = [word]

        if translation_id:
            query += " AND v.translation_id = ?"
            params.append(translation_id)

        if book_ids is not None:
            placeholders = ",".join("?" * len(book_ids))
            query += f" AND v.book_id IN ({placeholders})"
            params.extend(book_ids)
        elif book_id is not None:
            query += " AND v.book_id = ?"
            params.append(book_id)
            if chapter is not None:
                query += " AND v.chapter = ?"
                params.append(chapter)
                if verse_min is not None and verse_max is not None:
                    query += " AND v.verse >= ? AND v.verse <= ?"
                    params.extend([verse_min, verse_max])

        query += " ORDER BY v.book_id, v.chapter, v.verse"

        cursor = self.conn.execute(query, params)
        return [_row_to_verse(row) for row in cursor.fetchall()]
