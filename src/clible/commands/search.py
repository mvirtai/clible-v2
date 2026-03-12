"""Search command: find verses by word using FTS5 with scope and statistics."""

import re
from collections import Counter

import click
from rich.panel import Panel
from rich.table import Table

from clible.db.connection import get_connection
from clible.db.repositories.book_repo import BookRepo, Testament
from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo
from clible.services.verse_service import VerseService
from clible.ui.console import console


def _get_verse_service() -> VerseService:
    """Build VerseService with real dependencies."""
    conn = get_connection()
    return VerseService(
        verse_repo=VerseRepo(conn),
        book_repo=BookRepo(conn),
        translation_repo=TranslationRepo(conn),
    )


def _parse_chapter_reference(reference: str) -> tuple[str, int] | None:
    """Parse 'John 3' -> (book_name, chapter). Returns None if invalid."""
    pattern = re.compile(r"^\s*(.+?)\s+(\d+)\s*$", re.IGNORECASE)
    m = pattern.match(reference.strip())
    if not m:
        return None
    return (m.group(1).strip(), int(m.group(2)))


def _highlight_word(text: str, word: str) -> str:
    """Wrap each occurrence of word in Rich bold/yellow markup (case-insensitive)."""
    if not word.strip():
        return text
    pattern = re.compile(re.escape(word), re.IGNORECASE)

    def repl(match: re.Match[str]) -> str:
        return f"[bold yellow]{match.group(0)}[/bold yellow]"

    return pattern.sub(repl, text)


def _filter_verses_by_scope(
    verses: list[dict],
    scope: str,
    scope_value: str | None,
) -> list[dict]:
    """Filter verses based on scope type and value.

    Args:
        verses: All matching verses from FTS search.
        scope: One of: verse, chapter, book, testament, bible.
        scope_value: Reference/name for the scope (e.g. "John 3:16", "John", "OT").

    Returns:
        Filtered list of verses matching the scope.
    """
    if scope == "bible":
        return verses

    if scope == "testament":
        testament_str = scope_value.upper() if scope_value else "OT"
        conn = get_connection()
        book_repo = BookRepo(conn)
        testament_books = book_repo.get_by_testament(Testament(testament_str))
        book_ids = {b["id"] for b in testament_books}
        return [v for v in verses if v["book_id"] in book_ids]

    if scope == "book":
        book_name = scope_value or ""
        conn = get_connection()
        book_repo = BookRepo(conn)
        book = book_repo.get_by_name(book_name)
        if not book:
            matches = book_repo.search(book_name)
            book = matches[0] if matches else None
        if not book:
            return []
        return [v for v in verses if v["book_id"] == book["id"]]

    if scope == "chapter":
        parsed = _parse_chapter_reference(scope_value or "")
        if not parsed:
            return []
        book_name, chapter_num = parsed
        conn = get_connection()
        book_repo = BookRepo(conn)
        book = book_repo.get_by_name(book_name)
        if not book:
            matches = book_repo.search(book_name)
            book = matches[0] if matches else None
        if not book:
            return []
        return [
            v
            for v in verses
            if v["book_id"] == book["id"] and v["chapter"] == chapter_num
        ]

    if scope == "verse":
        from clible.services.verse_service import _parse_reference

        parsed = _parse_reference(scope_value or "")
        if not parsed:
            return []
        book_name, chapter_num, verse_start, verse_end = parsed
        conn = get_connection()
        book_repo = BookRepo(conn)
        book = book_repo.get_by_name(book_name)
        if not book:
            matches = book_repo.search(book_name)
            book = matches[0] if matches else None
        if not book:
            return []
        return [
            v
            for v in verses
            if v["book_id"] == book["id"]
            and v["chapter"] == chapter_num
            and verse_start <= v["verse"] <= verse_end
        ]

    return verses


def _build_statistics(verses: list[dict], word: str) -> dict:
    """Build search statistics from matching verses.

    Returns:
        Dict with total_occurrences, unique_verses, books_with_matches,
        top_books (list of tuples), etc.
    """
    total_occurrences = 0
    book_counter: Counter[str] = Counter()

    for v in verses:
        text_lower = v["text"].lower()
        word_lower = word.lower()
        count_in_verse = text_lower.count(word_lower)
        total_occurrences += count_in_verse
        book_counter[v["book_id"]] += count_in_verse

    return {
        "total_occurrences": total_occurrences,
        "unique_verses": len(verses),
        "books_with_matches": len(book_counter),
        "top_books": book_counter.most_common(5),
    }


def _display_scope_label(scope: str, scope_ref: str | None) -> str:
    """Format scope for display: e.g. testament ref 'ot' -> 'OT'."""
    if scope == "testament" and scope_ref:
        return scope_ref.upper()
    return scope_ref if scope_ref else scope.capitalize()


def _render_statistics(stats: dict, word: str, scope_label: str) -> None:
    """Render search statistics as a Rich table."""
    console.print(
        f"\n[bold cyan]Search Results: '{word}' in {scope_label}[/bold cyan]\n"
    )

    table = Table(title="Statistics", show_header=True)
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")

    table.add_row("Total occurrences", str(stats["total_occurrences"]))
    table.add_row("Unique verses", str(stats["unique_verses"]))
    table.add_row("Books with matches", str(stats["books_with_matches"]))

    console.print(table)

    if stats["top_books"]:
        books_table = Table(title="Top Books", show_header=True)
        books_table.add_column("Rank", justify="right", style="dim")
        books_table.add_column("Book")
        books_table.add_column("Occurrences", justify="right")

        for i, (book_id, count) in enumerate(stats["top_books"], 1):
            books_table.add_row(str(i), book_id, str(count))

        console.print(books_table)


