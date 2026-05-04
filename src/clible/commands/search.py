"""Search command: FTS5 phrase/boolean, wildcard (REGEXP), scope, history."""

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

import click
from rich.panel import Panel
from rich.table import Table

from clible.commands import (
    get_saved_search_service,
    get_search_history_service,
    get_verse_service,
)
from clible.db.connection import get_connection
from clible.db.repositories.translation_repo import TranslationRepo
from clible.services.search_query import SearchQuery
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


def _highlight_terms(text: str, terms: list[str]) -> str:
    """Highlight any of the given substrings (no regex in terms)."""
    safe = [t for t in terms if t and t.strip()]
    if not safe:
        return text
    pattern = re.compile("|".join(re.escape(t) for t in safe), re.IGNORECASE)

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


def display_verses(
    verses: Sequence[Mapping[str, Any]],
    primary_highlight: str,
    limit: int | None = None,
    translation_id: str | None = None,
    *,
    terms_for_highlight: list[str] | None = None,
) -> None:
    """Display verses with highlighted match text."""
    to_show = verses[:limit] if limit else verses

    console.print()
    for v in to_show:
        ref_display = f"{v['book_id']} {v['chapter']}:{v['verse']}"
        if translation_id:
            ref_display = f"{ref_display} ({translation_id})"
        if terms_for_highlight and len(terms_for_highlight) > 1:
            highlighted = _highlight_terms(v["text"], terms_for_highlight)
        else:
            hl = terms_for_highlight[0] if terms_for_highlight else primary_highlight
            highlighted = _highlight_word(v["text"], hl)
        console.print(Panel(highlighted, title=ref_display, border_style="dim"))

    if limit and len(verses) > limit:
        remaining = len(verses) - limit
        console.print(f"\n[dim]... and {remaining} more verses.[/dim]")


def _query_display_text(q: SearchQuery) -> str:
    return " ".join(q.terms).strip()


def _stats_count_key(q: SearchQuery) -> str:
    if not q.terms:
        return ""
    if q.mode == "boolean" and len(q.terms) > 1:
        return q.terms[0]
    return " ".join(q.terms).strip()


