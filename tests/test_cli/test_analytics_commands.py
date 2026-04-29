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


def test_analytics_reference_export_json_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics reference exports analysis as JSON using unified --export."""
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

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "reference",
            "John 3:16",
            "--translation",
            "fin-1992",
            "--export",
            f"PATH={tmp_path},FILENAME=analysis,FORMAT=json",
        ],
    )

    assert result.exit_code == 0
    out_path = tmp_path / "analysis.json"
    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["type"] == "analysis"
    assert data["scope"] == "John 3:16"
    assert "token_count" in data
    assert "top_words" in data


def test_analytics_reference_export_txt_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics reference exports analysis as TXT using unified --export."""
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

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "reference",
            "John 3:16",
            "--translation",
            "fin-1992",
            "--export",
            f"PATH={tmp_path},FILENAME=analysis_text,FORMAT=txt",
        ],
    )

    assert result.exit_code == 0
    out_path = tmp_path / "analysis_text.txt"
    assert out_path.exists()

    content = out_path.read_text(encoding="utf-8")
    assert "Text analysis: John 3:16" in content
    assert "Metrics" in content


def test_analytics_reference_export_defaults_to_md_in_current_dir(cli_uses_temp_db, tmp_path: Path):
    """analytics reference exports with minimal --export uses defaults (format=md)."""
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

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "reference",
            "John 3:16",
            "--translation",
            "fin-1992",
            "--export",
            f"PATH={tmp_path},FILENAME=test_analysis",
        ],
    )

    assert result.exit_code == 0
    out_path = tmp_path / "test_analysis.md"
    assert out_path.exists()

    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("# Text Analysis: John 3:16")
    assert "## Metrics" in content


def test_analytics_reference_export_xml_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics reference exports analysis as XML using unified --export."""
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

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "reference",
            "John 3:16",
            "--translation",
            "fin-1992",
            "--export",
            f"PATH={tmp_path},FILENAME=analysis_xml,FORMAT=xml",
        ],
    )

    assert result.exit_code == 0
    out_path = tmp_path / "analysis_xml.xml"
    assert out_path.exists()

    content = out_path.read_text(encoding="utf-8")
    assert '<?xml version="1.0"' in content
    assert "<analysis" in content
    assert "<scope>John 3:16</scope>" in content


def test_analytics_reference_export_rejects_unsupported_format(cli_uses_temp_db, tmp_path: Path):
    """analytics reference fails with unsupported FORMAT in --export."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "reference",
            "John 3:16",
            "--translation",
            "fin-1992",
            "--export",
            "PATH=" + str(tmp_path) + ",FORMAT=pdf",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported FORMAT" in result.output or "unsupported" in result.output.lower()


def test_analytics_compare_export_json_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics compare exports comparison as JSON using unified --export."""
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
            "--export",
            f"PATH={tmp_path},FILENAME=compare,FORMAT=json",
        ],
    )

    assert result.exit_code == 0
    out_path = tmp_path / "compare.json"
    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["type"] == "compare"
    assert data["reference"] == "John 3:16"
    assert len(data["aligned_verses"]) == 1


def test_analytics_compare_export_with_only_format_uses_defaults(cli_uses_temp_db, tmp_path: Path):
    """analytics compare with only FORMAT in --export uses PATH and FILENAME defaults."""
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
            "--export",
            f"PATH={tmp_path},FORMAT=html",
        ],
    )

    assert result.exit_code == 0
    html_files = list(tmp_path.glob("*.html"))
    assert len(html_files) == 1

    content = html_files[0].read_text(encoding="utf-8").lower()
    assert "<!doctype html>" in content
    assert "aligned verses" in content
    assert "summary statistics" in content
    assert "<h3>left</h3>" not in content
    assert "<h3>right</h3>" not in content
    assert "left:" not in content
    assert "right:" not in content
    assert "john 3:16" in content


def test_analytics_reference_output_json_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics reference exports analysis as JSON using --output."""
    conn = get_connection()
    TranslationRepo(conn).create({"id": "web", "name": "WEB", "language": "en", "format": "BEBLIA"})
    VerseRepo(conn).save_verses(
        [{"book_id": "GEN", "chapter": 1, "verse": 1, "text": "In the beginning..."}], "web"
    )
    conn.close()

    out_file = tmp_path / "result.json"
    runner = CliRunner()
    result = runner.invoke(main, ["analytics", "reference", "Gen 1:1", "--output", str(out_file)])

    assert result.exit_code == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["type"] == "analysis"
    assert data["scope"] == "Gen 1:1"


