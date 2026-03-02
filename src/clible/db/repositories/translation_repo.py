import sqlite3


class TranslationRepo:
    """CRUD operations for the translations table."""

    def __init__(self, conn: sqlite3.Connection):
        """Initialize TranslationRepo with a SQLite connection."""
        self.conn = conn

    def get_all(self) -> list[dict]:
        """Get all installed translations, ordered by installed_at.

        Returns:
            List of dicts (one per translation). Empty list if none found.
        """
        cursor = self.conn.execute("SELECT * FROM translations ORDER BY installed_at")
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, translation_id: str) -> dict | None:
        """Get a single translation by ID. Returns None if not found."""
        cursor = self.conn.execute(
            "SELECT * FROM translations WHERE id = ?",
            (translation_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

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

    def get_default(self) -> dict | None:
        """Return the default translation: WEB if installed, else first installed.

        Returns None if no translations are installed.
        """
        row = self.conn.execute(
            "SELECT * FROM translations WHERE id = ? LIMIT 1",
            ("web",),
        ).fetchone()
        if row:
            return dict(row)
        row = self.conn.execute(
            "SELECT * FROM translations ORDER BY installed_at LIMIT 1"
        ).fetchone()
        return dict(row) if row else None
