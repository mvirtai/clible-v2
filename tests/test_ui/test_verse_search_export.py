"""Unit tests for verse and search export serializers."""

import json

from clible.ui.verse_search_export import export_verses_bundle


def test_export_verse_json_includes_type_and_verses():
    """export_verses_bundle with kind=verse creates valid JSON."""
    verses = [
        {"book_id": "JHN", "chapter": 3, "verse": 16, "text": "For God so loved"},
        {"book_id": "JHN", "chapter": 3, "verse": 17, "text": "For God sent"},
    ]

    result = export_verses_bundle(
        verses,
        kind="verse",
        title="John 3:16-17",
        format="json",
        translation_id="web",
    )

    data = json.loads(result)
    assert data["type"] == "verse_lookup"
    assert data["title"] == "John 3:16-17"
    assert data["translation_id"] == "web"
    assert len(data["verses"]) == 2
    assert data["verses"][0]["book_id"] == "JHN"


def test_export_search_json_includes_query_and_stats():
    """export_verses_bundle with kind=search includes search metadata."""
    verses = [
        {"book_id": "JHN", "chapter": 1, "verse": 14, "text": "Full of grace"},
    ]
    stats = {"total_occurrences": 2, "unique_verses": 1, "books_with_matches": 1}

    result = export_verses_bundle(
        verses,
        kind="search",
        title="Search: grace",
        format="json",
        translation_id="web",
        search_word="grace",
        scope="bible",
        scope_ref=None,
        stats=stats,
    )

    data = json.loads(result)
    assert data["type"] == "search"
    assert data["query"] == "grace"
    assert data["scope"] == "bible"
    assert data["statistics"]["total_occurrences"] == 2


def test_export_verse_txt_is_human_readable():
    """export_verses_bundle format=txt creates readable plain text."""
    verses = [
        {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "In the beginning"},
    ]

    result = export_verses_bundle(
        verses,
        kind="verse",
        title="Genesis 1:1",
        format="txt",
        translation_id="kjv",
    )

    assert "Genesis 1:1" in result
    assert "Translation: kjv" in result
    assert "GEN 1:1" in result
    assert "In the beginning" in result


def test_export_verse_xml_is_valid():
    """export_verses_bundle format=xml creates valid XML structure."""
    verses = [
        {"book_id": "PSA", "chapter": 23, "verse": 1, "text": "The LORD is my shepherd"},
    ]

    result = export_verses_bundle(
        verses,
        kind="verse",
        title="Psalm 23:1",
        format="xml",
        translation_id="web",
    )

    assert '<?xml version="1.0"' in result
    assert "<clible-export" in result
    assert 'kind="verse"' in result
    assert "<title>Psalm 23:1</title>" in result
    assert "<translation-id>web</translation-id>" in result
    assert 'book="PSA"' in result
    assert 'chapter="23"' in result
    assert 'verse="1"' in result


def test_export_search_csv_has_consistent_header():
    """export_verses_bundle format=csv produces consistent column structure."""
    verses = [
        {"book_id": "JHN", "chapter": 3, "verse": 16, "text": "For God so loved"},
    ]

    result = export_verses_bundle(
        verses,
        kind="search",
        title="Search: loved",
        format="csv",
        translation_id="web",
        search_word="loved",
        scope="bible",
        scope_ref=None,
        stats={"total_occurrences": 1, "unique_verses": 1, "books_with_matches": 1},
    )

    lines = [line.rstrip("\r") for line in result.strip().split("\n")]
    assert lines[0] == "book_id,chapter,verse,text"
    assert "JHN,3,16" in lines[1]


def test_export_verse_md_includes_heading_and_sections():
    """export_verses_bundle format=md creates markdown with sections."""
    verses = [
        {"book_id": "MAT", "chapter": 5, "verse": 3, "text": "Blessed are the poor"},
    ]

    result = export_verses_bundle(
        verses,
        kind="verse",
        title="Matthew 5:3",
        format="md",
        translation_id="web",
    )

    assert result.startswith("# Matthew 5:3")
    assert "**Translation:** `web`" in result
    assert "## Verses" in result
    assert "### MAT 5:3" in result


def test_export_search_html_includes_statistics_table():
    """export_verses_bundle format=html with stats renders table."""
    verses = [
        {"book_id": "ROM", "chapter": 8, "verse": 28, "text": "All things work together"},
    ]
    stats = {
        "total_occurrences": 5,
        "unique_verses": 3,
        "books_with_matches": 2,
        "top_books": [("ROM", 3), ("JHN", 2)],
    }

    result = export_verses_bundle(
        verses,
        kind="search",
        title="Search: work",
        format="html",
        translation_id="web",
        search_word="work",
        scope="testament",
        scope_ref="NT",
        stats=stats,
    )

    assert "<!doctype html>" in result.lower()
    assert "<h2>Statistics</h2>" in result
    assert "Total occurrences</td><td>5</td>" in result
    assert "Unique verses</td><td>3</td>" in result
