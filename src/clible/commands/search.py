"""Search command: find verses by word using FTS5 with scope and statistics."""

import re

import click
from rich.panel import Panel
from rich.table import Table

from . import get_saved_search_service, get_verse_service
from clible.db.connection import get_connection
from clible.db.repositories.translation_repo import TranslationRepo
from clible.ui.console import console
from clible.ui.export import write_text
from clible.ui.export_cli import EXPORT_PARAM, ExportConfig
from clible.ui.help_texts import SEARCH_HELP
from clible.ui.verse_search_export import export_verses_bundle


def _highlight_word(text: str, word: str) -> str:
    """Wrap each occurrence of word in Rich bold/yellow markup (case-insensitive)."""
    if not word.strip():
        return text
    pattern = re.compile(re.escape(word), re.IGNORECASE)

    def repl(match: re.Match[str]) -> str:
        return f"[bold yellow]{match.group(0)}[/bold yellow]"

    return pattern.sub(repl, text)


def display_scope_label(scope: str, scope_ref: str | None) -> str:
    """Format scope for display: e.g. testament ref 'ot' -> 'OT'."""
    if scope == "testament" and scope_ref:
        return scope_ref.upper()
    return scope_ref if scope_ref else scope.capitalize()


def render_statistics(stats: dict, word: str, scope_label: str) -> None:
    """Render search statistics as a Rich table."""
    console.print(f"\n[bold cyan]Search Results: '{word}' in {scope_label}[/bold cyan]\n")

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


def display_verses(verses: list[dict], word: str, limit: int | None = None) -> None:
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


@click.command(add_help_option=False, context_settings={"help_option_names": []})
@click.argument("word", required=False)
@click.option(
    "--scope",
    "-s",
    type=click.Choice(["verse", "chapter", "book", "testament", "bible"], case_sensitive=False),
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
@click.option(
    "--export",
    "-exp",
    type=EXPORT_PARAM,
    default=None,
    help="Export to file: 'PATH=~/out,FILENAME=search,FORMAT=json' (all optional).",
)
@click.option(
    "--json",
    is_flag=True,
    default=False,
    help="Output pure JSON to stdout (for web bridge).",
)
@click.option(
    "--stdout-export",
    type=click.Choice(["csv", "html", "json", "md", "txt", "xml"], case_sensitive=False),
    help="Output formatted content directly to stdout (for web download).",
)
@click.option(
    "--save",
    "save_name",
    default=None,
    help="Save search parameters to current scope under this name.",
)
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def search(
    word: str | None,
    scope: str,
    scope_ref: str | None,
    translation_id: str | None,
    result_limit: int | None,
    export: ExportConfig | None,
    json: bool,
    stdout_export: str | None,
    save_name: str | None,
    show_help: bool,
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
    if show_help:
        console.print(SEARCH_HELP)
        return

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

    service = get_verse_service()
    filtered_verses = service.search_text(
        word,
        translation_id=translation_id,
        scope=scope,
        scope_ref=scope_ref,
    )

    if save_name:
        get_saved_search_service().save_search(
            name=save_name,
            query_text=word,
            search_scope=scope,
            scope_value=scope_ref,
            translation_id=translation_id,
        )
        console.print(f"[green]Saved search '{save_name}' to current scope.[/green]")

    if not filtered_verses:
        scope_label = display_scope_label(scope, scope_ref)
        if json:
            resolved_t = translation_id
            if resolved_t is None:
                conn = get_connection()
                default = TranslationRepo(conn).get_default()
                conn.close()
                resolved_t = default["id"] if default else None
            stats = service.get_search_statistics([], word)
            content = export_verses_bundle(
                [],
                kind="search",
                title=f'Search: "{word}" in {scope_label}',
                format="json",
                translation_id=resolved_t,
                search_word=word,
                scope=scope,
                scope_ref=scope_ref,
                stats=stats,
            )
            print(content)
            return
        console.print(
            f'[dim]No verses found containing "{word}" in {scope} scope'
            f"{' (' + scope_label + ')' if scope_ref else ''}.[/dim]"
        )
        return

    scope_label = display_scope_label(scope, scope_ref)
    stats = service.get_search_statistics(filtered_verses, word)

    if export is not None:
        try:
            out_path = export.resolve()
            resolved_t = translation_id
            if resolved_t is None:
                conn = get_connection()
                default = TranslationRepo(conn).get_default()
                conn.close()
                resolved_t = default["id"] if default else None
            title = f'Search: "{word}" in {scope_label}'
            content = export_verses_bundle(
                filtered_verses,
                kind="search",
                title=title,
                format=export.format,
                translation_id=resolved_t,
                search_word=word,
                scope=scope,
                scope_ref=scope_ref,
                stats=stats,
            )
            write_text(out_path, content)
            console.print(
                f"[green]Exported {export.format} to[/green] {out_path.resolve()}\n"
                f"[dim]PATH={export.path}, FILENAME={export.filename}, "
                f"FORMAT={export.format}[/dim]"
            )
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise SystemExit(1)
        except OSError as e:
            console.print(f"[red]Failed to write output file: {e}[/red]")
            raise SystemExit(1)
        return

    if stdout_export is not None:
        resolved_t = translation_id
        if resolved_t is None:
            conn = get_connection()
            default = TranslationRepo(conn).get_default()
            conn.close()
            resolved_t = default["id"] if default else None

        title = f'Search: "{word}" in {scope_label}'
        content = export_verses_bundle(
            filtered_verses,
            kind="search",
            title=title,
            format=stdout_export.lower(),
            translation_id=resolved_t,
            search_word=word,
            scope=scope,
            scope_ref=scope_ref,
            stats=stats,
        )
        print(content)
        return

    if json:
        scope_label = display_scope_label(scope, scope_ref)
        verses_for_json = filtered_verses
        if result_limit is not None:
            verses_for_json = filtered_verses[: max(result_limit, 0)]
        content = export_verses_bundle(
            verses_for_json,
            kind="search",
            title=f'Search: "{word}" in {scope_label}',
            format="json",
            translation_id=translation_id,
            search_word=word,
            scope=scope,
            scope_ref=scope_ref,
            stats=stats,
        )
        print(content)
        return

    render_statistics(stats, word, scope_label)

    verse_count = len(filtered_verses)
    display_limit = result_limit

    if display_limit is None and verse_count > 20:
        user_choice = _ask_user_confirmation(verse_count)
        if user_choice == 0:
            console.print("\n[dim]Statistics only. Use --limit N next time.[/dim]")
            return
        display_limit = user_choice

    display_verses(filtered_verses, word, display_limit)
