"""Verse lookup command: fetch verse from local database."""

import click
from rich.panel import Panel

from clible.db.connection import get_connection
from clible.db.repositories.book_repo import BookRepo
from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo
from clible.services.verse_service import VerseService
from clible.ui.console import console
from clible.ui.export import write_text
from clible.ui.export_cli import EXPORT_PARAM, ExportConfig
from clible.ui.help_texts import VERSE_HELP
from clible.ui.verse_search_export import export_verses_bundle


def _get_verse_service() -> VerseService:
    """Build VerseService with real dependencies."""
    conn = get_connection()
    return VerseService(
        verse_repo=VerseRepo(conn),
        book_repo=BookRepo(conn),
        translation_repo=TranslationRepo(conn),
    )


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
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def verse(
    reference: str | None,
    translation_id: str | None,
    export: ExportConfig | None,
    show_help: bool,
) -> None:
    """Display verse(s) from the local database.

    Supports single verse or range: "John 3:16" or "John 3:1-6".

    Example: clible verse "John 3:16"
    Example: clible verse "John 3:1-6" -t kjv

    Requires at least one translation to be installed (clible seed install web).
    """
    if show_help:
        console.print(VERSE_HELP)
        return

    if reference is None:
        console.print("[red]Reference is required.[/red]")
        raise SystemExit(1)

    service = _get_verse_service()
    verses = service.get_verses(reference, translation_id)

    if not verses:
        console.print(
            "[red]Verse(s) not found.[/red] "
            "Check the reference (e.g. 'John 3:16' or 'John 3:1-6') and that you have run: "
            "clible seed install web"
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

    for v in verses:
        ref_display = f"{v['book_id']} {v['chapter']}:{v['verse']}"
        console.print(Panel(v["text"], title=ref_display, border_style="dim"))
