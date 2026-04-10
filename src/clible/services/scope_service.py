from clible.config import Config
from clible.db.repositories.scope_repo import ScopeRepo, ScopeRow


class ScopeService:
    """Service for managing research scopes (contexts)."""

    def __init__(self, scope_repo: ScopeRepo, config: Config):
        """Initialize with repository and config."""
        self._scope_repo = scope_repo
        self._config = config

    def get_current_scope_id(self) -> str:
        """Resolve the current scope ID based on CLIBLE_SCOPE config.

        Ensures the scope exists in the database.
        """
        name = self._config.scope_name
        existing = self._scope_repo.get_by_name(name)
        if existing:
            return existing["id"]

        # Bootstrap scope if it doesn't exist
        return self._scope_repo.create(name)

    def list_scopes(self) -> list[ScopeRow]:
        """List all available scopes."""
        return self._scope_repo.list_all()

    def create_scope(self, name: str) -> str:
        """Create a new scope and return its ID."""
        existing = self._scope_repo.get_by_name(name)
        if existing:
            return existing["id"]
        return self._scope_repo.create(name)
