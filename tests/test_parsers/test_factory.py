"""Tests for parser factory."""

from pathlib import Path

import pytest

from clible.parsers.beblia_parser import BebliaParser
from clible.parsers.factory import create_parser
from clible.parsers.osis_parser import OSISParser
from clible.parsers.usfx_parser import USFXParser
from clible.parsers.zefania_parser import ZefaniaParser

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_create_parser_detects_usfx():
    """create_parser returns USFXParser for USFX XML."""
    parser = create_parser(FIXTURES_DIR / "sample.usfx.xml")
    assert isinstance(parser, USFXParser)


def test_create_parser_detects_osis():
    """create_parser returns OSISParser for OSIS XML."""
    parser = create_parser(FIXTURES_DIR / "sample.osis.xml")
    assert isinstance(parser, OSISParser)


def test_create_parser_detects_osis_milestone():
    """create_parser returns OSISParser for milestone-style OSIS XML."""
    parser = create_parser(FIXTURES_DIR / "sample_milestone.osis.xml")
    assert isinstance(parser, OSISParser)


def test_create_parser_detects_beblia():
    """create_parser returns BebliaParser for Beblia XML."""
    parser = create_parser(FIXTURES_DIR / "sample.beblia.xml")
    assert isinstance(parser, BebliaParser)


def test_create_parser_detects_zefania():
    """create_parser returns ZefaniaParser for Zefania XML."""
    parser = create_parser(FIXTURES_DIR / "sample.zefania.xml")
    assert isinstance(parser, ZefaniaParser)


def test_create_parser_rejects_unknown_format(tmp_path):
    """create_parser raises ValueError for unknown root element."""
    unknown_xml = tmp_path / "unknown.xml"
    unknown_xml.write_text('<?xml version="1.0"?><unknown><data>test</data></unknown>')
    with pytest.raises(ValueError, match="Unsupported XML format.*unknown"):
        create_parser(unknown_xml)


def test_create_parser_rejects_malformed_xml(tmp_path):
    """create_parser raises ValueError for malformed XML."""
    bad_xml = tmp_path / "bad.xml"
    bad_xml.write_text("not xml at all")
    with pytest.raises(ValueError, match="Malformed XML"):
        create_parser(bad_xml)


def test_create_parser_rejects_bible_without_testament(tmp_path):
    """create_parser raises ValueError for <bible> without <testament> (not Beblia)."""
    non_beblia = tmp_path / "non_beblia.xml"
    non_beblia.write_text(
        '<?xml version="1.0"?><bible><book number="1"><verse>text</verse></book></bible>'
    )
    with pytest.raises(ValueError, match="Unknown <bible> format variant"):
        create_parser(non_beblia)
