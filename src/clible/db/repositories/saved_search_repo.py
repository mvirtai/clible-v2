import sqlite3
import uuid
from typing import TypedDict


class SavedSearchRow(TypedDict):
    """Row shape for the saved_searches table."""

    id: str
    scope_id: str
    name: str
    query_text: str
    search_scope: str
    scope_value: str | None
    translation_id: str | None
    created_at: str


def _row_to_saved_search(row: sqlite3.Row) -> SavedSearchRow:
    return {
        "id": row["id"],
        "scope_id": row["scope_id"],
        "name": row["name"],
        "query_text": row["query_text"],
        "search_scope": row["search_scope"],
        "scope_value": row["scope_value"],
        "translation_id": row["translation_id"],
        "created_at": row["created_at"],
    }


class SavedSearchRepo:
    """CRUD operations for the saved_searches table."""

    def __init__(self, conn: sqlite3.Connection):
        """Initialize SavedSearchRepo with a SQLite connection."""
        self.conn = conn

    def create(
        self,
        scope_id: str,
        name: str,
        query_text: str,
        search_scope: str,
        scope_value: str | None,
        translation_id: str | None,
    ) -> str:
        """Create a new saved search record."""
        search_id = str(uuid.uuid4())
        self.conn.execute(
            """
            INSERT INTO saved_searches (
                id, scope_id, name, query_text, search_scope, scope_value, translation_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (search_id, scope_id, name, query_text, search_scope, scope_value, translation_id),
        )
        self.conn.commit()
        return search_id

    def get(self, search_id: str) -> SavedSearchRow | None:
        """Get a saved search by ID."""
        cursor = self.conn.execute("SELECT * FROM saved_searches WHERE id = ?", (search_id,))
        row = cursor.fetchone()
        return _row_to_saved_search(row) if row else None

    def get_by_name(self, name: str, scope_id: str) -> SavedSearchRow | None:
        """Get a saved search by name within a specific scope."""
        cursor = self.conn.execute(
            "SELECT * FROM saved_searches WHERE name = ? AND scope_id = ?",
            (name, scope_id),
        )
        row = cursor.fetchone()
        return _row_to_saved_search(row) if row else None

    def list_by_scope(self, scope_id: str) -> list[SavedSearchRow]:
        """List all saved searches in a scope, ordered by newest first."""
        cursor = self.conn.execute(
            "SELECT * FROM saved_searches WHERE scope_id = ? ORDER BY created_at DESC",
            (scope_id,),
        )
        return [_row_to_saved_search(row) for row in cursor.fetchall()]

    def delete(self, search_id: str, scope_id: str) -> bool:
        """Delete a saved search. Must match both ID and scope_id for security."""
        cursor = self.conn.execute(
            "DELETE FROM saved_searches WHERE id = ? AND scope_id = ?",
            (search_id, scope_id),
        )
        self.conn.commit()
        return cursor.rowcount > 0
