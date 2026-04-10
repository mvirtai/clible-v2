import click
from rich.table import Table

from clible.commands import get_scope_service
from clible.ui.console import console


@click.group()
def scope():
    """Manage research scopes (contexts for saved work)."""
    pass


@scope.command("list")
def list_scopes():
    """List all available research scopes."""
    service = get_scope_service()
    scopes = service.list_scopes()

    if not scopes:
        console.print("[dim]No scopes found.[/dim]")
        return

    table = Table(title="Research Scopes")
    table.add_column("Name", style="cyan")
    table.add_column("Created At", style="dim")

    for s in scopes:
        # Highlight current scope if possible
        # (For now we just list them all)
        table.add_row(s["name"], s["created_at"])

    console.print(table)
