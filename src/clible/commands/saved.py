import json

import click
from rich.table import Table

from clible.commands.analytics import (
    display_translation_label,
    render_analysis,
    render_comparison,
)
from clible.commands.search import display_scope_label, display_verses, render_statistics
from clible.ui.console import console

from . import (
    get_saved_analysis_service,
    get_saved_search_service,
    get_verse_service,
)


@click.group()
def saved():
    """Manage saved searches and analyses."""
    pass


@saved.group("search")
def search_group():
    """Manage saved searches."""
    pass


@saved.group("analysis")
def analysis_group():
    """Manage saved analyses."""
    pass


# Saved Search Commands


@search_group.command("list")
def list_searches():
    """List all saved searches in the current scope."""
    service = get_saved_search_service()
    items = service.list_saved_searches()

    if not items:
        console.print("[dim]No saved searches in current scope.[/dim]")
        return

    table = Table(title="Saved Searches")
    table.add_column("Name", style="cyan")
    table.add_column("Query", style="green")
    table.add_column("Scope", style="dim")
    table.add_column("Created At", style="dim")

    for item in items:
        scope_str = f"{item['search_scope']}"
        if item["scope_value"]:
            scope_str += f" ({item['scope_value']})"
        table.add_row(item["name"], item["query_text"], scope_str, item["created_at"])

    console.print(table)


@search_group.command("run")
@click.argument("identifier")
def run_search(identifier):
    """Re-run a saved search by name or ID."""
    service = get_saved_search_service()
    try:
        meta, verses = service.get_and_run(identifier)

        scope_label = display_scope_label(meta["search_scope"], meta["scope_value"])
        stats = get_verse_service().get_search_statistics(verses, meta["query_text"])

        render_statistics(stats, meta["query_text"], scope_label)
        display_verses(verses, meta["query_text"])
    except ValueError as e:
        console.print(f"[red]{e}[/red]")


@search_group.command("delete")
@click.argument("identifier")
def delete_search(identifier):
    """Delete a saved search by name or ID."""
    service = get_saved_search_service()
    if service.delete_saved_search(identifier):
        console.print(f"[green]Deleted saved search '{identifier}'.[/green]")
    else:
        console.print(f"[red]Could not find saved search '{identifier}'.[/red]")


# Saved Analysis Commands


@analysis_group.command("list")
def list_analyses():
    """List all saved analyses in the current scope."""
    service = get_saved_analysis_service()
    items = service.list_saved_analyses()

    if not items:
        console.print("[dim]No saved analyses in current scope.[/dim]")
        return

    table = Table(title="Saved Analyses")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Reference", style="dim")
    table.add_column("Created At", style="dim")

    for item in items:
        table.add_row(item["name"], item["analysis_type"], item["reference"], item["created_at"])

    console.print(table)


@analysis_group.command("run")
@click.argument("identifier")
def run_analysis(identifier):
    """Re-run a saved analysis by name or ID."""
    service = get_saved_analysis_service()
    try:
        meta, result = service.get_and_run(identifier)

        if meta["analysis_type"] == "compare":
            params = json.loads(meta["params_json"]) if meta["params_json"] else {}
            # Fallback to translation_id if resolved name info is lost
            left_label = display_translation_label(
                meta["translation_id"], meta["translation_id"] or "original"
            )
            right_label = display_translation_label(
                params.get("translation_b", "unknown"), params.get("translation_b", "unknown")
            )
            render_comparison(console, result, left_label, right_label)
        else:
            render_analysis(console, result, meta["reference"])
    except ValueError as e:
        console.print(f"[red]{e}[/red]")


@analysis_group.command("delete")
@click.argument("identifier")
def delete_analysis(identifier):
    """Delete a saved analysis by name or ID."""
    service = get_saved_analysis_service()
    if service.delete_saved_analysis(identifier):
        console.print(f"[green]Deleted saved analysis '{identifier}'.[/green]")
    else:
        console.print(f"[red]Could not find saved analysis '{identifier}'.[/red]")
