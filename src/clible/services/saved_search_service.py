from clible.db.repositories.saved_search_repo import SavedSearchRepo, SavedSearchRow
from clible.services.scope_service import ScopeService
from clible.services.verse_service import VerseRow, VerseService


class SavedSearchService:
    """Service to save and re-execute Bible text searches."""

    def __init__(
        self,
        saved_search_repo: SavedSearchRepo,
        scope_service: ScopeService,
        verse_service: VerseService,
    ):
        """Initialize with repos and search engine service."""
        self._repo = saved_search_repo
        self._scope_service = scope_service
        self._verse_service = verse_service

    def save_search(
        self,
        name: str,
        query_text: str,
        search_scope: str = "bible",
        scope_value: str | None = None,
        translation_id: str | None = None,
    ) -> str:
        """Save search parameters to the current scope."""
        scope_id = self._scope_service.get_current_scope_id()
        return self._repo.create(
            scope_id, name, query_text, search_scope, scope_value, translation_id
        )

    def list_saved_searches(self) -> list[SavedSearchRow]:
        """List all saved searches in the current scope."""
        scope_id = self._scope_service.get_current_scope_id()
        return self._repo.list_by_scope(scope_id)

    def get_and_run(self, identifier: str) -> tuple[SavedSearchRow, list[VerseRow]]:
        """Fetch a saved search by ID or name and re-execute it.

        Args:
            identifier: UUID or name of the saved search.

        Returns:
            Tuple of (SavedSearchRow, matching verses).

        Raises:
            ValueError: If the search is not found in the current scope.
        """
        scope_id = self._scope_service.get_current_scope_id()

        # Try ID, then Name
        saved = self._repo.get(identifier)
        if not saved or saved["scope_id"] != scope_id:
            saved = self._repo.get_by_name(identifier, scope_id)

        if not saved:
            raise ValueError(f"Saved search '{identifier}' not found in current scope.")

        verses = self._verse_service.search_text(
            word=saved["query_text"],
            translation_id=saved["translation_id"],
            scope=saved["search_scope"],
            scope_ref=saved["scope_value"],
        )
        return saved, verses

    def delete_saved_search(self, identifier: str) -> bool:
        """Delete a saved search by ID from the current scope."""
        scope_id = self._scope_service.get_current_scope_id()
        # Try as ID
        deleted = self._repo.delete(identifier, scope_id)
        if not deleted:
            # Try as name
            saved = self._repo.get_by_name(identifier, scope_id)
            if saved:
                deleted = self._repo.delete(saved["id"], scope_id)
        return deleted
