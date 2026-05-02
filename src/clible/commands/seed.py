"""Seed subcommands: install, list, available, remove."""

import json
from pathlib import Path

import click
import requests
import structlog
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from clible.db.connection import get_connection
from clible.db.repositories.book_repo import BookRepo
from clible.db.repositories.translation_repo import TranslationRepo
from clible.db.repositories.verse_repo import VerseRepo
from clible.parsers.combined_parser import CombinedParser
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

log = structlog.get_logger(__name__)


def _get_seed_service() -> SeedService:
    """Build SeedService with real dependencies."""
    conn = get_connection()
    return SeedService(
        translation_repo=TranslationRepo(conn),
        verse_repo=VerseRepo(conn),
        book_repo=BookRepo(conn),
        xml_parser=CombinedParser(),
    )


def _load_available_catalog() -> list[dict]:
    """Load available translations from the bundled catalog without DB access."""
    catalog_path = Path(__file__).resolve().parent.parent / "data" / "translations.json"
    with open(catalog_path, encoding="utf-8") as f:
        catalog = json.load(f)
    return [
        {"id": tid, **{k: v for k, v in meta.items() if k != "filename"}}
        for tid, meta in catalog.items()
    ]


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
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
    except requests.exceptions.ConnectionError:
        console.print(
            "[red]Error:[/red] Could not connect to download server. "
            "Check your internet connection."
        )
        raise SystemExit(1)
    except requests.exceptions.Timeout:
        console.print("[red]Error:[/red] Request timed out after all retries. Try again later.")
        raise SystemExit(1)
    except requests.exceptions.RequestException as e:
        log.warning(
            "seed.install.http_error",
            translation_id=translation_id,
            error=str(e),
        )
        console.print(f"[red]Error:[/red] Download failed: {e}")
        raise SystemExit(1)
    except Exception:
        log.exception("seed.install.unexpected", translation_id=translation_id)
        console.print(
            "[red]Error:[/red] An unexpected error occurred. "
            "Set CLIBLE_LOG_LEVEL=DEBUG for details."
        )
        raise SystemExit(1)


@click.command("list", add_help_option=False, context_settings={"help_option_names": []})
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Output installed translations as JSON to stdout (for web bridge).",
)
@click.option("--help", "show_help", is_flag=True, help="Show this message and exit.")
def list_installed(show_help: bool, as_json: bool) -> None:
    """List installed translations."""
    if show_help:
        console.print(SEED_LIST_HELP)
        return

    service = _get_seed_service()
    installed = service.list_installed()
    if as_json:
        payload = [
            {
                "id": t["id"],
                "name": t["name"],
                "language": t["language"],
                "format": t["format"],
            }
            for t in installed
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

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
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Output available translations as JSON to stdout (for web bridge).",
)
@click.option(
    "--format",
    "format_filters",
    multiple=True,
    type=click.Choice(["USFX", "OSIS", "BEBLIA", "ZEFANIA"], case_sensitive=False),
    help="Filter by XML format. Can be repeated.",
)
@click.option(
    "--language",
    "language_filters",
    multiple=True,
    type=str,
    help="Filter by language code (e.g. fi, en). Can be repeated.",
)
@click.option(
    "--query",
    "query_text",
    default=None,
    type=str,
    help="Search by ID or name (case-insensitive).",
)
@click.option(
    "--limit",
    "limit",
    type=int,
    default=50,
    show_default=True,
    help="Max number of rows to show after filtering. Use 0 to show all.",
)
@click.option(
    "--offset",
    "offset",
    type=int,
    default=0,
    show_default=True,
    help="Skip first N matches after filtering.",
)
def available(
    show_help: bool,
    as_json: bool,
    format_filters: tuple[str, ...],
    language_filters: tuple[str, ...],
    query_text: str | None,
    limit: int,
    offset: int,
) -> None:
    """List available translations from the catalog."""
    if show_help:
        console.print(SEED_AVAILABLE_HELP)
        return

    if limit < 0:
        console.print("[red]Error: --limit must be >= 0.[/red]")
        raise SystemExit(1)
    if offset < 0:
        console.print("[red]Error: --offset must be >= 0.[/red]")
        raise SystemExit(1)

    items = _load_available_catalog()

    if format_filters:
        allowed_formats = {f.upper() for f in format_filters}
        items = [t for t in items if t.get("format", "").upper() in allowed_formats]

    if language_filters:
        allowed_langs = {lang.lower() for lang in language_filters}
        items = [t for t in items if str(t.get("language", "")).lower() in allowed_langs]

    if query_text:
        q = query_text.strip().lower()
        if q:
            items = [
                t
                for t in items
                if q in str(t.get("id", "")).lower() or q in str(t.get("name", "")).lower()
            ]

    total_matches = len(items)
    if offset:
        items = items[offset:]

    if limit == 0:
        items_to_show = items
    else:
        items_to_show = items[:limit]

    if as_json:
        payload = [
            {
                "id": t["id"],
                "name": t["name"],
                "language": t["language"],
                "format": t["format"],
                "size_mb": t.get("size_mb"),
            }
            for t in items_to_show
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    table = Table(title="Available translations")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Language")
    table.add_column("Format")
    table.add_column("Size (MB)")
    if total_matches != len(items_to_show):
        console.print(
            f"[dim]Showing {len(items_to_show)}/{total_matches} translations "
            f"(offset={offset}, limit={limit}).[/dim]"
        )

    for t in items_to_show:
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
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
    except requests.exceptions.ConnectionError:
        console.print(
            "[red]Error:[/red] Could not connect to GitHub. Check your internet connection."
        )
        raise SystemExit(1)
    except requests.exceptions.Timeout:
        console.print("[red]Error:[/red] Request timed out after all retries. Try again later.")
        raise SystemExit(1)
    except requests.exceptions.RequestException as e:
        log.warning("seed.sync_catalog.http_error", error=str(e))
        console.print(f"[red]Error:[/red] Catalog sync failed: {e}")
        raise SystemExit(1)
    except Exception:
        log.exception("seed.sync_catalog.unexpected")
        console.print(
            "[red]Error:[/red] An unexpected error occurred. "
            "Set CLIBLE_LOG_LEVEL=DEBUG for details."
        )
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
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
