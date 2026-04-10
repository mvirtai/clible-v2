"""Verse lookup command: fetch verse from local database."""

import math

import click
from rich.panel import Panel

from clible.commands import get_verse_service
from clible.db.connection import get_connection
from clible.db.repositories.translation_repo import TranslationRepo
from clible.services.reference_parser import ReferenceScope, parse_reference
from clible.ui.console import console
from clible.ui.export import write_text
from clible.ui.export_cli import EXPORT_PARAM, ExportConfig
from clible.ui.help_texts import VERSE_HELP
from clible.ui.verse_search_export import export_verses_bundle


@click.command(add_help_option=False, context_settings={"help_option_names": []})
@click.argument("reference", required=False)
@click.option(
    "--translation",
    "-t",
    "translation_id",
    default=None,
    help="Translation ID (e.g. web). Defaults to installed default.",
)
@click.option(
    "--export",
    "-exp",
    type=EXPORT_PARAM,
    default=None,
    help="Export to file: 'PATH=~/out,FILENAME=myfile,FORMAT=json' (all optional).",
)
@click.option(
    "--json",
    is_flag=True,
    default=False,
    help="Output pure JSON to stdout (for web bridge).",
)
@click.option(
    "--page",
    type=click.IntRange(min=1),
    default=1,
    help="Page number (1-based) for chapter or whole-book references; ignored for verse ranges.",
)
@click.option(
    "--page-size",
    type=click.IntRange(min=0),
    default=50,
    help="Verses per page for chapter or whole-book; 0 = show all in one view.",
)
@click.option(
    "--stdout-export",
    type=click.Choice(["csv", "html", "json", "md", "txt", "xml"], case_sensitive=False),
    help="Output formatted content directly to stdout (for web download).",
)
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def verse(
    reference: str | None,
    translation_id: str | None,
    export: ExportConfig | None,
    json: bool,
    page: int,
    page_size: int,
    stdout_export: str | None,
    show_help: bool,
) -> None:
    """Display verse(s) from the local database.

    Supports verse or range ("John 3:16", "John 3:1-6"), a full chapter ("John 3"),
    or a whole book ("John"). Chapter and book output is paginated unless
    --page-size is 0.

    Example: clible verse "John 3:16"
    Example: clible verse "John 3:1-6" -t kjv
    Example: clible verse "John 3"
    Example: clible verse "Psalms" --page 2

    Requires at least one translation to be installed (clible seed install web).
    """
    if show_help:
        console.print(VERSE_HELP)
        return

    if reference is None:
        console.print("[red]Reference is required.[/red]")
        raise SystemExit(1)

    service = get_verse_service()
    verses = service.get_verses(reference, translation_id)

    if not verses:
        console.print(
            "[red]Verse(s) not found.[/red] "
            "Check the reference (e.g. 'John 3:16', 'John 3:1-6', 'John 3', or 'John') "
            "and that you have run: clible seed install web"
        )
        raise SystemExit(1)

    if export is not None:
        try:
            out_path = export.resolve()
            resolved_t = translation_id
            if resolved_t is None:
                conn = get_connection()
                default = TranslationRepo(conn).get_default()
                conn.close()
                resolved_t = default["id"] if default else None
            content = export_verses_bundle(
                verses,
                kind="verse",
                title=f"Verses: {reference}",
                format=export.format,
                translation_id=resolved_t,
            )
            write_text(out_path, content)
            console.print(
                f"[green]Exported {export.format}:[/green] {out_path.resolve()}\n"
                f"[dim]  PATH={export.path}  FILENAME={export.filename}  "
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

        content = export_verses_bundle(
            verses,
            kind="verse",
            title=f"Verses: {reference}",
            format=stdout_export.lower(),
            translation_id=resolved_t,
        )
        print(content)
        return

    if json:
        parsed = parse_reference(reference)
        # If this is a chapter/book query and paging is requested, match the UI output
        # by applying the same slicing rules as below.
        to_show = verses
        is_pageable_scope = parsed and parsed.scope in (
            ReferenceScope.CHAPTER,
            ReferenceScope.BOOK,
        )
        if is_pageable_scope and page_size > 0:
            total = len(verses)
            pages = max(1, math.ceil(total / page_size))
            if page < 1 or page > pages:
                console.print(
                    f"[red]Invalid --page {page}: valid range is 1–{pages} "
                    f"({total} verse(s), page-size {page_size}).[/red]"
                )
                raise SystemExit(1)
            start = (page - 1) * page_size
            to_show = verses[start : start + page_size]

        # Reuse the existing verse-search JSON payload schema.
        content = export_verses_bundle(
            to_show,
            kind="verse",
            title=f"Verses: {reference}",
            format="json",
            translation_id=translation_id,
            search_word=None,
            scope=None,
            scope_ref=None,
            stats=None,
        )
        # `export_verses_bundle` returns a JSON string; web bridge expects stdout-only JSON.
        print(content)
        return

    parsed = parse_reference(reference)
    to_show = verses
    if parsed and parsed.scope in (ReferenceScope.CHAPTER, ReferenceScope.BOOK) and page_size > 0:
        total = len(verses)
        pages = max(1, math.ceil(total / page_size))
        if page < 1 or page > pages:
            console.print(
                f"[red]Invalid --page {page}: valid range is 1–{pages} "
                f"({total} verse(s), page-size {page_size}).[/red]"
            )
            raise SystemExit(1)
        start = (page - 1) * page_size
        to_show = verses[start : start + page_size]
        first = start + 1
        last = start + len(to_show)
        console.print(
            f"[dim]Showing verses {first}–{last} of {total} "
            f"(page {page} of {pages}). "
            f"Use --page N and --page-size {page_size} to navigate; "
            f"--page-size 0 shows all.[/dim]\n"
        )

    for v in to_show:
        ref_display = f"{v['book_id']} {v['chapter']}:{v['verse']}"
        console.print(Panel(v["text"], title=ref_display, border_style="dim"))
