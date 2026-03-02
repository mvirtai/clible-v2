"""Tests for OSIS parser."""

from pathlib import Path

import pytest

from clible.parsers.osis_parser import OSISParser

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
SAMPLE_OSIS = FIXTURES_DIR / "sample.osis.xml"
SAMPLE_MILESTONE = FIXTURES_DIR / "sample_milestone.osis.xml"


@pytest.fixture
def parser():
    """OSISParser instance for tests."""
    return OSISParser()


def test_parse_file_returns_list_of_verse_dicts(parser):
    """parse_file returns list of dicts with book_id, chapter, verse, text."""
    result = parser.parse_file(SAMPLE_OSIS)
    assert isinstance(result, list)
    assert len(result) == 5
    for verse in result:
        assert "book_id" in verse
        assert "chapter" in verse
        assert "verse" in verse
        assert "text" in verse


def test_parse_file_genesis_1_1_content(parser):
    """Sample fixture parses Genesis 1:1 with correct content."""
    result = parser.parse_file(SAMPLE_OSIS)
    assert result[0] == {
        "book_id": "GEN",
        "chapter": 1,
        "verse": 1,
        "text": "Alussa loi Jumala taivaan ja maan.",
    }


def test_parse_file_genesis_1_2_to_5(parser):
    """Verses 2-5 have correct book_id, chapter, verse and non-empty text."""
    result = parser.parse_file(SAMPLE_OSIS)
    assert result[1]["book_id"] == "GEN"
    assert result[1]["chapter"] == 1
    assert result[1]["verse"] == 2
    assert "Ja maa oli autio" in result[1]["text"]

    assert result[4]["verse"] == 5
    assert "Ja Jumala kutsui valkeuden päiväksi" in result[4]["text"]
    assert "Ja tuli ehtoo, ja tuli aamu, ensimmäinen päivä." in result[4]["text"]


def test_parse_file_strips_notes(parser):
    """Note content (<note>) is excluded from verse text."""
    result = parser.parse_file(SAMPLE_OSIS)
    verse_5 = next(v for v in result if v["verse"] == 5)
    assert "merkintä" not in verse_5["text"]
    assert "Ja tuli ehtoo" in verse_5["text"]


def test_parse_file_maps_osis_book_id_to_clible(parser):
    """OSIS book code Gen is mapped to clible book_id GEN."""
    result = parser.parse_file(SAMPLE_OSIS)
    assert all(v["book_id"] == "GEN" for v in result)


def test_parse_file_skips_verses_without_osis_id(parser):
    """Verses without osisID are skipped (no crash)."""
    result = parser.parse_file(SAMPLE_OSIS)
    assert len(result) == 5
    for v in result:
        assert v["book_id"] and v["chapter"] and v["verse"] and "text" in v


def test_parse_file_skips_unknown_books(parser, tmp_path):
    """Books not in OSIS_TO_CLIBLE map are skipped."""
    xml = tmp_path / "apoc.xml"
    xml.write_text(
        '<?xml version="1.0"?>'
        '<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace">'
        "<osisText><div type='book' osisID='Tob'>"
        "<chapter osisID='Tob.1'><verse osisID='Tob.1.1'>Apocrypha text.</verse></chapter>"
        "</div></osisText></osis>"
    )
    result = parser.parse_file(xml)
    assert result == []


def test_parse_file_invalid_osis_id_parts_skipped(parser, tmp_path):
    """Malformed osisID (e.g. only one part) does not crash; verse is skipped."""
    xml = tmp_path / "bad.xml"
    xml.write_text(
        '<?xml version="1.0"?>'
        '<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace">'
        "<osisText><div type='book' osisID='Gen'>"
        "<chapter osisID='Gen.1'>"
        "<verse osisID='Gen'>No chapter.verse.</verse>"
        "<verse osisID='Gen.1.1'>Valid.</verse>"
        "</chapter></div></osisText></osis>"
    )
    result = parser.parse_file(xml)
    assert len(result) == 1
    assert result[0]["book_id"] == "GEN"
    assert result[0]["chapter"] == 1
    assert result[0]["verse"] == 1
    assert "Valid" in result[0]["text"]


def test_parse_file_milestone_format_returns_verses(parser):
    """Milestone form (KJV-style) is parsed: verse sID/eID with text between."""
    result = parser.parse_file(SAMPLE_MILESTONE)
    assert len(result) == 2
    assert result[0]["book_id"] == "GEN"
    assert result[0]["chapter"] == 1
    assert result[0]["verse"] == 1
    assert result[1]["verse"] == 2


def test_parse_file_milestone_gen_1_1_text(parser):
    """Milestone Gen 1:1 has correct text from tail and siblings."""
    result = parser.parse_file(SAMPLE_MILESTONE)
    gen_1_1 = next(v for v in result if v["chapter"] == 1 and v["verse"] == 1)
    assert "In the beginning God created the heaven and the earth." in gen_1_1["text"]


def test_parse_file_milestone_includes_trans_change_text(parser):
    """Milestone verse text includes transChange content (e.g. KJV added words)."""
    result = parser.parse_file(SAMPLE_MILESTONE)
    gen_1_2 = next(v for v in result if v["verse"] == 2)
    assert "was" in gen_1_2["text"]
    assert "upon the face of the deep" in gen_1_2["text"]
