"""Verse lookup command: fetch verse from local database."""

import click
from rich.console import Console
from rich.panel import Panel

from clible.db.connection import get_connection
from clible.db.repositories.book_repo import BookRepo
from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo
from clible.services.verse_service import VerseService


def _get_verse_service() -> VerseService:
    """Build VerseService with real dependencies."""
    conn = get_connection()
    return VerseService(
        verse_repo=VerseRepo(conn),
        book_repo=BookRepo(conn),
        translation_repo=TranslationRepo(conn),
    )


@click.command()
@click.argument("reference")
@click.option(
    "--translation",
    "-t",
    "translation_id",
    default=None,
    help="Translation ID (e.g. web). Defaults to installed default.",
)
def verse(reference: str, translation_id: str | None) -> None:
    """Display a verse from the local database.

    Example: clible verse "John 3:16"
    Example: clible verse "Genesis 1:1" -t web

    Requires at least one translation to be installed (clible seed install web).
    """
    console = Console()
    service = _get_verse_service()
    result = service.get_verse(reference, translation_id)

    if not result:
        console.print(
            "[red]Verse not found.[/red] "
            "Check the reference (e.g. 'John 3:16') and that you have run: clible seed install web"
        )
        raise SystemExit(1)

    ref_display = f"{result['book_id']} {result['chapter']}:{result['verse']}"
    console.print(Panel(result["text"], title=ref_display, border_style="dim"))
