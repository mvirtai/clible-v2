"""Tests for export I/O, shared helpers, and scope title parsing."""

from pathlib import Path

import pytest

from clible.ui.export.io import (
    detect_format,
    resolve_output_path,
    validate_export_format,
    write_text,
)
from clible.ui.export.scope import parse_and_format_scope
from clible.ui.export.shared import (
    format_title_with_acronym,
    load_book_names,
    stringify_number,
    xml_document,
)


def test_detect_format_supports_htm_alias():
    assert detect_format(Path("report.HTM")) == "html"


def test_detect_format_raises_without_extension():
    with pytest.raises(ValueError, match="Missing file extension"):
        detect_format(Path("report"))


def test_detect_format_raises_for_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported --output format"):
        detect_format(Path("report.pdf"))


def test_validate_export_format_normalizes_htm():
    assert validate_export_format("HTM") == "html"


def test_validate_export_format_raises_for_unknown():
    with pytest.raises(ValueError, match="Unsupported format"):
        validate_export_format("docx")


def test_resolve_output_path_uses_explicit_format_over_suffix():
    path, fmt = resolve_output_path("notes.old", "json")
    assert str(path).endswith("notes.json")
    assert fmt == "json"


def test_resolve_output_path_infers_from_suffix():
    path, fmt = resolve_output_path("notes.csv", None)
    assert path == Path("notes.csv")
    assert fmt == "csv"


def test_write_text_creates_parents_and_writes_utf8(tmp_path: Path):
    target = tmp_path / "nested" / "out" / "file.txt"
    write_text(target, "hei maailma")
    assert target.read_text(encoding="utf-8") == "hei maailma"


def test_stringify_number_formats_float_and_intlike():
    assert stringify_number(1.5) == "1.5"
    assert stringify_number(2.0) == "2"
    assert stringify_number(7) == "7"


def test_format_title_with_acronym_uses_localized_name(monkeypatch: pytest.MonkeyPatch):
    class _Cfg:
        ui_language = "fi"

    monkeypatch.setattr("clible.ui.export.shared.get_config", lambda: _Cfg())
    monkeypatch.setattr(
        "clible.ui.export.shared.get_display_name", lambda bid, lang: f"{bid}-{lang}"
    )
    full, acronym = format_title_with_acronym("JHN", 3, 16)
    assert full == "JHN-fi 3:16"
    assert acronym == "(JHN 3:16)"


def test_xml_document_adds_declaration():
    import xml.etree.ElementTree as ET

    root = ET.Element("root")
    ET.SubElement(root, "child").text = "x"
    doc = xml_document(root)
    assert doc.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "<root>" in doc
    assert "<child>x</child>" in doc


def test_load_book_names_reads_and_caches(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("clible.ui.export.shared._BOOK_NAMES_CACHE", None)
    first = load_book_names()
    second = load_book_names()
    assert isinstance(first, dict)
    assert first is second
    assert "GEN" in first


def test_parse_and_format_scope_returns_original_when_not_reference():
    full, acronym = parse_and_format_scope("Whole Bible")
    assert full == "Whole Bible"
    assert acronym == ""


def test_parse_and_format_scope_uses_resolved_book_id(monkeypatch: pytest.MonkeyPatch):
    class _Cfg:
        ui_language = "en"

    monkeypatch.setattr("clible.ui.export.scope.get_config", lambda: _Cfg())
    monkeypatch.setattr("clible.ui.export.scope.resolve_book_id", lambda _: "JHN")
    monkeypatch.setattr("clible.ui.export.scope.get_display_name", lambda bid, lang: "John")
    full, acronym = parse_and_format_scope("John 3:16-17")
    assert full == "John 3:16-17"
    assert acronym == "(JHN 3:16-17)"


def test_parse_and_format_scope_falls_back_to_structure_name_match(
    monkeypatch: pytest.MonkeyPatch,
):
    class _Cfg:
        ui_language = "en"

    monkeypatch.setattr("clible.ui.export.scope.get_config", lambda: _Cfg())
    monkeypatch.setattr("clible.ui.export.scope.resolve_book_id", lambda _: None)
    monkeypatch.setattr("clible.ui.export.scope._load_book_names", lambda: {"GEN": "Genesis"})
    monkeypatch.setattr("clible.ui.export.scope.get_display_name", lambda bid, lang: "Genesis")
    full, acronym = parse_and_format_scope("genesis 1:1")
    assert full == "Genesis 1:1"
    assert acronym == "(GEN 1:1)"


def test_parse_and_format_scope_id_branch_when_resolver_none(
    monkeypatch: pytest.MonkeyPatch,
):
    class _Cfg:
        ui_language = "en"

    monkeypatch.setattr("clible.ui.export.scope.get_config", lambda: _Cfg())
    monkeypatch.setattr("clible.ui.export.scope.resolve_book_id", lambda _: None)
    monkeypatch.setattr("clible.ui.export.scope._load_book_names", lambda: {"GEN": "Genesis"})
    monkeypatch.setattr("clible.ui.export.scope.get_display_name", lambda bid, lang: "Genesis")
    full, acronym = parse_and_format_scope("GEN 1:2")
    assert full == "Genesis 1:2"
    assert acronym == "(GEN 1:2)"


def test_parse_and_format_scope_returns_original_for_unresolved_reference(
    monkeypatch: pytest.MonkeyPatch,
):
    class _Cfg:
        ui_language = "en"

    monkeypatch.setattr("clible.ui.export.scope.get_config", lambda: _Cfg())
    monkeypatch.setattr("clible.ui.export.scope.resolve_book_id", lambda _: None)
    monkeypatch.setattr("clible.ui.export.scope._load_book_names", lambda: {"GEN": "Genesis"})
    full, acronym = parse_and_format_scope("Unknownbook 2:3")
    assert full == "Unknownbook 2:3"
    assert acronym == ""
