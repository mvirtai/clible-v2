"""Seed subcommands: install, list, available, remove."""

import click
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from clible.db.connection import get_connection
from clible.db.repositories.book_repo import BookRepo
from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo
from clible.parsers.factory import create_parser
from clible.services.seed_service import SeedService
from clible.services.translation_catalog_sync import (
    TranslationCatalogSyncError,
    sync_translations_catalog,
)
from clible.ui.console import console
from clible.ui.help_texts import (
    SEED_AVAILABLE_HELP,
    SEED_INSTALL_HELP,
    SEED_LIST_HELP,
    SEED_REMOVE_HELP,
    SEED_SYNC_CATALOG_HELP,
)


def _get_seed_service() -> SeedService:
    """Build SeedService with real dependencies."""
    conn = get_connection()
    return SeedService(
        translation_repo=TranslationRepo(conn),
        verse_repo=VerseRepo(conn),
        book_repo=BookRepo(conn),
        parser_factory=create_parser,
    )


@click.command("install", add_help_option=False, context_settings={"help_option_names": []})
@click.argument("translation_id", required=False)
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def install(translation_id: str | None, show_help: bool) -> None:
    """Install a Bible translation by ID.

    Example: clible seed install web
    Example: clible seed install kjv
    Example: clible seed install test-zefania

    Downloads, parses, and stores the translation locally.
    Supported formats: USFX (e.g. web), OSIS (e.g. kjv), BEBLIA (e.g. fin-1992),
    ZEFANIA (e.g. test-zefania).
    """
    if show_help:
        console.print(SEED_INSTALL_HELP)
        return

    if translation_id is None:
        console.print("[red]Translation ID is required.[/red]")
        raise SystemExit(1)

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


@click.command("list", add_help_option=False, context_settings={"help_option_names": []})
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def list_installed(show_help: bool) -> None:
    """List installed translations."""
    if show_help:
        console.print(SEED_LIST_HELP)
        return

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


@click.command("available", add_help_option=False, context_settings={"help_option_names": []})
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def available(show_help: bool) -> None:
    """List available translations from the catalog."""
    if show_help:
        console.print(SEED_AVAILABLE_HELP)
        return

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


@click.command("sync-catalog", add_help_option=False, context_settings={"help_option_names": []})
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def sync_catalog(show_help: bool) -> None:
    """Sync the local catalog (`src/clible/data/translations.json`) from upstream repos."""
    if show_help:
        console.print(SEED_SYNC_CATALOG_HELP)
        return

    try:
        stats = sync_translations_catalog()
    except TranslationCatalogSyncError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)

    console.print(
        f"[green]Catalog synced:[/green] "
        f"existing={stats['existing_count']} "
        f"discovered={stats['discovered_count']} "
        f"merged={stats['merged_count']}"
    )


@click.command("remove", add_help_option=False, context_settings={"help_option_names": []})
@click.argument("translation_id", required=False)
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def remove(translation_id: str | None, show_help: bool) -> None:
    """Remove an installed translation.

    Example: clible seed remove web
    """
    if show_help:
        console.print(SEED_REMOVE_HELP)
        return

    if translation_id is None:
        console.print("[red]Translation ID is required.[/red]")
        raise SystemExit(1)

    try:
        service = _get_seed_service()
        service.remove_translation(translation_id)
        console.print(f"[green]Removed {translation_id}[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)
