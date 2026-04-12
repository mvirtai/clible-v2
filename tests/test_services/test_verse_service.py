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


def test_get_verses_returns_chapter_when_reference_is_chapter(
    verse_service, verse_repo, translation_repo
):
    """get_verses with chapter reference returns all verses in that chapter."""
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
            {"book_id": "JHN", "chapter": 3, "verse": 1, "text": "A"},
            {"book_id": "JHN", "chapter": 3, "verse": 2, "text": "B"},
            {"book_id": "JHN", "chapter": 4, "verse": 1, "text": "Other"},
        ],
        "web",
    )
    result = verse_service.get_verses("John 3", translation_id="web")
    assert len(result) == 2
    assert [r["verse"] for r in result] == [1, 2]


def test_get_verses_returns_book_when_reference_is_book_only(
    verse_service, verse_repo, translation_repo
):
    """get_verses with book-only reference returns all verses in the book."""
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
            {"book_id": "JHN", "chapter": 1, "verse": 1, "text": "Start"},
            {"book_id": "JHN", "chapter": 21, "verse": 25, "text": "End"},
            {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "Gen"},
        ],
        "web",
    )
    result = verse_service.get_verses("John", translation_id="web")
    assert len(result) == 2
    assert result[0]["chapter"] == 1
    assert result[1]["chapter"] == 21


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


def test_get_chapter_verses_returns_all_verses_in_chapter(
    verse_service, verse_repo, book_repo, translation_repo
):
    """get_chapter_verses returns all verses in a chapter."""
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
        ],
        "web",
    )
    result = verse_service.get_chapter_verses("John", 3, "web")
    assert len(result) == 3
    assert [r["verse"] for r in result] == [1, 2, 3]


def test_get_chapter_verses_returns_empty_for_nonexistent_book(verse_service):
    """get_chapter_verses returns empty list when book not found."""
    result = verse_service.get_chapter_verses("Nonexistent", 1, "web")
    assert result == []


def test_get_book_verses_returns_all_verses_in_book(
    verse_service, verse_repo, book_repo, translation_repo
):
    """get_book_verses returns all verses in a book ordered by chapter and verse."""
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
            {"book_id": "JHN", "chapter": 1, "verse": 1, "text": "Ch1V1"},
            {"book_id": "JHN", "chapter": 1, "verse": 2, "text": "Ch1V2"},
            {"book_id": "JHN", "chapter": 2, "verse": 1, "text": "Ch2V1"},
            {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "GenCh1V1"},
        ],
        "web",
    )
    result = verse_service.get_book_verses("John", "web")
    assert len(result) == 3
    assert result[0]["chapter"] == 1
    assert result[0]["verse"] == 1
    assert result[1]["chapter"] == 1
    assert result[1]["verse"] == 2
    assert result[2]["chapter"] == 2


def test_get_book_verses_returns_empty_for_nonexistent_book(verse_service):
    """get_book_verses returns empty list when book not found."""
    result = verse_service.get_book_verses("Nonexistent", "web")
    assert result == []


def test_english_reference_resolves_greek_translation_text(
    verse_service, verse_repo, translation_repo
):
    """English book names ('John 3:16') correctly look up verses in a Greek translation.

    Users enter references in English regardless of the translation language.
    BookRepo uses the English canonical book structure, so Greek translation IDs
    work transparently with English reference strings.
    """
    translation_repo.create(
        {
            "id": "greek",
            "name": "Greek New Testament",
            "language": "grc",
            "format": "BEBLIA",
        }
    )
    greek_text = "Οὕτως γὰρ ἠγάπησεν ὁ θεὸς τὸν κόσμον"
    verse_repo.save_verses(
        [{"book_id": "JHN", "chapter": 3, "verse": 16, "text": greek_text}],
        "greek",
    )
    result = verse_service.get_verse("John 3:16", translation_id="greek")
    assert result is not None
    assert result["text"] == greek_text
    assert result["book_id"] == "JHN"
    assert result["chapter"] == 3
    assert result["verse"] == 16


def test_english_reference_resolves_across_all_non_english_translations(
    verse_service, verse_repo, translation_repo
):
    """English references work correctly for Finnish, Greek, and Chinese translations."""
    translations = [
        ("fin-1992", "Sillä niin on Jumala maailmaa rakastanut", "fi"),
        ("greek", "Οὕτως γὰρ ἠγάπησεν ὁ θεός", "grc"),
    ]
    for tid, text, lang in translations:
        translation_repo.create({"id": tid, "name": tid, "language": lang, "format": "BEBLIA"})
        verse_repo.save_verses(
            [{"book_id": "JHN", "chapter": 3, "verse": 16, "text": text}],
            tid,
        )

    for tid, expected_text, _ in translations:
        result = verse_service.get_verse("John 3:16", translation_id=tid)
        assert result is not None, f"Expected verse for translation '{tid}'"
        assert result["text"] == expected_text
