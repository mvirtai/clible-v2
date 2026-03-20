"""Tests for Zefania parser."""

from pathlib import Path

import pytest

from clible.parsers.zefania_parser import ZefaniaParser

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def parser():
    """ZefaniaParser instance for tests."""
    return ZefaniaParser()


def test_parse_file_returns_list_of_verse_dicts(parser):
    """parse_file returns list of dicts with book_id, chapter, verse, text."""
    result = parser.parse_file(FIXTURES_DIR / "sample.zefania.xml")
    assert isinstance(result, list)
    assert len(result) == 4
    for verse in result:
        assert "book_id" in verse
        assert "chapter" in verse
        assert "verse" in verse
        assert "text" in verse


def test_parse_file_john_1_1(parser):
    """Sample fixture parses John 1:1 with correct content."""
    result = parser.parse_file(FIXTURES_DIR / "sample.zefania.xml")
    assert result[0] == {
        "book_id": "JHN",
        "chapter": 1,
        "verse": 1,
        "text": "In the beginning was the Word, and the Word was with God, and the Word was God.",
    }


def test_parse_file_john_3_16(parser):
    """Sample fixture parses John 3:16 with correct content."""
    result = parser.parse_file(FIXTURES_DIR / "sample.zefania.xml")
    john_3_16 = next(v for v in result if v["chapter"] == 3 and v["verse"] == 16)
    assert john_3_16["book_id"] == "JHN"
    assert "God so loved the world" in john_3_16["text"]


def test_parse_file_maps_bnumber_to_book_id(parser):
    """Book number 43 maps to JHN (John is 43rd in canonical order)."""
    result = parser.parse_file(FIXTURES_DIR / "sample.zefania.xml")
    assert all(v["book_id"] == "JHN" for v in result)


def test_parse_file_skips_invalid_bnumber(tmp_path):
    """Books with invalid bnumber (out of 1-66 range) are skipped."""
    xml = tmp_path / "invalid.xml"
    xml.write_text(
        '<?xml version="1.0"?>'
        '<XMLBIBLE><BIBLEBOOK bnumber="999">'
        '<CHAPTER cnumber="1"><VERS vnumber="1">text</VERS></CHAPTER>'
        "</BIBLEBOOK></XMLBIBLE>"
    )
    parser = ZefaniaParser()
    result = parser.parse_file(xml)
    assert len(result) == 0


def test_parse_file_handles_missing_attributes(tmp_path):
    """Verses with missing or invalid attributes are skipped gracefully."""
    xml = tmp_path / "missing.xml"
    xml.write_text(
        '<?xml version="1.0"?>'
        '<XMLBIBLE><BIBLEBOOK bnumber="1">'
        '<CHAPTER cnumber="1">'
        '<VERS vnumber="1">Valid verse</VERS>'
        "<VERS>Missing vnumber</VERS>"
        '<VERS vnumber="abc">Invalid vnumber</VERS>'
        "</CHAPTER></BIBLEBOOK></XMLBIBLE>"
    )
    parser = ZefaniaParser()
    result = parser.parse_file(xml)
    assert len(result) == 1
    assert result[0]["verse"] == 1
    assert result[0]["text"] == "Valid verse"
