"""CLI integration tests for analytics commands."""

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
    """Use a temporary SQLite DB for CLI tests."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_path = f.name
    monkeypatch.setattr(config_module.config, "db_path", tmp_path)
    yield
    try:
        import os

        os.unlink(tmp_path)
    except OSError:
        pass


def test_analytics_compare_shows_side_by_side_diff_and_similarity(cli_uses_temp_db):
    """analytics compare renders table rows and similarity summary."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    verse_repo = VerseRepo(conn)

    translation_repo.create(
        {
            "id": "fin-1992",
            "name": "Finnish Bible 1992",
            "language": "fi",
            "format": "BEBLIA",
        }
    )
    translation_repo.create(
        {
            "id": "fin-1776",
            "name": "Finnish Bible 1776",
            "language": "fi",
            "format": "BEBLIA",
        }
    )

    verse_repo.save_verses(
        [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä niin on Jumala maailmaa rakastanut",
            },
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 17,
                "text": "Jumala ei lähettänyt Poikaansa tuomitsemaan maailmaa",
            },
        ],
        "fin-1992",
    )
    verse_repo.save_verses(
        [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä Jumala on rakastanut maailmaa niin paljon",
            },
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 17,
                "text": "Jumala ei lähettänyt Poikaansa tuomitsemaan maailmaa",
            },
        ],
        "fin-1776",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["analytics", "compare", "John 3:16-17"])

    assert result.exit_code == 0
    assert "Translation Comparison: John 3:16-17" in result.output
    assert "fin-1992" in result.output
    assert "fin17xx" in result.output
    assert "fin-1776" in result.output
    assert "Similarity Analysis" in result.output
    assert "Exact textual matches" in result.output
    assert "Average similarity" in result.output


def test_analytics_compare_fails_when_required_translations_missing(cli_uses_temp_db):
    """analytics compare exits with error if fin17xx alias cannot be resolved."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    translation_repo.create(
        {
            "id": "fin-1992",
            "name": "Finnish Bible 1992",
            "language": "fi",
            "format": "BEBLIA",
        }
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["analytics", "compare", "John 3:16"])

    assert result.exit_code != 0
    assert "Comparison failed." in result.output
    assert "Missing translation(s): fin17xx" in result.output


def test_analytics_compare_fails_when_same_translation_used_on_both_sides(cli_uses_temp_db):
    """analytics compare rejects identical left and right translation IDs."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    translation_repo.create(
        {
            "id": "fin-1992",
            "name": "Finnish Bible 1992",
            "language": "fi",
            "format": "BEBLIA",
        }
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["analytics", "compare", "John 3:16", "--left", "fin-1992", "--right", "fin-1992"],
    )

    assert result.exit_code != 0
    assert "Left and right translations are the same." in result.output


