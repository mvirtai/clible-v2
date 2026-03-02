"""Tests for VerseService."""

import pytest

from clible.db.repositories.translation_repo import TranslationRepo
from clible.services.verse_service import VerseService


@pytest.fixture
def verse_service(verse_repo, book_repo, translation_repo):
    """VerseService with repo fixtures."""
    return VerseService(
        verse_repo=verse_repo,
        book_repo=book_repo,
        translation_repo=translation_repo,
    )


def test_get_verse_returns_none_when_empty(verse_service):
    """get_verse returns None when no verses installed."""
    assert verse_service.get_verse("John 3:16") is None


def test_get_verse_returns_verse_when_exists(verse_service, verse_repo, translation_repo):
    """get_verse returns verse when reference exists in DB."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [{"book_id": "JHN", "chapter": 3, "verse": 16, "text": "For God so loved..."}],
        "web",
    )
    result = verse_service.get_verse("John 3:16")
    assert result is not None
    assert result["text"] == "For God so loved..."


def test_get_verse_accepts_translation_override(verse_service, verse_repo, translation_repo):
    """get_verse uses --translation when provided."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [{"book_id": "GEN", "chapter": 1, "verse": 1, "text": "In the beginning..."}],
        "web",
    )
    result = verse_service.get_verse("Genesis 1:1", translation_id="web")
    assert result is not None
    assert "In the beginning" in result["text"]


def test_get_verse_returns_none_for_invalid_reference(verse_service):
    """get_verse returns None for malformed reference."""
    assert verse_service.get_verse("not a reference") is None
    assert verse_service.get_verse("") is None
