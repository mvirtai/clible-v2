"""Structured logging configuration for clible.

Configured once at CLI startup via configure_logging().
Other modules call structlog.get_logger(__name__) and are unaware of the renderer.
"""

import logging
import sys

import structlog


def configure_logging(level: str = "WARNING", fmt: str = "console") -> None:
    """Configure structlog for the application.

    Call this once at startup before any log calls are made.

    Args:
        level: Minimum log level (DEBUG / INFO / WARNING / ERROR). Case-insensitive.
               Calls below this level are no-ops - no string formatting, no I/O.

        fmt:   Output format. "console" gives colored human-readable output (dev).
               "json" gives machine-parseable JSON lines (production)
    """
    # Convert level string to an integer (e.g. "WARNING" -> 30)
    # logging.WARNING, logging.DEBUG etc. are just integers in stdlib.
    log_level = getattr(logging, level.upper(), logging.WARNING)

    # Choose the renderer based on format.
    # ConsoleRenderer: colorful, human-readable, goes to stderr.
    # JSONRenderer: machine-parseable JSON lines, goes to stdout.
    if fmt == "json":
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        # Processors run in order on every log event.
        # The list is a pipeline: each step adds information to the event dict.
        processors=[
            structlog.processors.add_log_level,  # "level": "warning"
            structlog.processors.TimeStamper(fmt="iso"),  # "timestamp"
            structlog.processors.StackInfoRenderer(),  # renders stack_info if present
            structlog.processors.format_exc_info,  # populate exception for renderers
            structlog.processors.ExceptionRenderer(),
            renderer,  # must be last: event dict -> string to stderr
        ],
        # make_filtering_bound_logger(level) returns a BoundLogger class that
        # short-circuits calls below `level` before doing any work.
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        # PrintLoggerFactory writes to a file object — here stderr.
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        # cache_logger_on_first_use: after the first get_logger() call in a module,
        # structlog caches the bound logger so subsequent calls are O(1) dict lookups.
        cache_logger_on_first_use=True,
    )
