"""CLI integration tests for verse command."""

import json
import tempfile
from pathlib import Path

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


def test_verse_chapter_displays_verses(cli_uses_temp_db):
    """verse with chapter reference shows all verses in chapter (under page size)."""
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
            {"book_id": "JHN", "chapter": 3, "verse": 1, "text": "C1"},
            {"book_id": "JHN", "chapter": 3, "verse": 2, "text": "C2"},
        ],
        "kjv",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["verse", "John 3", "-t", "kjv", "--page-size", "0"])
    assert result.exit_code == 0
    assert "C1" in result.output
    assert "C2" in result.output
    assert "JHN 3:1" in result.output


def test_verse_chapter_second_page(cli_uses_temp_db):
    """verse paginates chapter output when --page-size is smaller than chapter."""
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
    rows = [
        {"book_id": "JHN", "chapter": 3, "verse": n, "text": f"V{n}"} for n in range(1, 6)
    ]
    verse_repo.save_verses(rows, "kjv")
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["verse", "John 3", "-t", "kjv", "--page-size", "2", "--page", "2"],
    )
    assert result.exit_code == 0
    assert "V3" in result.output
    assert "V4" in result.output
    assert "V1" not in result.output
    assert "page 2 of 3" in result.output


def test_verse_export_chapter_includes_all_verses(cli_uses_temp_db, tmp_path: Path):
    """verse --export on a chapter writes every verse, not one page only."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    verse_repo = VerseRepo(conn)
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [
            {"book_id": "JHN", "chapter": 3, "verse": 1, "text": "A"},
            {"book_id": "JHN", "chapter": 3, "verse": 2, "text": "B"},
            {"book_id": "JHN", "chapter": 3, "verse": 3, "text": "C"},
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "verse",
            "John 3",
            "-t",
            "web",
            "--page-size",
            "1",
            "--export",
            f"PATH={tmp_path},FILENAME=ch3,FORMAT=json",
        ],
    )
    assert result.exit_code == 0
    data = json.loads((tmp_path / "ch3.json").read_text(encoding="utf-8"))
    assert len(data["verses"]) == 3


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


def test_verse_export_json_with_unified_flag(cli_uses_temp_db, tmp_path: Path):
    """verse --export creates JSON file with verses."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    verse_repo = VerseRepo(conn)
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [
            {"book_id": "JHN", "chapter": 3, "verse": 16, "text": "For God so loved the world"},
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "verse",
            "John 3:16",
            "-t",
            "web",
            "--export",
            f"PATH={tmp_path},FILENAME=verse_john,FORMAT=json",
        ],
    )

    assert result.exit_code == 0
    out_path = tmp_path / "verse_john.json"
    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["type"] == "verse_lookup"
    assert len(data["verses"]) == 1
    assert data["verses"][0]["text"] == "For God so loved the world"


def test_verse_export_md_uses_default_when_format_omitted(cli_uses_temp_db, tmp_path: Path):
    """verse --export without FORMAT defaults to md."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    verse_repo = VerseRepo(conn)
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    verse_repo.save_verses(
        [
            {"book_id": "JHN", "chapter": 3, "verse": 16, "text": "For God so loved the world"},
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "verse",
            "John 3:16",
            "-t",
            "web",
            "--export",
            f"PATH={tmp_path},FILENAME=verse_default",
        ],
    )

    assert result.exit_code == 0
    out_path = tmp_path / "verse_default.md"
    assert out_path.exists()

    content = out_path.read_text(encoding="utf-8")
    assert "# Verses: John 3:16" in content
    assert "## Verses" in content
