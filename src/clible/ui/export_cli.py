"""Unified export parameter: parse PATH, FILENAME, and FORMAT from a single string."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import click

from clible.ui.export import SUPPORTED_EXPORT_FORMATS


@dataclass
class ExportConfig:
    """Parsed export configuration with defaults applied."""

    path: Path
    filename: str
    format: str

    def resolve(self) -> Path:
        """Build the full output path with format extension."""
        stem = self.filename
        if "." in stem:
            stem = stem.rsplit(".", 1)[0]
        return self.path / f"{stem}.{self.format}"


def parse_export_string(
    value: str,
    *,
    default_path: str | None = None,
    default_filename: str | None = None,
    default_format: str = "md",
) -> ExportConfig:
    """Parse export parameter string into PATH, FILENAME, FORMAT.

    Accepts comma- or space-separated key=value pairs (case-insensitive keys).
    Missing keys fall back to defaults. Unknown keys raise ValueError.

    Examples:
        "PATH=~/exports,FILENAME=john316,FORMAT=json"
        "path=. filename=result format=html"
        "PATH=. FORMAT=csv"

    Args:
        value: User-provided export string.
        default_path: Default directory (current dir if None).
        default_filename: Default stem (timestamp-based if None).
        default_format: Default format (md if not specified).

    Returns:
        Parsed ExportConfig with all fields resolved.

    Raises:
        ValueError: If format is unsupported or key is unknown.
    """
    defaults = {
        "path": default_path or ".",
        "filename": default_filename or f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "format": default_format,
    }

    pairs = re.split(r"[,\s]+", value.strip())
    parsed: dict[str, str] = {}

    for pair in pairs:
        if not pair or "=" not in pair:
            continue
        key, val = pair.split("=", 1)
        key_lower = key.strip().lower()
        if key_lower not in {"path", "filename", "format"}:
            raise ValueError(
                f"Unknown export key: '{key}'. Use PATH, FILENAME, or FORMAT (case-insensitive)."
            )
        parsed[key_lower] = val.strip()

    resolved_format = parsed.get("format", defaults["format"]).lower()
    if resolved_format not in SUPPORTED_EXPORT_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_EXPORT_FORMATS))
        raise ValueError(f"Unsupported FORMAT '{resolved_format}'. Use one of: {supported}.")

    return ExportConfig(
        path=Path(parsed.get("path", defaults["path"])).expanduser(),
        filename=parsed.get("filename", defaults["filename"]),
        format=resolved_format,
    )


class ExportParamType(click.ParamType):
    """Click parameter type for unified --export string."""

    name = "export"

    def convert(
        self,
        value: str | ExportConfig,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> ExportConfig | None:
        if value is None:
            return None
        if isinstance(value, ExportConfig):
            return value

        if not value.strip():
            self.fail(
                "Empty --export value. Use: --export 'PATH=~/out,FILENAME=myfile,FORMAT=json' "
                "(all keys optional, case-insensitive).",
                param,
                ctx,
            )

        try:
            return parse_export_string(value)
        except ValueError as e:
            self.fail(str(e), param, ctx)


EXPORT_PARAM = ExportParamType()
