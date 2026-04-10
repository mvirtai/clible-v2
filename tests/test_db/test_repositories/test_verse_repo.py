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


def test_search_text_finds_matching_verses(verse_repo, translation_repo):
    """search_text finds verses containing the search word using FTS5."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verses = [
        {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "In the beginning God created"},
        {"book_id": "GEN", "chapter": 1, "verse": 2, "text": "And the earth was without form"},
        {"book_id": "JHN", "chapter": 1, "verse": 1, "text": "In the beginning was the Word"},
    ]
    verse_repo.save_verses(verses, "web")

    results = verse_repo.search_text("beginning")
    assert len(results) == 2
    assert results[0]["book_id"] == "GEN"
    assert results[1]["book_id"] == "JHN"


def test_search_text_is_case_insensitive(verse_repo, translation_repo):
    """search_text is case-insensitive."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [{"book_id": "GEN", "chapter": 1, "verse": 1, "text": "God created the heavens"}],
        "web",
    )

    results = verse_repo.search_text("GOD")
    assert len(results) == 1
    assert "God" in results[0]["text"]


def test_search_text_filters_by_translation(verse_repo, translation_repo):
    """search_text filters by translation_id when provided."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    translation_repo.create(
        {
            "id": "kjv",
            "name": "King James Version",
            "language": "en",
            "format": "USFX",
        }
    )
    verses_web = [
        {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "In the beginning God created"},
    ]
    verses_kjv = [
        {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "In the beginning God made"},
    ]
    verse_repo.save_verses(verses_web, "web")
    verse_repo.save_verses(verses_kjv, "kjv")

    results_web = verse_repo.search_text("created", "web")
    results_kjv = verse_repo.search_text("created", "kjv")
    results_all = verse_repo.search_text("beginning")

    assert len(results_web) == 1
    assert results_web[0]["translation_id"] == "web"
    assert len(results_kjv) == 0
    assert len(results_all) == 2


def test_search_text_filters_by_book_id(verse_repo, translation_repo):
    """search_text restricts to book_id when provided."""
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
            {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "God said light"},
            {"book_id": "JHN", "chapter": 1, "verse": 1, "text": "God was the Word"},
        ],
        "web",
    )
    results = verse_repo.search_text("God", "web", book_id="JHN")
    assert len(results) == 1
    assert results[0]["book_id"] == "JHN"


def test_search_text_filters_by_chapter_and_verse_range(verse_repo, translation_repo):
    """search_text applies chapter and verse range in SQL."""
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
            {"book_id": "JHN", "chapter": 3, "verse": 15, "text": "Moses lifted serpent"},
            {"book_id": "JHN", "chapter": 3, "verse": 16, "text": "God so loved the world"},
            {"book_id": "JHN", "chapter": 3, "verse": 17, "text": "God sent the Son"},
        ],
        "web",
    )
    results = verse_repo.search_text(
        "God",
        "web",
        book_id="JHN",
        chapter=3,
        verse_min=16,
        verse_max=16,
    )
    assert len(results) == 1
    assert results[0]["verse"] == 16


def test_search_text_returns_empty_when_no_match(verse_repo, translation_repo):
    """search_text returns empty list when no verses match."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [{"book_id": "GEN", "chapter": 1, "verse": 1, "text": "In the beginning"}],
        "web",
    )

    results = verse_repo.search_text("nonexistent")
    assert results == []


def test_get_book_verses_returns_all_verses_in_book(verse_repo, translation_repo):
    """get_book_verses returns all verses in a book ordered by chapter and verse."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verses = [
        {"book_id": "JHN", "chapter": 1, "verse": 1, "text": "Ch1V1"},
        {"book_id": "JHN", "chapter": 1, "verse": 2, "text": "Ch1V2"},
        {"book_id": "JHN", "chapter": 2, "verse": 1, "text": "Ch2V1"},
        {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "GenCh1V1"},
    ]
    verse_repo.save_verses(verses, "web")

    result = verse_repo.get_book_verses("web", "JHN")
    assert len(result) == 3
    assert result[0]["chapter"] == 1
    assert result[0]["verse"] == 1
    assert result[1]["chapter"] == 1
    assert result[1]["verse"] == 2
    assert result[2]["chapter"] == 2
    assert result[2]["verse"] == 1


def test_get_book_verses_returns_empty_for_nonexistent_book(verse_repo, translation_repo):
    """get_book_verses returns empty list when book has no verses."""
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

    result = verse_repo.get_book_verses("web", "JHN")
    assert result == []


def test_get_book_verses_filters_by_translation(verse_repo, translation_repo):
    """get_book_verses only returns verses for the specified translation."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    translation_repo.create(
        {
            "id": "kjv",
            "name": "King James Version",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [{"book_id": "JHN", "chapter": 1, "verse": 1, "text": "Web text"}],
        "web",
    )
    verse_repo.save_verses(
        [{"book_id": "JHN", "chapter": 1, "verse": 1, "text": "KJV text"}],
        "kjv",
    )

    result = verse_repo.get_book_verses("web", "JHN")
    assert len(result) == 1
    assert result[0]["translation_id"] == "web"


def test_search_text_handles_invalid_fts5_syntax(verse_repo, translation_repo):
    """search_text falls back to literal phrase search when FTS5 syntax fails."""
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
            {"book_id": "ACT", "chapter": 1, "verse": 13, "text": "They went up into the upper room"},
            {"book_id": "JHN", "chapter": 3, "verse": 16, "text": "ACT 1:13"},
        ],
        "web",
    )

    # "1:13" triggers a "no such column: 1" OperationalError in FTS5 because of the colon.
    # We expect the repository to catch this and fall back to searching literally.
    results = verse_repo.search_text("ACT 1:13")
    assert len(results) == 1
    assert results[0]["book_id"] == "JHN"
    assert results[0]["text"] == "ACT 1:13"