def test_analytics_compare_fails_when_reference_has_no_verses(cli_uses_temp_db):
    """analytics compare exits with error if selected translations have no matching verses."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    translation_repo.create(
        {
            "id": "fin-1992",
            "name": "Finnish Bible 1992",
            "language": "fi",
            "format": "BEBLIA",
        }
    )
    translation_repo.create(
        {
            "id": "fin-1776",
            "name": "Finnish Bible 1776",
            "language": "fi",
            "format": "BEBLIA",
        }
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["analytics", "compare", "John 3:16"])

    assert result.exit_code != 0
    assert "No verses found for this reference in the selected translations." in result.output


def test_analytics_reference_output_json_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics reference exports analysis as JSON."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    verse_repo = VerseRepo(conn)

    translation_repo.create(
        {
            "id": "fin-1992",
            "name": "Finnish Bible 1992",
            "language": "fi",
            "format": "BEBLIA",
        }
    )
    verse_repo.save_verses(
        [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä niin on Jumala maailmaa rakastanut",
            }
        ],
        "fin-1992",
    )
    conn.close()

    out_path = tmp_path / "analysis.json"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "reference",
            "John 3:16",
            "--translation",
            "fin-1992",
            "--output",
            str(out_path),
        ],
    )

    assert result.exit_code == 0
    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["type"] == "analysis"
    assert data["scope"] == "John 3:16"
    assert "token_count" in data
    assert "top_words" in data


def test_analytics_reference_output_csv_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics reference exports analysis as CSV."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    verse_repo = VerseRepo(conn)

    translation_repo.create(
        {
            "id": "fin-1992",
            "name": "Finnish Bible 1992",
            "language": "fi",
            "format": "BEBLIA",
        }
    )
    verse_repo.save_verses(
        [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä niin on Jumala maailmaa rakastanut",
            }
        ],
        "fin-1992",
    )
    conn.close()

    out_path = tmp_path / "analysis.csv"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "reference",
            "John 3:16",
            "--translation",
            "fin-1992",
            "--output",
            str(out_path),
        ],
    )

    assert result.exit_code == 0
    assert out_path.exists()

    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("section,metric,rank,token,count")
    assert "metrics,token_count" in content


def test_analytics_reference_output_md_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics reference exports analysis as Markdown."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    verse_repo = VerseRepo(conn)

    translation_repo.create(
        {
            "id": "fin-1992",
            "name": "Finnish Bible 1992",
            "language": "fi",
            "format": "BEBLIA",
        }
    )
    verse_repo.save_verses(
        [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä niin on Jumala maailmaa rakastanut",
            }
        ],
        "fin-1992",
    )
    conn.close()

    out_path = tmp_path / "analysis.md"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "reference",
            "John 3:16",
            "--translation",
            "fin-1992",
            "--output",
            str(out_path),
        ],
    )

    assert result.exit_code == 0
    assert out_path.exists()

    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("# Text Analysis: John 3:16")
    assert "## Metrics" in content


def test_analytics_reference_output_html_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics reference exports analysis as HTML."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    verse_repo = VerseRepo(conn)

    translation_repo.create(
        {
            "id": "fin-1992",
            "name": "Finnish Bible 1992",
            "language": "fi",
            "format": "BEBLIA",
        }
    )
    verse_repo.save_verses(
        [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä niin on Jumala maailmaa rakastanut",
            }
        ],
        "fin-1992",
    )
    conn.close()

    out_path = tmp_path / "analysis.html"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "reference",
            "John 3:16",
            "--translation",
            "fin-1992",
            "--output",
            str(out_path),
        ],
    )

    assert result.exit_code == 0
    assert out_path.exists()

    content = out_path.read_text(encoding="utf-8")
    assert "<table" in content.lower()
    assert "Text Analysis" in content


def test_analytics_reference_output_rejects_unsupported_extension(cli_uses_temp_db, tmp_path: Path):
    """analytics reference fails with unsupported output extension and does not create a file."""
    out_path = tmp_path / "analysis.txt"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "reference",
            "John 3:16",
            "--translation",
            "fin-1992",
            "--output",
            str(out_path),
        ],
    )

    assert result.exit_code != 0
    assert not out_path.exists()


def test_analytics_compare_output_json_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics compare exports comparison as JSON."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    verse_repo = VerseRepo(conn)

    translation_repo.create(
        {
            "id": "fin-1992",
            "name": "Finnish Bible 1992",
            "language": "fi",
            "format": "BEBLIA",
        }
    )
    translation_repo.create(
        {
            "id": "fin-1776",
            "name": "Finnish Bible 1776",
            "language": "fi",
            "format": "BEBLIA",
        }
    )

    verse_repo.save_verses(
        [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä niin on Jumala maailmaa rakastanut",
            }
        ],
        "fin-1992",
    )
    verse_repo.save_verses(
        [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä Jumala on rakastanut maailmaa niin paljon",
            }
        ],
        "fin-1776",
    )
    conn.close()

    out_path = tmp_path / "compare.json"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "compare",
            "John 3:16",
            "--left",
            "fin-1992",
            "--right",
            "fin-1776",
            "--output",
            str(out_path),
        ],
    )

    assert result.exit_code == 0
    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["type"] == "compare"
    assert data["reference"] == "John 3:16"
    assert len(data["aligned_verses"]) == 1


def test_analytics_compare_output_html_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics compare exports comparison as HTML."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)
    verse_repo = VerseRepo(conn)

    translation_repo.create(
        {
            "id": "fin-1992",
            "name": "Finnish Bible 1992",
            "language": "fi",
            "format": "BEBLIA",
        }
    )
    translation_repo.create(
        {
            "id": "fin-1776",
            "name": "Finnish Bible 1776",
            "language": "fi",
            "format": "BEBLIA",
        }
    )

    verse_repo.save_verses(
        [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä niin on Jumala maailmaa rakastanut",
            }
        ],
        "fin-1992",
    )
    verse_repo.save_verses(
        [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä Jumala on rakastanut maailmaa niin paljon",
            }
        ],
        "fin-1776",
    )
    conn.close()

    out_path = tmp_path / "compare.html"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "compare",
            "John 3:16",
            "--left",
            "fin-1992",
            "--right",
            "fin-1776",
            "--output",
            str(out_path),
        ],
    )

    assert result.exit_code == 0
    assert out_path.exists()

    content = out_path.read_text(encoding="utf-8").lower()
    assert "<table" in content
    assert "aligned verses" in content
