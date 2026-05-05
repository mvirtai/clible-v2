"""Tests for structured logging setup."""

import logging

import structlog

from clible.logging_config import configure_logging


def test_configure_logging_uses_json_renderer_for_json_format():
    configure_logging(level="info", fmt="json")
    cfg = structlog.get_config()
    assert cfg["wrapper_class"] is structlog.make_filtering_bound_logger(logging.INFO)
    assert cfg["processors"][-1].__class__.__name__ == "JSONRenderer"


def test_configure_logging_defaults_to_console_for_unknown_format():
    configure_logging(level="warning", fmt="anything")
    cfg = structlog.get_config()
    assert cfg["processors"][-1].__class__.__name__ == "ConsoleRenderer"


def test_configure_logging_falls_back_to_warning_for_unknown_level():
    configure_logging(level="notalevel", fmt="json")
    cfg = structlog.get_config()
    assert cfg["wrapper_class"] is structlog.make_filtering_bound_logger(logging.WARNING)
