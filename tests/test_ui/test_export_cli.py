"""Unit tests for unified --export parameter parsing."""

from pathlib import Path

import pytest

from clible.ui.export_cli import parse_export_string


def test_parse_export_all_keys_explicit():
    """parse_export_string with all keys returns ExportConfig."""
    config = parse_export_string(
        "PATH=~/exports,FILENAME=myfile,FORMAT=json",
        default_path=".",
        default_filename="default",
        default_format="md",
    )

    assert config.format == "json"
    assert config.path == Path("~/exports").expanduser()
    assert config.filename == "myfile"


def test_parse_export_uses_defaults_when_keys_missing():
    """parse_export_string with empty string or no keys uses defaults."""
    config = parse_export_string(
        "",
        default_path="/tmp",
        default_filename="test_file",
        default_format="csv",
    )

    assert config.format == "csv"
    assert config.path == Path("/tmp")
    assert config.filename == "test_file"


def test_parse_export_case_insensitive_keys():
    """parse_export_string accepts keys in any case."""
    config = parse_export_string(
        "format=xml,path=/home/user,filename=Result",
    )

    assert config.format == "xml"
    assert config.path == Path("/home/user")
    assert config.filename == "Result"


def test_parse_export_mixed_separators():
    """parse_export_string handles comma and space separators."""
    config = parse_export_string(
        "PATH=/tmp FILENAME=output FORMAT=html",
    )

    assert config.format == "html"
    assert config.path == Path("/tmp")
    assert config.filename == "output"


def test_parse_export_partial_keys_fills_with_defaults():
    """parse_export_string with only FORMAT uses defaults for PATH and FILENAME."""
    config = parse_export_string(
        "FORMAT=txt",
        default_path=".",
        default_filename="generated",
        default_format="md",
    )

    assert config.format == "txt"
    assert config.path == Path(".")
    assert config.filename == "generated"


def test_parse_export_rejects_unknown_key():
    """parse_export_string raises ValueError for unknown keys."""
    with pytest.raises(ValueError, match="Unknown export key"):
        parse_export_string("FORMAT=json,OUTPUT=/tmp,UNKNOWN=value")


def test_parse_export_rejects_unsupported_format():
    """parse_export_string raises ValueError for unsupported format."""
    with pytest.raises(ValueError, match="Unsupported FORMAT"):
        parse_export_string("FORMAT=pdf,PATH=/tmp")


def test_export_config_resolve_appends_format_extension():
    """ExportConfig.resolve() builds path with format extension."""
    from clible.ui.export_cli import ExportConfig

    config = ExportConfig(path=Path("/tmp"), filename="test", format="json")
    resolved = config.resolve()

    assert resolved == Path("/tmp/test.json")


def test_export_config_resolve_strips_existing_extension():
    """ExportConfig.resolve() removes existing extension before adding format."""
    from clible.ui.export_cli import ExportConfig

    config = ExportConfig(path=Path("/tmp"), filename="test.old", format="xml")
    resolved = config.resolve()

    assert resolved == Path("/tmp/test.xml")


def test_parse_export_with_tilde_expands_home_dir():
    """parse_export_string expands ~ in PATH."""
    config = parse_export_string("PATH=~/exports,FORMAT=json")

    assert "~" not in str(config.path)
    assert str(config.path).startswith("/home") or str(config.path).startswith("/Users")
