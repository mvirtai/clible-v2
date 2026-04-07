"""CLI integration tests for search command."""

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


def test_search_no_results_without_data(cli_uses_temp_db):
    """search prints no-results message when no verses are installed."""
    runner = CliRunner()
    result = runner.invoke(main, ["search", "grace"])
    assert result.exit_code == 0
    assert "No verses found" in result.output
    assert "grace" in result.output


def test_search_json_no_matches_emits_valid_json(cli_uses_temp_db):
    """search --json with no matches prints a single JSON object (web bridge)."""
    runner = CliRunner()
    result = runner.invoke(main, ["search", "nomatchxyz", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output.strip())
    assert data["type"] == "search"
    assert data["query"] == "nomatchxyz"
    assert data["verses"] == []
    assert data["statistics"]["unique_verses"] == 0


def test_search_json_limit_slices_verses_statistics_from_full_match_set(cli_uses_temp_db):
    """search --json --limit caps verses; statistics still describe the full match set."""
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
            {
                "book_id": "JHN",
                "chapter": 1,
                "verse": 14,
                "text": "Full of grace and truth",
            },
            {
                "book_id": "JHN",
                "chapter": 1,
                "verse": 17,
                "text": "Grace and truth came through Jesus",
            },
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["search", "grace", "-t", "web", "--json", "--limit", "1"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output.strip())
    assert len(data["verses"]) == 1
    assert data["statistics"]["unique_verses"] == 2
    assert data["statistics"]["total_occurrences"] == 2


def test_search_displays_matching_verses_with_highlight(cli_uses_temp_db):
    """search finds verses containing the word and displays them."""
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
            {
                "book_id": "JHN",
                "chapter": 1,
                "verse": 14,
                "text": "Full of grace and truth",
            },
            {
                "book_id": "JHN",
                "chapter": 1,
                "verse": 17,
                "text": "Grace and truth came through Jesus",
            },
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["search", "grace", "-t", "web"])
    assert result.exit_code == 0
    assert "grace" in result.output.lower()
    assert "JHN 1:14" in result.output
    assert "JHN 1:17" in result.output
    assert "Full of grace" in result.output or "grace" in result.output


def test_search_empty_word_exits_with_error(cli_uses_temp_db):
    """search with empty word prints error and exits non-zero."""
    runner = CliRunner()
    result = runner.invoke(main, ["search", ""])
    assert result.exit_code != 0
    assert "empty" in result.output.lower()


def test_search_scope_book_filters_to_single_book(cli_uses_temp_db):
    """search --scope book filters results to specified book only."""
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
            {
                "book_id": "GEN",
                "chapter": 1,
                "verse": 1,
                "text": "God created the heavens",
            },
            {
                "book_id": "JHN",
                "chapter": 1,
                "verse": 1,
                "text": "In the beginning was God",
            },
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["search", "God", "--scope", "book", "-r", "John", "-t", "web"])
    assert result.exit_code == 0
    assert "JHN 1:1" in result.output
    assert "GEN 1:1" not in result.output


def test_search_scope_testament_filters_to_ot_or_nt(cli_uses_temp_db):
    """search --scope testament filters to OT or NT books."""
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
            {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "God created"},
            {"book_id": "JHN", "chapter": 1, "verse": 1, "text": "God was the Word"},
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["search", "God", "--scope", "testament", "-r", "NT", "-t", "web"])
    assert result.exit_code == 0
    assert "JHN 1:1" in result.output
    assert "GEN 1:1" not in result.output
    assert "in NT" in result.output


def test_search_scope_testament_displays_ot_uppercase(cli_uses_temp_db):
    """search --scope testament -r ot shows 'OT' in header, not 'ot'."""
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
        [{"book_id": "GEN", "chapter": 1, "verse": 1, "text": "wrath of God"}],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["search", "wrath", "-s", "testament", "-r", "ot", "-t", "web"])
    assert result.exit_code == 0
    assert "in OT" in result.output
    assert "Search Results: 'wrath' in OT" in result.output


def test_search_scope_chapter_filters_to_single_chapter(cli_uses_temp_db):
    """search --scope chapter filters to specified chapter only."""
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
            {"book_id": "JHN", "chapter": 1, "verse": 1, "text": "Word was with God"},
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "God so loved the world",
            },
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main, ["search", "God", "--scope", "chapter", "-r", "John 3", "-t", "web"]
    )
    assert result.exit_code == 0
    assert "JHN 3:16" in result.output
    assert "JHN 1:1" not in result.output


