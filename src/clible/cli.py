"""CLI entry point for clible."""

import click

from clible.commands.analytics import book as analytics_book
from clible.commands.analytics import chapter as analytics_chapter
from clible.commands.analytics import reference as analytics_reference
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

    Manage translations, search verses, analyze text, and export to files.
    """
    pass


@main.group("seed")
def seed() -> None:
    """Manage Bible translations (install, list, remove)."""
    pass


@main.group("analytics")
def analytics() -> None:
    """Text analysis: word frequency, n-grams, and statistics."""
    pass


seed.add_command(install)
seed.add_command(list_installed, "list")
seed.add_command(available)
seed.add_command(remove)

analytics.add_command(analytics_reference, "reference")
analytics.add_command(analytics_chapter, "chapter")
analytics.add_command(analytics_book, "book")

main.add_command(verse)
