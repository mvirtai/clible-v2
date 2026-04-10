"""CLI command modules and shared wiring helpers."""

from clible.db.connection import get_connection
from clible.db.repositories.book_repo import BookRepo
from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo
from clible.db.repositories.scope_repo import ScopeRepo
from clible.db.repositories.saved_search_repo import SavedSearchRepo
from clible.db.repositories.saved_analysis_repo import SavedAnalysisRepo
from clible.services.verse_service import VerseService
from clible.services.scope_service import ScopeService
from clible.services.saved_search_service import SavedSearchService
from clible.services.saved_analysis_service import SavedAnalysisService
from clible.services.analytic_service import AnalyticService
from clible.config import get_config


def get_verse_service() -> VerseService:
    """Build VerseService with real dependencies (shared across commands)."""
    conn = get_connection()
    return VerseService(
        verse_repo=VerseRepo(conn),
        book_repo=BookRepo(conn),
        translation_repo=TranslationRepo(conn),
    )


def get_scope_service() -> ScopeService:
    """Build ScopeService with real dependencies."""
    conn = get_connection()
    return ScopeService(
        scope_repo=ScopeRepo(conn),
        config=get_config(),
    )


def get_saved_search_service() -> SavedSearchService:
    """Build SavedSearchService with real dependencies."""
    conn = get_connection()
    scope_service = get_scope_service()
    verse_service = get_verse_service()
    return SavedSearchService(
        saved_search_repo=SavedSearchRepo(conn),
        scope_service=scope_service,
        verse_service=verse_service,
    )


def get_analytic_service(translation_id: str | None = None) -> AnalyticService:
    """Build AnalyticService with real dependencies."""
    # Note: Language detection logic from analytics.py could be moved here
    # but for SavedAnalysisService, we basically just need the service.
    verse_service = get_verse_service()
    return AnalyticService(verse_service=verse_service)


def get_saved_analysis_service() -> SavedAnalysisService:
    """Build SavedAnalysisService with real dependencies."""
    conn = get_connection()
    scope_service = get_scope_service()
    analytic_service = get_analytic_service()
    return SavedAnalysisService(
        saved_analysis_repo=SavedAnalysisRepo(conn),
        scope_service=scope_service,
        analytic_service=analytic_service,
    )
