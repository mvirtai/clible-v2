"""Tests for VerseService."""

import pytest

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


def test_get_verse_with_range_returns_first_verse(verse_service, verse_repo, translation_repo):
    """get_verse with range (e.g. John 3:16-18) returns the first verse in range."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [
            {"book_id": "JHN", "chapter": 3, "verse": 16, "text": "For God so loved..."},
            {"book_id": "JHN", "chapter": 3, "verse": 17, "text": "For God sent..."},
            {"book_id": "JHN", "chapter": 3, "verse": 18, "text": "Whoever believes..."},
        ],
        "web",
    )
    result = verse_service.get_verse("John 3:16-18")
    assert result is not None
    assert result["verse"] == 16
    assert result["text"] == "For God so loved..."


def test_get_verse_returns_none_for_invalid_range(verse_service, verse_repo, translation_repo):
    """get_verse returns None when range is reversed (end < start)."""
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
    assert verse_service.get_verse("John 3:18-16") is None


def test_get_verse_single_verse_and_explicit_range_same_result(
    verse_service, verse_repo, translation_repo
):
    """get_verse('John 3:16') and get_verse('John 3:16-16') return the same verse."""
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
    single = verse_service.get_verse("John 3:16")
    range_same = verse_service.get_verse("John 3:16-16")
    assert single is not None
    assert range_same is not None
    assert single["id"] == range_same["id"]
    assert single["verse"] == range_same["verse"] == 16


# --- get_verses (range support) ---


def test_get_verses_returns_single_verse_for_single_reference(
    verse_service, verse_repo, translation_repo
):
    """get_verses with single reference returns list of one verse."""
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
    result = verse_service.get_verses("John 3:16", translation_id="web")
    assert len(result) == 1
    assert result[0]["verse"] == 16
    assert "For God so loved" in result[0]["text"]


def test_get_verses_returns_multiple_verses_for_range(verse_service, verse_repo, translation_repo):
    """get_verses with range (e.g. John 3:1-6) returns all verses in order."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [
            {"book_id": "JHN", "chapter": 3, "verse": 1, "text": "V1"},
            {"book_id": "JHN", "chapter": 3, "verse": 2, "text": "V2"},
            {"book_id": "JHN", "chapter": 3, "verse": 3, "text": "V3"},
            {"book_id": "JHN", "chapter": 3, "verse": 4, "text": "V4"},
            {"book_id": "JHN", "chapter": 3, "verse": 5, "text": "V5"},
            {"book_id": "JHN", "chapter": 3, "verse": 6, "text": "V6"},
        ],
        "web",
    )
    result = verse_service.get_verses("John 3:1-6", translation_id="web")
    assert len(result) == 6
    assert [r["verse"] for r in result] == [1, 2, 3, 4, 5, 6]
    assert result[0]["text"] == "V1"
    assert result[5]["text"] == "V6"


def test_get_verses_returns_empty_for_invalid_reference(verse_service):
    """get_verses returns empty list for malformed or invalid range."""
    assert verse_service.get_verses("not a reference") == []
    assert verse_service.get_verses("") == []
    assert verse_service.get_verses("John 3:18-16") == []


def test_get_verses_returns_empty_when_no_translation(verse_service, verse_repo):
    """get_verses returns empty list when no translation is installed."""
    result = verse_service.get_verses("John 3:16")
    assert result == []
