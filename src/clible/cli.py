"""CLI entry point for clible."""

import click

from clible.commands.seed import (
    available,
    install,
    list_installed,
    remove,
)
from clible.commands.verse import verse


@click.group()
def main() -> None:
    """clible — Bible study tool for the command line.

    Manage translations, search verses, and export to files.
    """
    pass


@main.group("seed")
def seed() -> None:
    """Manage Bible translations (install, list, remove)."""
    pass


seed.add_command(install)
seed.add_command(list_installed, "list")
seed.add_command(available)
seed.add_command(remove)

main.add_command(verse)
