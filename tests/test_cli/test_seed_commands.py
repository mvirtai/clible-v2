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
