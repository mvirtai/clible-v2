"""CLI integration tests for seed commands."""

import tempfile

import pytest
from click.testing import CliRunner

from clible import config as config_module
from clible.cli import main


@pytest.fixture(autouse=True)
def cli_uses_temp_db(monkeypatch):
    """Use a temp DB for CLI tests to avoid touching the dev database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_path = f.name
    monkeypatch.setattr(config_module.config, "db_path", tmp_path)
    yield
    try:
        import os

        os.unlink(tmp_path)
    except OSError:
        pass


def test_seed_available_outputs_table(cli_uses_temp_db):
    """seed available prints a table of translations."""
    runner = CliRunner()
    result = runner.invoke(main, ["seed", "available", "--query", "web", "--limit", "0"])
    assert result.exit_code == 0
    assert "web" in result.output
    assert "World English Bible" in result.output


def test_seed_available_filter_zefania(cli_uses_temp_db):
    """seed available supports filtering by ZEFANIA format."""
    runner = CliRunner()
    result = runner.invoke(main, ["seed", "available", "--format", "ZEFANIA", "--limit", "0"])
    assert result.exit_code == 0
    assert "test-zefania" in result.output


def test_seed_available_filter_language_fi(cli_uses_temp_db):
    """seed available supports filtering by language code."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["seed", "available", "--language", "fi", "--limit", "0"],
    )
    assert result.exit_code == 0
    assert "fin-1992" in result.output


def test_seed_available_query_world_english_bible_uses_default_limit(cli_uses_temp_db):
    """seed available search by name works with default limit."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["seed", "available", "--query", "World English Bible"],
    )
    assert result.exit_code == 0
    assert "web" in result.output
    assert "World English Bible" in result.output


def test_seed_available_offset_past_matches_shows_no_rows(cli_uses_temp_db):
    """seed available offset skips matches and can produce an empty table."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "seed",
            "available",
            "--query",
            "World English Bible",
            "--limit",
            "1",
            "--offset",
            "1",
        ],
    )
    assert result.exit_code == 0
    assert "web" not in result.output


def test_seed_list_empty_shows_hint(cli_uses_temp_db):
    """seed list shows hint when no translations installed."""
    runner = CliRunner()
    result = runner.invoke(main, ["seed", "list"])
    assert result.exit_code == 0
    assert "No translations installed" in result.output or "install web" in result.output


def test_verse_command_help():
    """verse command shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["verse", "--help"])
    assert result.exit_code == 0
    assert "REFERENCE" in result.output
    assert "translation" in result.output
