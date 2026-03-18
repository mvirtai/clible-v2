"""Analytics commands: text analysis for verses, chapters, books, and comparison."""

import difflib
import json
from pathlib import Path

import click
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from clible.db.connection import get_connection
from clible.db.repositories.book_repo import BookRepo
from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo
from clible.services.analytic_service import AnalyticService
from clible.services.verse_service import VerseService
from clible.ui.analytics_export import (
    detect_format,
    export_analysis,
    export_compare,
    write_text,
)
from clible.ui.console import console
from clible.ui.help_texts import (
    ANALYTICS_BOOK_HELP,
    ANALYTICS_CHAPTER_HELP,
    ANALYTICS_COMPARE_HELP,
    ANALYTICS_REFERENCE_HELP,
)

_TRANSLATIONS_FILE = Path(__file__).parent.parent / "data" / "translations.json"


def _language_for_translation(translation_id: str) -> str:
    """Look up the language code for a given translation ID."""
    if not _TRANSLATIONS_FILE.exists():
        return "en"
    with open(_TRANSLATIONS_FILE, encoding="utf-8") as f:
        catalog = json.load(f)
    return catalog.get(translation_id, {}).get("language", "en")


def _get_analytic_service(translation_id: str | None) -> AnalyticService:
    """Build AnalyticService with real dependencies."""
    conn = get_connection()
    translation_repo = TranslationRepo(conn)

    resolved_id = translation_id
    if resolved_id is None:
        default = translation_repo.get_default()
        resolved_id = default["id"] if default else None

    language = _language_for_translation(resolved_id) if resolved_id else "en"

    verse_service = VerseService(
        verse_repo=VerseRepo(conn),
        book_repo=BookRepo(conn),
        translation_repo=translation_repo,
    )
    return AnalyticService(verse_service=verse_service, language=language)


def _resolve_compare_translation_id(
    translation_repo: TranslationRepo,
    requested_translation_id: str,
) -> str | None:
    """Resolve compare translation IDs, including fin17xx alias support."""
    if translation_repo.exists(requested_translation_id):
        return requested_translation_id

    alias = requested_translation_id.strip().lower()
    if alias in {"fin17xx", "fin-17xx"}:
        if translation_repo.exists("fin-1776"):
            return "fin-1776"

        for item in translation_repo.get_all():
            if item["id"].startswith("fin-17"):
                return item["id"]

    return None


def _display_translation_label(requested_id: str, resolved_id: str) -> str:
    """Build a readable translation label for table headers."""
    if requested_id == resolved_id:
        return resolved_id
    return f"{requested_id} ({resolved_id})"


def _word_level_diff_markup(text_a: str, text_b: str) -> str:
    """Render word-level diff with Rich color markup."""
    tokens_a = text_a.split()
    tokens_b = text_b.split()
    diff_tokens: list[str] = []

    for token in difflib.ndiff(tokens_a, tokens_b):
        marker = token[:2]
        word = escape(token[2:])
        if marker == "- ":
            diff_tokens.append(f"[red]-{word}[/red]")
        elif marker == "+ ":
            diff_tokens.append(f"[green]+{word}[/green]")
        elif marker == "  ":
            diff_tokens.append(word)

    if not diff_tokens:
        return "[dim]No textual difference.[/dim]"
    return " ".join(diff_tokens)


def _render_analysis(console: Console, analysis: dict, scope_label: str) -> None:
    """Render analysis results as Rich tables."""
    console.print(f"\n[bold cyan]Text Analysis: {scope_label}[/bold cyan]\n")

    metrics_table = Table(title="Metrics", show_header=True)
    metrics_table.add_column("Metric", style="dim")
    metrics_table.add_column("Value", justify="right")

    metrics_table.add_row("Total tokens", str(analysis["token_count"]))
    metrics_table.add_row("Unique tokens", str(analysis["unique_token_count"]))
    metrics_table.add_row("Type-token ratio", f"{analysis['type_token_ratio']:.3f}")

    console.print(metrics_table)

    if analysis["top_words"]:
        words_table = Table(title="Top Words", show_header=True)
        words_table.add_column("Rank", justify="right", style="dim")
        words_table.add_column("Word")
        words_table.add_column("Count", justify="right")

        for i, (word, count) in enumerate(analysis["top_words"], 1):
            words_table.add_row(str(i), word, str(count))

        console.print(words_table)

    if analysis["top_bigrams"]:
        bigrams_table = Table(title="Top Bigrams", show_header=True)
        bigrams_table.add_column("Rank", justify="right", style="dim")
        bigrams_table.add_column("Bigram")
        bigrams_table.add_column("Count", justify="right")

        for i, (bigram, count) in enumerate(analysis["top_bigrams"], 1):
            bigrams_table.add_row(str(i), bigram, str(count))

        console.print(bigrams_table)

    if analysis["top_trigrams"]:
        trigrams_table = Table(title="Top Trigrams", show_header=True)
        trigrams_table.add_column("Rank", justify="right", style="dim")
        trigrams_table.add_column("Trigram")
        trigrams_table.add_column("Count", justify="right")

        for i, (trigram, count) in enumerate(analysis["top_trigrams"], 1):
            trigrams_table.add_row(str(i), trigram, str(count))

        console.print(trigrams_table)


