"""CLI integration tests for verse command."""

import tempfile

import pytest
from click.testing import CliRunner

from clible import config as config_module
from clible.cli import main
from clible.db.connection import get_connection
from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo


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


def test_verse_range_not_found_without_data(cli_uses_temp_db):
    """verse with range exits with error when no verses are installed."""
    runner = CliRunner()
    result = runner.invoke(main, ["verse", "John 3:1-6"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


def test_verse_range_displays_multiple_verses(cli_uses_temp_db):
    """verse with range (e.g. John 3:1-6) displays all verses in order."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    verse_repo = VerseRepo(conn)
    translation_repo.create(
        {
            "id": "kjv",
            "name": "King James Version",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [
            {"book_id": "JHN", "chapter": 3, "verse": 1, "text": "V1"},
            {"book_id": "JHN", "chapter": 3, "verse": 2, "text": "V2"},
            {"book_id": "JHN", "chapter": 3, "verse": 3, "text": "V3"},
            {"book_id": "JHN", "chapter": 3, "verse": 4, "text": "V4"},
            {"book_id": "JHN", "chapter": 3, "verse": 5, "text": "V5"},
            {"book_id": "JHN", "chapter": 3, "verse": 6, "text": "V6"},
        ],
        "kjv",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["verse", "John 3:1-6", "-t", "kjv"])
    assert result.exit_code == 0
    assert "V1" in result.output
    assert "V2" in result.output
    assert "V6" in result.output
    assert result.output.count("JHN 3:") >= 6
