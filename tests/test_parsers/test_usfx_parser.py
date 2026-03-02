"""Tests for USFX parser."""

from pathlib import Path

import pytest

from clible.parsers.usfx_parser import USFXParser

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def parser():
    """USFXParser instance for tests."""
    return USFXParser()


def test_parse_file_returns_list_of_verse_dicts(parser):
    """parse_file returns list of dicts with book_id, chapter, verse, text."""
    result = parser.parse_file(FIXTURES_DIR / "sample.usfx.xml")
    assert isinstance(result, list)
    assert len(result) == 5
    for verse in result:
        assert "book_id" in verse
        assert "chapter" in verse
        assert "verse" in verse
        assert "text" in verse


def test_parse_file_john_1_1_to_5(parser):
    """Sample fixture parses John 1:1-5 with correct content."""
    result = parser.parse_file(FIXTURES_DIR / "sample.usfx.xml")
    assert result[0] == {
        "book_id": "JHN",
        "chapter": 1,
        "verse": 1,
        "text": "In the beginning was the Word, and the Word was with God, and the Word was God.",
    }
    assert result[4]["verse"] == 5
    assert result[4]["text"] == (
        "The light shines in the darkness, and the darkness hasn't overcome it."
    )


def test_parse_file_strips_footnotes(parser):
    """Footnote content (<f>) is excluded from verse text."""
    result = parser.parse_file(FIXTURES_DIR / "sample.usfx.xml")
    verse_5 = next(v for v in result if v["verse"] == 5)
    assert "Footnote" not in verse_5["text"]
    assert "it." in verse_5["text"]


def test_parse_file_skips_frt_book(parser):
    """Front matter (FRT) book is not parsed."""
    result = parser.parse_file(FIXTURES_DIR / "sample_with_frt.usfx.xml")
    assert not any(v["book_id"] == "FRT" for v in result)
    assert len(result) == 1
    assert result[0]["book_id"] == "JHN"


def test_parse_file_real_genesis_1_1(parser):
    """Real eng-web.usfx.xml parses Genesis 1:1 correctly."""
    xml_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "clible"
        / "data"
        / "eng-web.usfx.xml"
    )
    if not xml_path.exists():
        pytest.skip("eng-web.usfx.xml not found")
    result = parser.parse_file(xml_path)
    gen_1_1 = next(
        (
            v
            for v in result
            if v["book_id"] == "GEN" and v["chapter"] == 1 and v["verse"] == 1
        ),
        None,
    )
    assert gen_1_1 is not None
    assert "In the beginning" in gen_1_1["text"]
    assert "God" in gen_1_1["text"]


def test_parse_file_real_genesis_strips_footnotes(parser):
    """Genesis verses with footnotes have footnote content stripped."""
    xml_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "clible"
        / "data"
        / "eng-web.usfx.xml"
    )
    if not xml_path.exists():
        pytest.skip("eng-web.usfx.xml not found")
    result = parser.parse_file(xml_path)
    gen_1_1 = next(
        (
            v
            for v in result
            if v["book_id"] == "GEN" and v["chapter"] == 1 and v["verse"] == 1
        ),
        None,
    )
    assert gen_1_1 is not None
    assert "Elohim" not in gen_1_1["text"]
    assert "אֱלֹהִ֑ים" not in gen_1_1["text"]
