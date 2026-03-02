"""Seed subcommands: install, list, available, remove."""

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from clible.db.connection import get_connection
from clible.db.repositories.book_repo import BookRepo
from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo
from clible.parsers.usfx_parser import USFXParser
from clible.services.seed_service import SeedService


def _get_seed_service() -> SeedService:
    """Build SeedService with real dependencies."""
    conn = get_connection()
    return SeedService(
        translation_repo=TranslationRepo(conn),
        verse_repo=VerseRepo(conn),
        book_repo=BookRepo(conn),
        parser=USFXParser(),
    )


@click.command("install")
@click.argument("translation_id")
def install(translation_id: str) -> None:
    """Install a Bible translation by ID.

    Example: clible seed install web

    Downloads, parses, and stores the translation locally.
    Only USFX format is supported currently.
    """
    console = Console()
    try:
        service = _get_seed_service()
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.fields[msg]}"),
            console=console,
        ) as progress:
            task = progress.add_task("install", msg="Starting...")
            stats = service.seed_translation(
                translation_id,
                progress_callback=lambda m: progress.update(task, msg=m),
            )
        console.print(
            f"[green]Installed {stats['translation_id']}: "
            f"{stats['verses_installed']} verses in {stats['duration_seconds']}s[/green]"
        )
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)


@click.command("list")
def list_installed() -> None:
    """List installed translations."""
    console = Console()
    service = _get_seed_service()
    installed = service.list_installed()
    if not installed:
        console.print("[dim]No translations installed. Run: clible seed install web[/dim]")
        return
    table = Table(title="Installed translations")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Language")
    table.add_column("Format")
    for t in installed:
        table.add_row(
            t["id"],
            t["name"],
            t["language"],
            t["format"],
        )
    console.print(table)


@click.command("available")
def available() -> None:
    """List available translations from the catalog."""
    console = Console()
    service = _get_seed_service()
    items = service.list_available()
    table = Table(title="Available translations")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Language")
    table.add_column("Format")
    table.add_column("Size (MB)")
    for t in items:
        table.add_row(
            t["id"],
            t["name"],
            t["language"],
            t["format"],
            str(t.get("size_mb", "—")),
        )
    console.print(table)


@click.command("remove")
@click.argument("translation_id")
def remove(translation_id: str) -> None:
    """Remove an installed translation.

    Example: clible seed remove web
    """
    console = Console()
    try:
        service = _get_seed_service()
        service.remove_translation(translation_id)
        console.print(f"[green]Removed {translation_id}[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)
