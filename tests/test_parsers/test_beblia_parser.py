"""Tests for Beblia parser."""

from pathlib import Path

import pytest

from clible.parsers.beblia_parser import BebliaParser

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
SAMPLE_BEBLIA = FIXTURES_DIR / "sample.beblia.xml"


@pytest.fixture
def parser():
    """BebliaParser instance for tests."""
    return BebliaParser()


def test_parse_file_returns_list_of_verse_dicts(parser):
    """parse_file returns list of dicts with book_id, chapter, verse, text."""
    result = parser.parse_file(SAMPLE_BEBLIA)
    assert isinstance(result, list)
    assert len(result) == 2
    for verse in result:
        assert "book_id" in verse
        assert "chapter" in verse
        assert "verse" in verse
        assert "text" in verse


def test_parse_file_genesis_1_1_content(parser):
    """Sample fixture parses Genesis 1:1 (book number 1) with correct content."""
    result = parser.parse_file(SAMPLE_BEBLIA)
    assert result[0] == {
        "book_id": "GEN",
        "chapter": 1,
        "verse": 1,
        "text": "Alussa Jumala loi taivaan ja maan.",
    }


def test_parse_file_genesis_1_2(parser):
    """Second verse has correct book_id, chapter, verse and text."""
    result = parser.parse_file(SAMPLE_BEBLIA)
    assert result[1]["book_id"] == "GEN"
    assert result[1]["chapter"] == 1
    assert result[1]["verse"] == 2
    assert result[1]["text"] == "Maa oli autio ja tyhjä."


def test_parse_file_maps_book_number_to_clible_id(parser):
    """Book number 1 maps to GEN (canonical order)."""
    result = parser.parse_file(SAMPLE_BEBLIA)
    assert all(v["book_id"] == "GEN" for v in result)


def test_parse_file_skips_book_number_out_of_range(parser, tmp_path):
    """Books with number < 1 or > 66 are skipped."""
    xml = tmp_path / "bad.xml"
    xml.write_text(
        '<?xml version="1.0"?><bible><testament name="Old">'
        '<book number="0"><chapter number="1"><verse number="1">Skip.</verse></chapter></book>'
        '<book number="99"><chapter number="1"><verse number="1">Skip.</verse></chapter></book>'
        "</testament></bible>"
    )
    result = parser.parse_file(xml)
    assert result == []


def test_parse_file_empty_verse_text_still_included(parser, tmp_path):
    """Verse with empty or whitespace-only text is still returned."""
    xml = tmp_path / "empty.xml"
    xml.write_text(
        '<?xml version="1.0"?><bible><testament name="Old">'
        '<book number="1"><chapter number="1">'
        '<verse number="1">   </verse>'
        "</chapter></book></testament></bible>"
    )
    result = parser.parse_file(xml)
    assert len(result) == 1
    assert result[0]["book_id"] == "GEN"
    assert result[0]["verse"] == 1
    assert result[0]["text"] == ""
