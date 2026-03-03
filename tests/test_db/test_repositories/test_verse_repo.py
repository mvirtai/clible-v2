"""Tests for VerseRepo.

Covers get_verse, get_verses, save_verses. Verses are keyed by translation_id +
book_id + chapter + verse. Tests require a translation to exist (FK constraint);
fixture creates one before verse operations.
"""

from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo


def test_get_verse_returns_none_when_empty(verse_repo: VerseRepo):
    """get_verse returns None when no verses exist (translation may not exist)."""
    result = verse_repo.get_verse("web", "GEN", 1, 1)
    assert result is None


def test_get_verses_returns_empty_list_when_empty(verse_repo: VerseRepo):
    """get_verses returns empty list when chapter has no verses."""
    result = verse_repo.get_verses("web", "GEN", 1)
    assert result == []


def test_save_verses_inserts_and_returns_count(
    verse_repo: VerseRepo,
    translation_repo: TranslationRepo,
):
    """save_verses inserts verses and returns the count. Requires translation FK."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verses = [
        {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "In the beginning..."},
        {"book_id": "GEN", "chapter": 1, "verse": 2, "text": "And the earth was..."},
    ]
    count = verse_repo.save_verses(verses, "web")
    assert count == 2


def test_get_verse_returns_saved_verse(
    verse_repo: VerseRepo,
    translation_repo: TranslationRepo,
):
    """get_verse returns the verse after save_verses."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verses = [
        {"book_id": "JHN", "chapter": 3, "verse": 16, "text": "For God so loved..."},
    ]
    verse_repo.save_verses(verses, "web")

    row = verse_repo.get_verse("web", "JHN", 3, 16)
    assert row is not None
    assert row["translation_id"] == "web"
    assert row["book_id"] == "JHN"
    assert row["chapter"] == 3
    assert row["verse"] == 16
    assert row["text"] == "For God so loved..."
    assert "id" in row
    assert len(row["id"]) > 0


def test_get_verse_returns_none_for_wrong_translation(
    verse_repo: VerseRepo,
    translation_repo: TranslationRepo,
):
    """get_verse returns None when translation_id does not match."""
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

    result = verse_repo.get_verse("kjv", "GEN", 1, 1)
    assert result is None


def test_get_verse_returns_none_for_wrong_reference(
    verse_repo: VerseRepo,
    translation_repo: TranslationRepo,
):
    """get_verse returns None when book/chapter/verse do not exist."""
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

    assert verse_repo.get_verse("web", "GEN", 1, 99) is None
    assert verse_repo.get_verse("web", "XXX", 1, 1) is None


def test_get_verses_returns_ordered_by_verse(
    verse_repo: VerseRepo,
    translation_repo: TranslationRepo,
):
    """get_verses returns verses ordered by verse number."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verses = [
        {"book_id": "GEN", "chapter": 1, "verse": 3, "text": "Verse 3"},
        {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "Verse 1"},
        {"book_id": "GEN", "chapter": 1, "verse": 2, "text": "Verse 2"},
    ]
    verse_repo.save_verses(verses, "web")

    result = verse_repo.get_verses("web", "GEN", 1)
    assert len(result) == 3
    assert [r["verse"] for r in result] == [1, 2, 3]
    assert result[0]["text"] == "Verse 1"


def test_get_verses_in_range_returns_subset_ordered(
    verse_repo: VerseRepo,
    translation_repo: TranslationRepo,
):
    """get_verses_in_range returns only verses in [verse_start, verse_end] inclusive, ordered."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verses = [
        {"book_id": "JHN", "chapter": 3, "verse": 1, "text": "V1"},
        {"book_id": "JHN", "chapter": 3, "verse": 2, "text": "V2"},
        {"book_id": "JHN", "chapter": 3, "verse": 3, "text": "V3"},
        {"book_id": "JHN", "chapter": 3, "verse": 4, "text": "V4"},
        {"book_id": "JHN", "chapter": 3, "verse": 5, "text": "V5"},
        {"book_id": "JHN", "chapter": 3, "verse": 6, "text": "V6"},
    ]
    verse_repo.save_verses(verses, "web")

    result = verse_repo.get_verses_in_range("web", "JHN", 3, 2, 4)
    assert len(result) == 3
    assert [r["verse"] for r in result] == [2, 3, 4]
    assert result[0]["text"] == "V2"
    assert result[-1]["text"] == "V4"


def test_get_verses_in_range_returns_empty_when_none_in_range(
    verse_repo: VerseRepo,
    translation_repo: TranslationRepo,
):
    """get_verses_in_range returns empty list when no verses in range exist."""
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
    result = verse_repo.get_verses_in_range("web", "JHN", 3, 1, 5)
    assert result == []


def test_get_verses_only_returns_matching_chapter(
    verse_repo: VerseRepo,
    translation_repo: TranslationRepo,
):
    """get_verses returns only verses from the requested chapter."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verses = [
        {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "Ch1V1"},
        {"book_id": "GEN", "chapter": 2, "verse": 1, "text": "Ch2V1"},
    ]
    verse_repo.save_verses(verses, "web")

    ch1 = verse_repo.get_verses("web", "GEN", 1)
    ch2 = verse_repo.get_verses("web", "GEN", 2)
    assert len(ch1) == 1
    assert len(ch2) == 1
    assert ch1[0]["text"] == "Ch1V1"
    assert ch2[0]["text"] == "Ch2V1"


def test_save_verses_generates_unique_ids(
    verse_repo: VerseRepo,
    translation_repo: TranslationRepo,
):
    """Each saved verse gets a unique id (UUID)."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verses = [
        {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "First"},
        {"book_id": "GEN", "chapter": 1, "verse": 2, "text": "Second"},
    ]
    verse_repo.save_verses(verses, "web")

    v1 = verse_repo.get_verse("web", "GEN", 1, 1)
    v2 = verse_repo.get_verse("web", "GEN", 1, 2)
    assert v1["id"] != v2["id"]


def test_save_verses_returns_plain_dicts(verse_repo: VerseRepo, translation_repo):
    """VerseRepo returns plain dicts, not sqlite3.Row."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [{"book_id": "GEN", "chapter": 1, "verse": 1, "text": "Text"}],
        "web",
    )
    row = verse_repo.get_verse("web", "GEN", 1, 1)
    assert isinstance(row, dict)
    assert type(row).__name__ != "Row"


def test_save_verses_empty_list_returns_zero(verse_repo, translation_repo):
    """save_verses with empty list returns 0."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    count = verse_repo.save_verses([], "web")
    assert count == 0