def _render_comparison(
    console: Console,
    comparison: dict,
    left_label: str,
    right_label: str,
) -> None:
    """Render side-by-side diff table and similarity summary."""
    console.print(f"\n[bold cyan]Translation Comparison: {comparison['reference']}[/bold cyan]\n")

    table = Table(show_header=True, show_lines=True)
    table.add_column("Verse", style="dim", no_wrap=True)
    table.add_column(left_label, overflow="fold")
    table.add_column(right_label, overflow="fold")
    table.add_column("Diff", overflow="fold")
    table.add_column("Similarity", justify="right", no_wrap=True)

    for row in comparison["aligned_verses"]:
        ref = f"{row['book_id']} {row['chapter']}:{row['verse']}"
        text_a = row["text_a"] or "[dim]— missing —[/dim]"
        text_b = row["text_b"] or "[dim]— missing —[/dim]"

        if row["text_a"] and row["text_b"]:
            diff = _word_level_diff_markup(row["text_a"], row["text_b"])
        elif row["text_a"]:
            diff = "[red]Only left translation has this verse.[/red]"
        else:
            diff = "[green]Only right translation has this verse.[/green]"

        table.add_row(
            ref,
            text_a,
            text_b,
            diff,
            f"{row['similarity'] * 100:.1f}%",
        )

    console.print(table)

    summary = comparison["summary"]
    summary_lines = [
        f"Compared verses: {summary['total_verses']}",
        f"Aligned on both sides: {summary['fully_aligned_verses']}",
        (
            "Exact textual matches: "
            f"{summary['exact_matches']} ({summary['exact_match_ratio'] * 100:.1f}%)"
        ),
        f"Average similarity: {summary['average_similarity'] * 100:.1f}%",
    ]

    most_similar = summary["most_similar_verse"]
    if most_similar is not None:
        summary_lines.append(
            "Most similar verse: "
            f"{most_similar['reference']} ({most_similar['similarity'] * 100:.1f}%)"
        )

    top_shared_words = summary["top_shared_words"]
    if top_shared_words:
        top_words_text = ", ".join(f"{word} ({count})" for word, count in top_shared_words[:5])
        summary_lines.append(f"Top shared vocabulary: {top_words_text}")

    console.print(
        Panel(
            "\n".join(summary_lines),
            title="Similarity Analysis",
            border_style="cyan",
        )
    )


def _export_analysis_if_requested(
    *,
    analysis: dict,
    scope_label: str,
    output_path: str | None,
) -> None:
    """Write analysis output to a file when --output is provided."""
    if output_path is None:
        return

    out_path = Path(output_path)
    try:
        fmt = detect_format(out_path)
        content = export_analysis(analysis, scope_label=scope_label, format=fmt)
        write_text(out_path, content)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)
    except OSError as e:
        console.print(f"[red]Failed to write output file: {e}[/red]")
        raise SystemExit(1)


def _export_compare_if_requested(
    *,
    comparison: dict,
    output_path: str | None,
) -> None:
    """Write comparison output to a file when --output is provided."""
    if output_path is None:
        return

    out_path = Path(output_path)
    try:
        fmt = detect_format(out_path)
        content = export_compare(comparison, format=fmt)
        write_text(out_path, content)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)
    except OSError as e:
        console.print(f"[red]Failed to write output file: {e}[/red]")
        raise SystemExit(1)


@click.command(
    "reference",
    add_help_option=False,
    context_settings={"help_option_names": []},
)
@click.argument("ref", required=False)
@click.option(
    "-t",
    "--translation",
    "translation_id",
    default=None,
    help="Translation ID (e.g. web). Defaults to installed default.",
)
@click.option(
    "-n",
    "--top",
    "top_n",
    default=10,
    type=int,
    help="Number of top items to show (default 10).",
)
@click.option(
    "--output",
    "output_path",
    default=None,
    help="Write results to a file. Format is inferred from extension: .json/.csv/.html/.md",
)
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def reference(
    ref: str | None,
    translation_id: str | None,
    top_n: int,
    output_path: str | None,
    show_help: bool,
) -> None:
    """Analyze verses in a reference (e.g. 'John 3:16' or 'John 3:16-18')."""
    if show_help:
        console.print(ANALYTICS_REFERENCE_HELP)
        return

    if ref is None:
        console.print("[red]Reference is required.[/red]")
        raise SystemExit(1)

    service = _get_analytic_service(translation_id)
    analysis = service.analyze_reference(ref, translation_id, top_n)

    if output_path is not None:
        _export_analysis_if_requested(
            analysis=analysis, scope_label=ref, output_path=output_path
        )
        return
    _render_analysis(console, analysis, ref)


