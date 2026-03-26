"""
Analytics export helpers.

This package converts analytics result dictionaries into a user-selected file
format. It performs no database access and no network calls.

Implementation lives in ``clible.ui.export``; this module re-exports the public
API for stable import paths (e.g. ``from clible.ui.analytics_export import …``).
"""

from __future__ import annotations

from clible.ui.export import (
    SUPPORTED_EXPORT_FORMATS,
    detect_format,
    export_analysis,
    export_compare,
    render_html_document,
    resolve_output_path,
    validate_export_format,
    write_text,
)

__all__ = [
    "SUPPORTED_EXPORT_FORMATS",
    "detect_format",
    "export_analysis",
    "export_compare",
    "render_html_document",
    "resolve_output_path",
    "validate_export_format",
    "write_text",
]
