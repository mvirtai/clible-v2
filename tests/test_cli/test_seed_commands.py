"""CLI integration tests for seed commands."""

import json
import tempfile

import pytest
from click.testing import CliRunner

from clible import config as config_module
from clible.cli import main
from clible.db.connection import get_connection
from clible.db.repositories.translation_repo import TranslationRepo


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


def test_seed_available_json_returns_filtered_rows(cli_uses_temp_db):
    """seed available --json returns filtered translations."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "seed",
            "available",
            "--json",
            "--query",
            "World English Bible",
            "--limit",
            "1",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(result.output.strip())
    assert len(data) == 1
    assert data[0]["id"] == "web"
    assert data[0]["name"] == "World English Bible"
    assert data[0]["language"] == "en"
    assert data[0]["format"] == "USFX"
    assert "size_mb" in data[0]


def test_seed_available_json_limit_zero_returns_many(cli_uses_temp_db):
    """seed available --json supports limit=0 for all matches."""
    runner = CliRunner()
    result = runner.invoke(main, ["seed", "available", "--json", "--query", "fi", "--limit", "0"])
    assert result.exit_code == 0
    data = json.loads(result.output.strip())
    assert len(data) >= 1
    assert all("id" in row for row in data)


def test_seed_available_works_without_seed_service(monkeypatch, cli_uses_temp_db):
    """seed available should not require opening DB-backed SeedService."""
    import clible.commands.seed as seed_commands

    def fail_if_called():
        raise RuntimeError("SeedService should not be called for available.")

    monkeypatch.setattr(seed_commands, "_get_seed_service", fail_if_called)
    runner = CliRunner()
    result = runner.invoke(main, ["seed", "available", "--json", "--limit", "1"])
    assert result.exit_code == 0
    data = json.loads(result.output.strip())
    assert len(data) == 1


def test_seed_list_empty_shows_hint(cli_uses_temp_db):
    """seed list shows hint when no translations installed."""
    runner = CliRunner()
    result = runner.invoke(main, ["seed", "list"])
    assert result.exit_code == 0
    assert "No translations installed" in result.output or "install web" in result.output


def test_seed_list_json_empty_array(cli_uses_temp_db):
    """seed list --json prints [] when no translations installed."""
    runner = CliRunner()
    result = runner.invoke(main, ["seed", "list", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.output.strip()) == []


def test_seed_list_json_returns_installed_rows(cli_uses_temp_db):
    """seed list --json prints id/name/language/format for installed translations."""
    conn = get_connection()
    TranslationRepo(conn).create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["seed", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output.strip())
    assert len(data) == 1
    assert data[0] == {
        "id": "web",
        "name": "World English Bible",
        "language": "en",
        "format": "USFX",
    }


def test_verse_command_help():
    """verse command shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["verse", "--help"])
    assert result.exit_code == 0
    assert "REFERENCE" in result.output
    assert "translation" in result.output