@click.command(add_help_option=False, context_settings={"help_option_names": []})
@click.argument("word", nargs=-1, required=False)
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
    "json_output",
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
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["phrase", "words", "wildcard"], case_sensitive=False),
    default="phrase",
    show_default=True,
    help=("Search mode: phrase (exact), words (AND/OR/NOT), wildcard (lov* = love/loves/loving)."),
)
@click.option(
    "--operator",
    type=click.Choice(["and", "or", "not"], case_sensitive=False),
    default="and",
    show_default=True,
    help="Logical operator for --mode words.",
)
@click.option(
    "--book",
    "-b",
    "book_filter",
    default=None,
    help="Shortcut: search within one book (e.g. John).",
)
@click.option(
    "--nt",
    "testament_filter",
    flag_value="NT",
    default=None,
    help="Shortcut: New Testament only.",
)
@click.option(
    "--ot",
    "testament_filter",
    flag_value="OT",
    default=None,
    help="Shortcut: Old Testament only.",
)
@click.option(
    "--history",
    "show_history",
    is_flag=True,
    default=False,
    help="Show recent search history.",
)
@click.option(
    "--history-run",
    "history_run",
    type=int,
    default=None,
    help="Re-run search #N from history (see --history).",
)
@click.option(
    "--clear-history",
    "clear_history",
    is_flag=True,
    default=False,
    help="Delete all search history entries.",
)
@click.option(
    "--list-saved",
    "list_saved",
    is_flag=True,
    default=False,
    help="List saved searches for the current scope (use with --json for machine output).",
)
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def search(
    word: tuple[str, ...],
    scope: str,
    scope_ref: str | None,
    translation_id: str | None,
    result_limit: int | None,
    export: ExportConfig | None,
    json_output: bool,
    stdout_export: str | None,
    save_name: str | None,
    mode: str,
    operator: str,
    book_filter: str | None,
    testament_filter: str | None,
    show_history: bool,
    history_run: int | None,
    clear_history: bool,
    list_saved: bool,
    show_help: bool,
) -> None:
    """Search for verses; supports phrase, boolean, wildcard, scope, and history."""
    if show_help:
        console.print(SEARCH_HELP)
        return

    if clear_history:
        history_svc = get_search_history_service()
        n = history_svc.clear()
        if json_output:
            print(json.dumps({"ok": True, "deleted": n}))
        else:
            console.print(f"[green]Cleared {n} search history entries.[/green]")
        return

    if list_saved:
        items = get_saved_search_service().list_saved_searches()
        if json_output:
            print(json.dumps(items))
        else:
            if not items:
                console.print("[dim]No saved searches in current scope.[/dim]")
            else:
                t = Table(title="Saved Searches")
                t.add_column("Name", style="cyan")
                t.add_column("Query", style="green")
                t.add_column("Scope", style="dim")
                for item in items:
                    scope_str = f"{item['search_scope']}"
                    if item["scope_value"]:
                        scope_str += f" ({item['scope_value']})"
                    t.add_row(item["name"], item["query_text"], scope_str)
                console.print(t)
        return

    if show_history:
        history_svc = get_search_history_service()
        rows = history_svc.list_recent(10)
        if json_output:
            print(json.dumps([dict(r) for r in rows]))
            return
        if not rows:
            console.print("[dim]No search history yet.[/dim]")
            return
        table = Table(title="Recent Searches", show_header=True)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Query")
        table.add_column("Scope")
        table.add_column("Mode")
        table.add_column("Results", justify="right")
        for i, row in enumerate(rows, 1):
            scope_display = row["scope_value"] or row["search_scope"].capitalize()
            table.add_row(
                str(i),
                row["query_text"],
                scope_display,
                row["mode"],
                str(row["result_count"]),
            )
        console.print(table)
        return

    if history_run is not None:
        history_svc = get_search_history_service()
        rows = history_svc.list_recent(10)
        if history_run < 1 or history_run > len(rows):
            console.print(
                f"[red]Invalid history index {history_run}. Use --history to see available.[/red]"
            )
            raise SystemExit(1)
        entry = rows[history_run - 1]
        text = entry["query_text"]
        scope = entry["search_scope"]
        scope_ref = entry["scope_value"]
        translation_id = entry["translation_id"] or translation_id
        if entry["mode"] == "boolean":
            mode = "words"
            word = tuple(text.split())
        else:
            mode = entry["mode"] if entry["mode"] in ("phrase", "wildcard") else "phrase"
            word = (text,) if text else tuple()
        console.print(f"[dim]Re-running: {text} ({scope})[/dim]")

    if not word or not any(x.strip() for x in word):
        console.print("[red]Search text cannot be empty.[/red]")
        raise SystemExit(1)

    if book_filter:
        scope = "book"
        scope_ref = book_filter

    if testament_filter:
        scope = "testament"
        scope_ref = testament_filter

    if scope != "bible" and not scope_ref:
        qpreview = " ".join(word)
        console.print(
            f"[red]Scope '{scope}' requires --reference (-r) or a shorthand like --book.[/red]\n"
            f"Example: clible search {qpreview} --scope {scope} --reference <value>"
        )
        raise SystemExit(1)

    op_upper: str = operator.upper()
    internal_mode: str = "boolean" if mode == "words" else mode

    if internal_mode == "boolean":
        terms = [t.strip() for t in word if t.strip()]
    else:
        terms = [" ".join(word).strip()]

    query = SearchQuery(
        terms=terms,
        operator=op_upper,  # type: ignore[arg-type]
        mode=internal_mode,  # type: ignore[arg-type]
        translation_id=translation_id,
        scope=scope,
        scope_ref=scope_ref,
    )

    service = get_verse_service()
    filtered_verses = service.search_advanced(query)
    display_q = _query_display_text(query)

    history_svc = get_search_history_service()
    history_svc.record(query, len(filtered_verses))

    if save_name:
        get_saved_search_service().save_search(
            name=save_name,
            query_text=display_q,
            search_scope=scope,
            scope_value=scope_ref,
            translation_id=translation_id,
        )
        console.print(f"[green]Saved search '{save_name}' to current scope.[/green]")

    stats_key = _stats_count_key(query)
    highlight_list = list(query.terms) if query.mode == "boolean" else None

    if not filtered_verses:
        scope_label = display_scope_label(scope, scope_ref)
        if json_output:
            resolved_t = translation_id
            if resolved_t is None:
                conn = get_connection()
                default = TranslationRepo(conn).get_default()
                conn.close()
                resolved_t = default["id"] if default else None
            stats = service.get_search_statistics([], stats_key)
            content = export_verses_bundle(
                [],
                kind="search",
                title=f'Search: "{display_q}" in {scope_label}',
                format="json",
                translation_id=resolved_t,
                search_word=display_q,
                scope=scope,
                scope_ref=scope_ref,
                stats=stats,
                highlight_terms=list(query.terms),
                search_mode=query.mode,
                search_operator=query.operator if query.mode == "boolean" else None,
            )
            print(content)
            return
        console.print(
            f'[dim]No verses found containing "{display_q}" in {scope} scope'
            f"{' (' + scope_label + ')' if scope_ref else ''}.[/dim]"
        )
        return

    scope_label = display_scope_label(scope, scope_ref)
    stats = service.get_search_statistics(filtered_verses, stats_key)

    if export is not None:
        try:
            out_path = export.resolve()
            resolved_t = translation_id
            if resolved_t is None:
                conn = get_connection()
                default = TranslationRepo(conn).get_default()
                conn.close()
                resolved_t = default["id"] if default else None
            title = f'Search: "{display_q}" in {scope_label}'
            content = export_verses_bundle(
                filtered_verses,
                kind="search",
                title=title,
                format=export.format,
                translation_id=resolved_t,
                search_word=display_q,
                scope=scope,
                scope_ref=scope_ref,
                stats=stats,
                highlight_terms=list(query.terms),
                search_mode=query.mode,
                search_operator=query.operator if query.mode == "boolean" else None,
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

        title = f'Search: "{display_q}" in {scope_label}'
        content = export_verses_bundle(
            filtered_verses,
            kind="search",
            title=title,
            format=stdout_export.lower(),
            translation_id=resolved_t,
            search_word=display_q,
            scope=scope,
            scope_ref=scope_ref,
            stats=stats,
            highlight_terms=list(query.terms),
            search_mode=query.mode,
            search_operator=query.operator if query.mode == "boolean" else None,
        )
        print(content)
        return

    if json_output:
        verses_for_json = filtered_verses
        if result_limit is not None:
            verses_for_json = filtered_verses[: max(result_limit, 0)]
        content = export_verses_bundle(
            verses_for_json,
            kind="search",
            title=f'Search: "{display_q}" in {scope_label}',
            format="json",
            translation_id=translation_id,
            search_word=display_q,
            scope=scope,
            scope_ref=scope_ref,
            stats=stats,
            highlight_terms=list(query.terms),
            search_mode=query.mode,
            search_operator=query.operator if query.mode == "boolean" else None,
        )
        print(content)
        return

    render_statistics(stats, display_q, scope_label)

    verse_count = len(filtered_verses)
    display_limit = result_limit

    if display_limit is None and verse_count > 20:
        user_choice = _ask_user_confirmation(verse_count)
        if user_choice == 0:
            console.print("\n[dim]Statistics only. Use --limit N next time.[/dim]")
            return
        display_limit = user_choice

    resolved_t = translation_id
    if resolved_t is None:
        conn = get_connection()
        default = TranslationRepo(conn).get_default()
        conn.close()
        resolved_t = default["id"] if default else None

    display_verses(
        filtered_verses,
        display_q,
        display_limit,
        translation_id=resolved_t,
        terms_for_highlight=highlight_list,
    )