def test_search_scope_verse_filters_to_single_verse(cli_uses_temp_db):
    """search --scope verse filters to specified verse only."""
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
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "God so loved the world",
            },
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 17,
                "text": "God sent not his Son",
            },
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main, ["search", "God", "--scope", "verse", "-r", "John 3:16", "-t", "web"]
    )
    assert result.exit_code == 0
    assert "JHN 3:16" in result.output
    assert "JHN 3:17" not in result.output


def test_search_shows_statistics_table(cli_uses_temp_db):
    """search displays statistics table with occurrences and top books."""
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
            {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "God created God"},
            {"book_id": "JHN", "chapter": 1, "verse": 1, "text": "God was the Word"},
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["search", "God", "-t", "web"])
    assert result.exit_code == 0
    assert "Statistics" in result.output
    assert "Total occurrences" in result.output
    assert "Unique verses" in result.output
    assert "Top Books" in result.output


def test_search_with_limit_shows_only_n_verses(cli_uses_temp_db):
    """search --limit N displays only first N verses."""
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
            {"book_id": "JHN", "chapter": 1, "verse": i, "text": f"Verse {i} with word"}
            for i in range(1, 26)
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["search", "word", "--limit", "5", "-t", "web"])
    assert result.exit_code == 0
    assert "JHN 1:1" in result.output
    assert "JHN 1:5" in result.output
    assert "and 20 more verses" in result.output


def test_search_scope_without_reference_exits_with_error(cli_uses_temp_db):
    """search --scope book without --reference exits with error."""
    runner = CliRunner()
    result = runner.invoke(main, ["search", "grace", "--scope", "book"])
    assert result.exit_code != 0
    assert "requires --reference" in result.output


def test_search_interactive_confirmation_no_skips_display(cli_uses_temp_db):
    """search with >20 results asks confirmation; 'no' skips display."""
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
            {"book_id": "JHN", "chapter": 1, "verse": i, "text": f"Verse {i} with word"}
            for i in range(1, 30)
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["search", "word", "-t", "web"], input="no\n")
    assert result.exit_code == 0
    assert "Found 29 verses" in result.output
    assert "How many verses to display?" in result.output
    assert "Statistics only" in result.output


def test_search_interactive_confirmation_accepts_number(cli_uses_temp_db):
    """search with >20 results accepts numeric input to limit display."""
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
            {"book_id": "JHN", "chapter": 1, "verse": i, "text": f"Verse {i} with word"}
            for i in range(1, 30)
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["search", "word", "-t", "web"], input="5\n")
    assert result.exit_code == 0
    assert "JHN 1:1" in result.output
    assert "JHN 1:5" in result.output
    assert "and 24 more verses" in result.output
    assert "JHN 1:10" not in result.output


def test_search_interactive_confirmation_all_shows_everything(cli_uses_temp_db):
    """search with >20 results accepts 'all' to display everything."""
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
            {"book_id": "JHN", "chapter": 1, "verse": i, "text": f"Verse {i} with word"}
            for i in range(1, 25)
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(main, ["search", "word", "-t", "web"], input="all\n")
    assert result.exit_code == 0
    assert "JHN 1:1" in result.output
    assert "JHN 1:24" in result.output
    assert "more verses" not in result.output


def test_search_export_json_includes_statistics(cli_uses_temp_db, tmp_path: Path):
    """search --export creates JSON with verses and statistics."""
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
            {"book_id": "JHN", "chapter": 1, "verse": 14, "text": "Full of grace and truth"},
            {"book_id": "JHN", "chapter": 1, "verse": 17, "text": "Grace and truth came"},
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "search",
            "grace",
            "-t",
            "web",
            "--export",
            f"PATH={tmp_path},FILENAME=search_grace,FORMAT=json",
        ],
    )

    assert result.exit_code == 0
    out_path = tmp_path / "search_grace.json"
    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["type"] == "search"
    assert data["query"] == "grace"
    assert data["scope"] == "bible"
    assert len(data["verses"]) == 2
    assert "statistics" in data
    assert data["statistics"]["total_occurrences"] == 2


def test_search_export_md_all_keys_explicit(cli_uses_temp_db, tmp_path: Path):
    """search --export with all keys explicit creates markdown."""
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
            {"book_id": "JHN", "chapter": 3, "verse": 16, "text": "For God so loved"},
        ],
        "web",
    )
    conn.close()

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "search",
            "loved",
            "-t",
            "web",
            "--export",
            f"PATH={tmp_path},FILENAME=search_loved,FORMAT=md",
        ],
    )

    assert result.exit_code == 0
    out_path = tmp_path / "search_loved.md"
    assert out_path.exists()

    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("# Search:")
    assert "loved" in content
    assert "## Statistics" in content
    assert "## Verses" in content
