"""Export format identifiers shared across CLI and serializers."""

from __future__ import annotations

SUPPORTED_EXPORT_FORMATS: frozenset[str] = frozenset({"json", "csv", "html", "md", "txt", "xml"})
_SUPPORTED_FORMATS: set[str] = set(SUPPORTED_EXPORT_FORMATS)
