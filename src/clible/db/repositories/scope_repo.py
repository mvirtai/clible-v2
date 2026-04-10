import sqlite3
import uuid
from typing import TypedDict


class ScopeRow(TypedDict):
    """Row shape for the scopes table."""

    id: str
    name: str
    created_at: str


def _row_to_scope(row: sqlite3.Row) -> ScopeRow:
    return {
        "id": row["id"],
        "name": row["name"],
        "created_at": row["created_at"],
    }


class ScopeRepo:
    """CRUD operations for the scopes table."""

    def __init__(self, conn: sqlite3.Connection):
        """Initialize ScopeRepo with a SQLite connection."""
        self.conn = conn

    def create(self, name: str) -> str:
        """Create a new scope with the given name. Returns the inner UUID."""
        scope_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO scopes (id, name) VALUES (?, ?)",
            (scope_id, name),
        )
        self.conn.commit()
        return scope_id

    def get(self, scope_id: str) -> ScopeRow | None:
        """Get a scope by ID."""
        cursor = self.conn.execute("SELECT * FROM scopes WHERE id = ?", (scope_id,))
        row = cursor.fetchone()
        return _row_to_scope(row) if row else None

    def get_by_name(self, name: str) -> ScopeRow | None:
        """Get a scope by name (e.g. 'default')."""
        cursor = self.conn.execute("SELECT * FROM scopes WHERE name = ?", (name,))
        row = cursor.fetchone()
        return _row_to_scope(row) if row else None

    def list_all(self) -> list[ScopeRow]:
        """List all available scopes."""
        cursor = self.conn.execute("SELECT * FROM scopes ORDER BY name")
        return [_row_to_scope(row) for row in cursor.fetchall()]

    def get_or_create_default(self) -> str:
        """Ensure 'default' scope exists and return its ID."""
        existing = self.get_by_name("default")
        if existing:
            return existing["id"]
        return self.create("default")