def test_analytics_reference_output_md_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics reference exports analysis as Markdown using --output."""
    conn = get_connection()
    TranslationRepo(conn).create({"id": "web", "name": "WEB", "language": "en", "format": "BEBLIA"})
    VerseRepo(conn).save_verses(
        [{"book_id": "GEN", "chapter": 1, "verse": 1, "text": "In the beginning..."}], "web"
    )
    conn.close()

    out_file = tmp_path / "result.md"
    runner = CliRunner()
    result = runner.invoke(main, ["analytics", "reference", "Gen 1:1", "-o", str(out_file)])

    assert result.exit_code == 0
    assert out_file.exists()
    assert "# Text Analysis: Gen 1:1" in out_file.read_text(encoding="utf-8")


def test_analytics_compare_output_html_creates_file(cli_uses_temp_db, tmp_path: Path):
    """analytics compare exports comparison as HTML using --output."""
    conn = get_connection()
    repo = TranslationRepo(conn)
    repo.create({"id": "web", "name": "WEB", "language": "en", "format": "BEBLIA"})
    repo.create({"id": "kjv", "name": "KJV", "language": "en", "format": "BEBLIA"})
    VerseRepo(conn).save_verses(
        [{"book_id": "GEN", "chapter": 1, "verse": 1, "text": "In the beginning..."}], "web"
    )
    VerseRepo(conn).save_verses(
        [{"book_id": "GEN", "chapter": 1, "verse": 1, "text": "In start..."}], "kjv"
    )
    conn.close()

    out_file = tmp_path / "diff.html"
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["analytics", "compare", "Gen 1:1", "--left", "web", "--right", "kjv", "-o", str(out_file)],
    )

    assert result.exit_code == 0
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8").lower()
    assert "<!doctype html>" in content
    assert "gen 1:1" in content


def test_analytics_output_fails_on_unsupported_extension(cli_uses_temp_db, tmp_path: Path):
    """analytics reference fails gracefully when extension is not supported."""
    conn = get_connection()
    TranslationRepo(conn).create({"id": "web", "name": "WEB", "language": "en", "format": "BEBLIA"})
    conn.close()

    out_file = tmp_path / "result.pdf"
    runner = CliRunner()
    result = runner.invoke(main, ["analytics", "reference", "Gen 1:1", "--output", str(out_file)])

    assert result.exit_code != 0
    assert "Unsupported --output format '.pdf'" in result.output


def test_analytics_output_fails_on_missing_extension(cli_uses_temp_db, tmp_path: Path):
    """analytics reference fails gracefully when extension is missing."""
    conn = get_connection()
    TranslationRepo(conn).create({"id": "web", "name": "WEB", "language": "en", "format": "BEBLIA"})
    conn.close()

    out_file = tmp_path / "result_no_ext"
    runner = CliRunner()
    result = runner.invoke(main, ["analytics", "reference", "Gen 1:1", "--output", str(out_file)])

    assert result.exit_code != 0
    assert "Missing file extension for --output" in result.output


def test_analytics_chapter_json_works_for_web_bridge(cli_uses_temp_db):
    """analytics chapter --json should work (web bridge compatibility regression test)."""
    conn = get_connection()
    TranslationRepo(conn).create(
        {"id": "fin-1992", "name": "FIN1992", "language": "fi", "format": "BEBLIA"}
    )
    VerseRepo(conn).save_verses(
        [{"book_id": "PSA", "chapter": 1, "verse": 1, "text": "Autuas se mies"}],
        "fin-1992",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "chapter",
            "PSA",
            "1",
            "--translation",
            "fin-1992",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["type"] == "analysis"
    assert payload["scope"] == "PSA 1"


def test_analytics_book_json_works_for_web_bridge(cli_uses_temp_db):
    """analytics book --json should work (web bridge compatibility regression test)."""
    conn = get_connection()
    TranslationRepo(conn).create(
        {"id": "fin-1992", "name": "FIN1992", "language": "fi", "format": "BEBLIA"}
    )
    VerseRepo(conn).save_verses(
        [{"book_id": "PSA", "chapter": 1, "verse": 1, "text": "Autuas se mies"}],
        "fin-1992",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analytics",
            "book",
            "PSA",
            "--translation",
            "fin-1992",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["type"] == "analysis"
    assert payload["scope"] == "PSA"