@click.command("chapter", add_help_option=False, context_settings={"help_option_names": []})
@click.argument("book_name", required=False)
@click.argument("chapter_num", type=int, required=False)
@click.option(
    "-t",
    "--translation",
    "translation_id",
    default=None,
    help="Translation ID (e.g. web). Defaults to installed default.",
)
@click.option(
    "-n",
    "--top",
    "top_n",
    default=10,
    type=int,
    help="Number of top items to show (default 10).",
)
@click.option(
    "--output",
    "output_path",
    default=None,
    help="Write results to a file. Format is inferred from extension: .json/.csv/.html/.md",
)
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def chapter(
    book_name: str | None,
    chapter_num: int | None,
    translation_id: str | None,
    top_n: int,
    output_path: str | None,
    show_help: bool,
) -> None:
    """Analyze all verses in a chapter."""
    if show_help:
        console.print(ANALYTICS_CHAPTER_HELP)
        return

    if book_name is None or chapter_num is None:
        console.print("[red]Book and chapter are required.[/red]")
        raise SystemExit(1)

    service = _get_analytic_service(translation_id)
    analysis = service.analyze_chapter(book_name, chapter_num, translation_id, top_n)
    scope_label = f"{book_name} {chapter_num}"

    if output_path is not None:
        _export_analysis_if_requested(
            analysis=analysis, scope_label=scope_label, output_path=output_path
        )
        return
    _render_analysis(console, analysis, scope_label)


@click.command("book", add_help_option=False, context_settings={"help_option_names": []})
@click.argument("book_name", required=False)
@click.option(
    "-t",
    "--translation",
    "translation_id",
    default=None,
    help="Translation ID (e.g. web). Defaults to installed default.",
)
@click.option(
    "-n",
    "--top",
    "top_n",
    default=10,
    type=int,
    help="Number of top items to show (default 10).",
)
@click.option(
    "--output",
    "output_path",
    default=None,
    help="Write results to a file. Format is inferred from extension: .json/.csv/.html/.md",
)
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def book(
    book_name: str | None,
    translation_id: str | None,
    top_n: int,
    output_path: str | None,
    show_help: bool,
) -> None:
    """Analyze all verses in a book."""
    if show_help:
        console.print(ANALYTICS_BOOK_HELP)
        return

    if book_name is None:
        console.print("[red]Book name is required.[/red]")
        raise SystemExit(1)

    service = _get_analytic_service(translation_id)
    analysis = service.analyze_book(book_name, translation_id, top_n)

    if output_path is not None:
        _export_analysis_if_requested(
            analysis=analysis, scope_label=book_name, output_path=output_path
        )
        return
    _render_analysis(console, analysis, book_name)


@click.command(
    "compare",
    add_help_option=False,
    context_settings={"help_option_names": []},
)
@click.argument("ref", required=False)
@click.option(
    "--left",
    "translation_a",
    default="fin-1992",
    show_default=True,
    help="Left-side translation ID (default fin-1992).",
)
@click.option(
    "--right",
    "translation_b",
    default="fin17xx",
    show_default=True,
    help="Right-side translation ID (default fin17xx alias for fin-1776).",
)
@click.option(
    "--output",
    "output_path",
    default=None,
    help="Write results to a file. Format is inferred from extension: .json/.csv/.html/.md",
)
@click.option(
    "--help",
    "show_help",
    is_flag=True,
    help="Show this message and exit.",
)
def compare(
    ref: str | None,
    translation_a: str,
    translation_b: str,
    output_path: str | None,
    show_help: bool,
) -> None:
    """Compare two translations side-by-side with diffs and similarity stats."""
    if show_help:
        console.print(ANALYTICS_COMPARE_HELP)
        return

    if ref is None:
        console.print("[red]Reference is required.[/red]")
        raise SystemExit(1)

    conn = get_connection()
    translation_repo = TranslationRepo(conn)

    resolved_a = _resolve_compare_translation_id(translation_repo, translation_a)
    resolved_b = _resolve_compare_translation_id(translation_repo, translation_b)

    missing_ids: list[str] = []
    if resolved_a is None:
        missing_ids.append(translation_a)
    if resolved_b is None:
        missing_ids.append(translation_b)

    if missing_ids:
        missing = ", ".join(missing_ids)
        console.print(
            "[red]Comparison failed.[/red] Missing translation(s): "
            f"{missing}. Install them first with:\n"
            "clible seed install fin-1992\n"
            "clible seed install fin-1776"
        )
        raise SystemExit(1)

    if resolved_a == resolved_b:
        console.print("[red]Comparison failed.[/red] Left and right translations are the same.")
        raise SystemExit(1)

    service = _get_analytic_service(resolved_a)
    comparison = service.compare_translations(ref, resolved_a, resolved_b)

    if not comparison["aligned_verses"]:
        console.print("[red]No verses found for this reference in the selected translations.[/red]")
        raise SystemExit(1)

    left_label = _display_translation_label(translation_a, resolved_a)
    right_label = _display_translation_label(translation_b, resolved_b)

    if output_path is not None:
        _export_compare_if_requested(comparison=comparison, output_path=output_path)
        return
    _render_comparison(console, comparison, left_label, right_label)
