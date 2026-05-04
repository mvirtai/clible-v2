"""Search history orchestration (delegates to SearchHistoryRepo)."""

from clible.db.repositories.search_history_repo import SearchHistoryRepo, SearchHistoryRow
from clible.services.search_query import SearchQuery


class SearchHistoryService:
    """Records and retrieves search history."""

    def __init__(self, repo: SearchHistoryRepo):
        self._repo = repo

    def record(self, query: SearchQuery, result_count: int) -> str:
        """Persist one completed search. Returns the new row id."""
        term_display = " ".join(query.terms).strip()
        return self._repo.record(
            query_text=term_display,
            search_scope=query.scope,
            scope_value=query.scope_ref,
            translation_id=query.translation_id,
            mode=query.mode,
            result_count=result_count,
        )

    def list_recent(self, limit: int = 10) -> list[SearchHistoryRow]:
        """Most recent searches first."""
        return self._repo.list_recent(limit)

    def clear(self) -> int:
        """Delete all history rows."""
        return self._repo.clear()
