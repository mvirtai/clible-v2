"""Shared Rich Console instance for CLI output.

Import this single instance in command modules instead of creating
a new Console() in each. Rich recommends one shared instance so that
terminal capabilities, encoding, and color handling stay consistent.
"""

from rich.console import Console

console = Console()
