import sqlite3
from typing import TypedDict


class TranslationRow(TypedDict):
    """Row shape for the translations table as returned by TranslationRepo."""

    id: str
    name: str
    language: str
    format: str
    source_url: str | None
    installed_at: str


def _row_to_translation(row: sqlite3.Row) -> TranslationRow:
    return {
        "id": row["id"],
        "name": row["name"],
        "language": row["language"],
        "format": row["format"],
        "source_url": row["source_url"],
        "installed_at": row["installed_at"],
    }


class TranslationRepo:
    """CRUD operations for the translations table."""

    def __init__(self, conn: sqlite3.Connection):
        """Initialize TranslationRepo with a SQLite connection."""
        self.conn = conn

    def get_all(self) -> list[TranslationRow]:
        """Get all installed translations, ordered by installed_at.

        Returns:
            List of rows. Empty list if none found.
        """
        cursor = self.conn.execute("SELECT * FROM translations ORDER BY installed_at")
        return [_row_to_translation(row) for row in cursor.fetchall()]

    def get_by_id(self, translation_id: str) -> TranslationRow | None:
        """Get a single translation by ID. Returns None if not found."""
        cursor = self.conn.execute(
            "SELECT * FROM translations WHERE id = ?",
            (translation_id,),
        )
        row = cursor.fetchone()
        return _row_to_translation(row) if row else None

    def exists(self, translation_id: str) -> bool:
        """Return True if a translation with the given ID is installed."""
        cursor = self.conn.execute(
            "SELECT 1 FROM translations WHERE id = ? LIMIT 1",
            (translation_id,),
        )
        return cursor.fetchone() is not None

    def create(self, translation_data: dict, *, commit: bool = True) -> str:
        """Insert a new translation. Returns the translation id.

        Args:
            translation_data: dict with keys id, name, language, format,
                and optionally source_url.
            commit: If True, commit the transaction. Set False when the caller
                manages the transaction (e.g. bulk seed operations).
        """
        self.conn.execute(
            """
            INSERT INTO translations (id, name, language, format, source_url)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                translation_data["id"],
                translation_data["name"],
                translation_data["language"],
                translation_data["format"],
                translation_data.get("source_url"),
            ),
        )
        if commit:
            self.conn.commit()
        return translation_data["id"]

    def delete(self, translation_id: str) -> None:
        """Remove a translation. Verses are removed via CASCADE."""
        self.conn.execute(
            "DELETE FROM translations WHERE id = ?",
            (translation_id,),
        )
        self.conn.commit()

    def get_default(self) -> TranslationRow | None:
        """Return the default translation: WEB if installed, else first installed.

        Returns None if no translations are installed.
        """
        row = self.conn.execute(
            "SELECT * FROM translations WHERE id = ? LIMIT 1",
            ("web",),
        ).fetchone()
        if row:
            return _row_to_translation(row)
        row = self.conn.execute(
            "SELECT * FROM translations ORDER BY installed_at LIMIT 1"
        ).fetchone()
        return _row_to_translation(row) if row else None