def _ask_user_confirmation(verse_count: int) -> int | None:
    """Ask user how many results they want to see when count is large.

    Returns:
        None to display all, 0 to skip display, or a positive int for limit.
    """
    console.print(
        f"\n[yellow]Found {verse_count} verses. This may produce a lot of output.[/yellow]"
    )
    console.print(
        "\nOptions:\n"
        "  [cyan]all[/cyan]  — Display all verses\n"
        "  [cyan]N[/cyan]    — Display first N verses (e.g. 10, 25)\n"
        "  [cyan]no[/cyan]   — Skip display (show statistics only)"
    )

    choice = (
        click.prompt(
            "\nHow many verses to display?",
            type=str,
            default="no",
            show_default=True,
        )
        .strip()
        .lower()
    )

    if choice in {"all", "a", "yes", "y"}:
        return None
    if choice in {"no", "n", "none", "skip"}:
        return 0

    try:
        limit = int(choice)
        if limit > 0:
            return limit
        console.print("[red]Limit must be positive.[/red]")
        return 0
    except ValueError:
        console.print(f"[red]Invalid choice: '{choice}'. Skipping display.[/red]")
        return 0


def _display_verses(verses: list[dict], word: str, limit: int | None = None) -> None:
    """Display verses with highlighted search word.

    Args:
        verses: List of verse dicts to display.
        word: Search word for highlighting.
        limit: Optional limit on number of verses to display.
    """
    display_verses = verses[:limit] if limit else verses

    console.print()
    for v in display_verses:
        ref_display = f"{v['book_id']} {v['chapter']}:{v['verse']}"
        highlighted = _highlight_word(v["text"], word)
        console.print(Panel(highlighted, title=ref_display, border_style="dim"))

    if limit and len(verses) > limit:
        remaining = len(verses) - limit
        console.print(f"\n[dim]... and {remaining} more verses.[/dim]")


@click.command()
@click.argument("word")
@click.option(
    "--scope",
    "-s",
    type=click.Choice(
        ["verse", "chapter", "book", "testament", "bible"], case_sensitive=False
    ),
    default="bible",
    show_default=True,
    help="Search scope: verse range, chapter, book, testament (OT/NT), or whole bible.",
)
@click.option(
    "--reference",
    "-r",
    "scope_ref",
    default=None,
    help="Reference for scope (e.g. 'John 3:16' for verse, 'John' for book, 'OT' for testament).",
)
@click.option(
    "--translation",
    "-t",
    "translation_id",
    default=None,
    help="Translation ID (e.g. web). Defaults to installed default.",
)
@click.option(
    "--limit",
    "-n",
    "result_limit",
    type=int,
    default=None,
    help="Maximum number of verses to display. If not set, asks for confirmation when >20.",
)
def search(
    word: str,
    scope: str,
    scope_ref: str | None,
    translation_id: str | None,
    result_limit: int | None,
) -> None:
    """Search for verses containing a word with scope and statistics.

    Scope determines where to search:
    - verse: specific verse or range (requires --reference "John 3:16" or "John 3:16-18")
    - chapter: entire chapter (requires --reference "John 3")
    - book: entire book (requires --reference "John")
    - testament: Old or New Testament (requires --reference "OT" or "NT")
    - bible: entire Bible (default)

    Examples:
        clible search grace
        clible search love --scope book --reference John
        clible search peace --scope testament --reference NT -t web
        clible search faith --scope verse --reference "Hebrews 11:1"
    """
    if not word or not word.strip():
        console.print("[red]Search word cannot be empty.[/red]")
        raise SystemExit(1)

    word = word.strip()

    if scope != "bible" and not scope_ref:
        console.print(
            f"[red]Scope '{scope}' requires --reference (-r) to be specified.[/red]\n"
            f"Example: clible search {word} --scope {scope} --reference <value>"
        )
        raise SystemExit(1)

    service = _get_verse_service()
    all_verses = service.search_text(word, translation_id)

    filtered_verses = _filter_verses_by_scope(all_verses, scope, scope_ref)

    if not filtered_verses:
        scope_label = _display_scope_label(scope, scope_ref)
        console.print(
            f'[dim]No verses found containing "{word}" in {scope} scope'
            f"{' (' + scope_label + ')' if scope_ref else ''}.[/dim]"
        )
        return

    scope_label = _display_scope_label(scope, scope_ref)
    stats = _build_statistics(filtered_verses, word)
    _render_statistics(stats, word, scope_label)

    verse_count = len(filtered_verses)
    display_limit = result_limit

    if display_limit is None and verse_count > 20:
        user_choice = _ask_user_confirmation(verse_count)
        if user_choice == 0:
            console.print("\n[dim]Statistics only. Use --limit N next time.[/dim]")
            return
        display_limit = user_choice

    _display_verses(filtered_verses, word, display_limit)
