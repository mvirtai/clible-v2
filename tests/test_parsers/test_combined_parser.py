"""Tests for CombinedParser."""

import tempfile
from pathlib import Path

import pytest

from clible.parsers.combined_parser import CombinedParser

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def parser():
    """CombinedParser instance for tests."""
    return CombinedParser()


def test_parse_usfx_format(parser):
    """Detects and parses USFX format correctly."""
    result = parser.parse_file(FIXTURES_DIR / "sample.usfx.xml")
    assert len(result) == 5
    assert result[0]["book_id"] == "JHN"
    assert result[0]["chapter"] == 1
    assert result[0]["verse"] == 1
    assert "In the beginning was the Word" in result[0]["text"]


def test_parse_osis_format(parser):
    """Detects and parses OSIS format correctly."""
    result = parser.parse_file(FIXTURES_DIR / "sample.osis.xml")
    assert len(result) == 5
    assert result[0]["book_id"] == "GEN"
    assert result[0]["chapter"] == 1
    assert result[0]["verse"] == 1
    assert "Alussa loi Jumala" in result[0]["text"]


def test_parse_osis_milestone_format(parser):
    """Detects and parses OSIS milestone format correctly."""
    result = parser.parse_file(FIXTURES_DIR / "sample_milestone.osis.xml")
    assert len(result) == 2
    assert result[0]["book_id"] == "GEN"
    assert "In the beginning God created" in result[0]["text"]


def test_parse_beblia_format(parser):
    """Detects and parses Beblia format correctly."""
    result = parser.parse_file(FIXTURES_DIR / "sample.beblia.xml")
    assert len(result) == 2
    assert result[0]["book_id"] == "GEN"
    assert result[0]["chapter"] == 1
    assert result[0]["verse"] == 1
    assert result[0]["text"] == "Alussa Jumala loi taivaan ja maan."


def test_parse_zefania_format(parser):
    """Detects and parses Zefania format correctly."""
    result = parser.parse_file(FIXTURES_DIR / "sample.zefania.xml")
    assert len(result) == 4
    assert result[0]["book_id"] == "JHN"
    assert result[0]["chapter"] == 1
    assert result[0]["verse"] == 1
    assert (
        result[0]["text"]
        == "In the beginning was the Word, and the Word was with God, and the Word was God."
    )


def test_parse_fails_on_malformed_xml(parser):
    """Raises ValueError when XML is malformed."""
    with tempfile.NamedTemporaryFile(suffix=".xml", mode="w", delete=False) as tmp:
        tmp.write("<root><unclosed>")
        tmp_path = Path(tmp.name)

    try:
        with pytest.raises(ValueError, match="Malformed XML file"):
            parser.parse_file(tmp_path)
    finally:
        tmp_path.unlink()


def test_parse_fails_on_unknown_root_element(parser):
    """Raises ValueError when root element tag is not recognized."""
    with tempfile.NamedTemporaryFile(suffix=".xml", mode="w", delete=False) as tmp:
        tmp.write("<unknown_root><child/></unknown_root>")
        tmp_path = Path(tmp.name)

    try:
        with pytest.raises(ValueError, match="Unsupported XML format"):
            parser.parse_file(tmp_path)
    finally:
        tmp_path.unlink()


def test_parse_fails_on_bible_without_testament(parser):
    """Raises ValueError when root is <bible> but Beblia structure is missing."""
    with tempfile.NamedTemporaryFile(suffix=".xml", mode="w", delete=False) as tmp:
        tmp.write("<bible><something_else/></bible>")
        tmp_path = Path(tmp.name)

    try:
        with pytest.raises(ValueError, match="Unknown <bible> variant"):
            parser.parse_file(tmp_path)
    finally:
        tmp_path.unlink()
