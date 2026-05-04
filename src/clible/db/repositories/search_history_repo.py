import sqlite3
import uuid
from typing import TypedDict


class SearchHistoryRow(TypedDict):
    id: str
    query_text: str
    search_scope: str
    scope_value: str | None
    translation_id: str | None
    mode: str
    result_count: int
    searched_at: str


def _row_to_history(row: sqlite3.Row) -> SearchHistoryRow:
    return {
        "id": row["id"],
        "query_text": row["query_text"],
        "search_scope": row["search_scope"],
        "scope_value": row["scope_value"],
        "translation_id": row["translation_id"],
        "mode": row["mode"],
        "result_count": row["result_count"],
        "searched_at": row["searched_at"],
    }


class SearchHistoryRepo:
    """Records and retrieves search history."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def record(
        self,
        query_text: str,
        search_scope: str,
        scope_value: str | None,
        translation_id: str | None,
        mode: str,
        result_count: int,
    ) -> str:
        """Insert a new history entry. Returns the new record's ID."""
        record_id = str(uuid.uuid4())
        self.conn.execute(
            """
            INSERT INTO search_history
                (id, query_text, search_scope, scope_value, translation_id, mode, result_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                query_text,
                search_scope,
                scope_value,
                translation_id,
                mode,
                result_count,
            ),
        )
        self.conn.commit()
        return record_id

    def list_recent(self, limit: int = 10) -> list[SearchHistoryRow]:
        """Return the most recent searches, newest first."""
        cursor = self.conn.execute(
            "SELECT * FROM search_history ORDER BY searched_at DESC LIMIT ?",
            (limit,),
        )
        return [_row_to_history(row) for row in cursor.fetchall()]

    def clear(self) -> int:
        """Delete all history. Returns number of rows deleted."""
        cursor = self.conn.execute("DELETE FROM search_history")
        self.conn.commit()
        return cursor.rowcount
