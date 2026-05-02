"""Shared pytest fixtures for clible tests.

Provides in-memory SQLite connections with full app schema (migrations +
seed_books). Repository tests use these fixtures so they operate against
the real schema without touching the filesystem or config db_path.
"""

import pytest
import structlog

from clible.db.connection import get_connection
from clible.db.repositories.book_repo import BookRepo
from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo


@pytest.fixture
def db_conn():
    """In-memory SQLite connection with migrations applied and books seeded.

    Each test gets a fresh database. Use this for repository tests that need
    the full schema (books, translations, verses).
    """
    conn = get_connection(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def translation_repo(db_conn):
    """TranslationRepo wired to a fresh in-memory database."""
    return TranslationRepo(db_conn)


@pytest.fixture
def book_repo(db_conn):
    """BookRepo wired to a fresh in-memory database (books table seeded)."""
    return BookRepo(db_conn)


@pytest.fixture
def verse_repo(db_conn):
    """VerseRepo wired to a fresh in-memory database."""
    return VerseRepo(db_conn)


@pytest.fixture(autouse=True)
def _silent_structlog():
    """Silence structlog during tests (drop all events; no stderr noise)."""

    def _drop_all(_logger, _method_name, _event_dict):
        raise structlog.DropEvent

    structlog.configure(
        processors=[_drop_all],
        wrapper_class=structlog.BoundLogger,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
