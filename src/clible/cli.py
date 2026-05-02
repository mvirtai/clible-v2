"""CLI entry point for clible."""

import os

import click

from clible.commands.analytics import book as analytics_book
from clible.commands.analytics import chapter as analytics_chapter
from clible.commands.analytics import compare as analytics_compare
from clible.commands.analytics import reference as analytics_reference
from clible.commands.backup import backup
from clible.commands.saved import saved
from clible.commands.scope import scope
from clible.commands.search import search
from clible.commands.seed import (
    available,
    install,
    list_installed,
    remove,
    sync_catalog,
)
from clible.commands.verse import verse
from clible.logging_config import configure_logging
from clible.ui.help_texts import CLI_ROOT_HELP


@click.group(help=CLI_ROOT_HELP)
def main() -> None:
    """Entry point for the clible CLI (see CLI_ROOT_HELP for `clible --help` text)."""
    configure_logging(
        level=os.environ.get("CLIBLE_LOG_LEVEL", "WARNING"),
        fmt=os.environ.get("CLIBLE_LOG_FORMAT", "console"),
    )


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
seed.add_command(sync_catalog)
seed.add_command(remove)

analytics.add_command(analytics_reference, "reference")
analytics.add_command(analytics_chapter, "chapter")
analytics.add_command(analytics_book, "book")
analytics.add_command(analytics_compare, "compare")

main.add_command(verse)
main.add_command(search)
main.add_command(backup)
main.add_command(scope)
main.add_command(saved)
