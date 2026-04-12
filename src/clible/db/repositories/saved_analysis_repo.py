import sqlite3
import uuid
from typing import TypedDict


class SavedAnalysisRow(TypedDict):
    """Row shape for the saved_analyses table."""

    id: str
    scope_id: str
    name: str
    reference: str
    analysis_type: str
    translation_id: str | None
    params_json: str | None
    created_at: str


def _row_to_saved_analysis(row: sqlite3.Row) -> SavedAnalysisRow:
    return {
        "id": row["id"],
        "scope_id": row["scope_id"],
        "name": row["name"],
        "reference": row["reference"],
        "analysis_type": row["analysis_type"],
        "translation_id": row["translation_id"],
        "params_json": row["params_json"],
        "created_at": row["created_at"],
    }


class SavedAnalysisRepo:
    """CRUD operations for the saved_analyses table."""

    def __init__(self, conn: sqlite3.Connection):
        """Initialize SavedAnalysisRepo with a SQLite connection."""
        self.conn = conn

    def create(
        self,
        scope_id: str,
        name: str,
        reference: str,
        analysis_type: str,
        translation_id: str | None,
        params_json: str | None = None,
    ) -> str:
        """Create a new saved analysis record."""
        analysis_id = str(uuid.uuid4())
        self.conn.execute(
            """
            INSERT INTO saved_analyses (
                id, scope_id, name, reference, analysis_type, translation_id, params_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (analysis_id, scope_id, name, reference, analysis_type, translation_id, params_json),
        )
        self.conn.commit()
        return analysis_id

    def get(self, analysis_id: str) -> SavedAnalysisRow | None:
        """Get a saved analysis by ID."""
        cursor = self.conn.execute("SELECT * FROM saved_analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        return _row_to_saved_analysis(row) if row else None

    def get_by_name(self, name: str, scope_id: str) -> SavedAnalysisRow | None:
        """Get a saved analysis by name within a specific scope."""
        cursor = self.conn.execute(
            "SELECT * FROM saved_analyses WHERE name = ? AND scope_id = ?",
            (name, scope_id),
        )
        row = cursor.fetchone()
        return _row_to_saved_analysis(row) if row else None

    def list_by_scope(self, scope_id: str) -> list[SavedAnalysisRow]:
        """List all saved analyses in a scope, ordered by newest first."""
        cursor = self.conn.execute(
            "SELECT * FROM saved_analyses WHERE scope_id = ? ORDER BY created_at DESC",
            (scope_id,),
        )
        return [_row_to_saved_analysis(row) for row in cursor.fetchall()]

    def delete(self, analysis_id: str, scope_id: str) -> bool:
        """Delete a saved analysis. Must match both ID and scope_id for security."""
        cursor = self.conn.execute(
            "DELETE FROM saved_analyses WHERE id = ? AND scope_id = ?",
            (analysis_id, scope_id),
        )
        self.conn.commit()
        return cursor.rowcount > 0
