"""Analytics commands: text analysis for verses, chapters, and books."""

import click
from rich.console import Console
from rich.table import Table

from clible.db.connection import get_connection
from clible.db.repositories.book_repo import BookRepo
from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo
from clible.services.analytic_service import AnalyticService
from clible.services.verse_service import VerseService


def _get_analytic_service() -> AnalyticService:
    """Build AnalyticService with real dependencies."""
    conn = get_connection()
    verse_service = VerseService(
        verse_repo=VerseRepo(conn),
        book_repo=BookRepo(conn),
        translation_repo=TranslationRepo(conn),
    )
    return AnalyticService(verse_service=verse_service)


def _render_analysis(console: Console, analysis: dict, scope_label: str) -> None:
    """Render analysis results as Rich tables.

    Args:
        console: Rich console for output.
        analysis: Analysis dict with metrics and top-N lists.
        scope_label: Label for the scope (e.g. "John 3:16-18", "John 3", "John").
    """
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


@click.command()
@click.argument("ref")
@click.option(
    "--translation",
    "-t",
    "translation_id",
    default=None,
    help="Translation ID (e.g. web). Defaults to installed default.",
)
@click.option(
    "--top",
    "-n",
    "top_n",
    default=10,
    type=int,
    help="Number of top items to show (default 10).",
)
def reference(ref: str, translation_id: str | None, top_n: int) -> None:
    """Analyze verses in a reference (e.g. 'John 3:16' or 'John 3:16-18').

    Example: clible analytics reference "John 3:16-18"
    Example: clible analytics reference "Genesis 1:1" -t kjv --top 5
    """
    console = Console()
    service = _get_analytic_service()

    analysis = service.analyze_reference(ref, translation_id, top_n)
    _render_analysis(console, analysis, ref)


@click.command()
@click.argument("book_name")
@click.argument("chapter_num", type=int)
@click.option(
    "--translation",
    "-t",
    "translation_id",
    default=None,
    help="Translation ID (e.g. web). Defaults to installed default.",
)
@click.option(
    "--top",
    "-n",
    "top_n",
    default=10,
    type=int,
    help="Number of top items to show (default 10).",
)
def chapter(book_name: str, chapter_num: int, translation_id: str | None, top_n: int) -> None:
    """Analyze all verses in a chapter.

    Example: clible analytics chapter John 3
    Example: clible analytics chapter Genesis 1 -t kjv --top 5
    """
    console = Console()
    service = _get_analytic_service()

    analysis = service.analyze_chapter(book_name, chapter_num, translation_id, top_n)
    scope_label = f"{book_name} {chapter_num}"
    _render_analysis(console, analysis, scope_label)


@click.command()
@click.argument("book_name")
@click.option(
    "--translation",
    "-t",
    "translation_id",
    default=None,
    help="Translation ID (e.g. web). Defaults to installed default.",
)
@click.option(
    "--top",
    "-n",
    "top_n",
    default=10,
    type=int,
    help="Number of top items to show (default 10).",
)
def book(book_name: str, translation_id: str | None, top_n: int) -> None:
    """Analyze all verses in a book.

    Example: clible analytics book John
    Example: clible analytics book Genesis -t kjv --top 5
    """
    console = Console()
    service = _get_analytic_service()

    analysis = service.analyze_book(book_name, translation_id, top_n)
    _render_analysis(console, analysis, book_name)
