"""Export serializers, HTML shell, and output helpers (UI layer; no DB access)."""

from __future__ import annotations

from clible.ui.export.analysis import export_analysis
from clible.ui.export.compare import export_compare
from clible.ui.export.constants import SUPPORTED_EXPORT_FORMATS
from clible.ui.export.html_document import render_html_document
from clible.ui.export.io import (
    detect_format,
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
