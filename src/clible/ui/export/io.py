"""Output path resolution and UTF-8 file writes for exports."""

from __future__ import annotations

from pathlib import Path

from clible.ui.export.constants import _SUPPORTED_FORMATS


def detect_format(output_path: Path) -> str:
    """Detect output format by file extension.

    Args:
        output_path: Output file path. Format is inferred from the extension.

    Returns:
        A lower-case format string: one of the supported export formats.

    Raises:
        ValueError: If the extension is missing or unsupported.
    """
    suffix = output_path.suffix.lower().lstrip(".")
    if suffix == "htm":
        return "html"
    if not suffix:
        raise ValueError(
            "Missing file extension for --output. "
            "Add an extension or use --export with a path (extension optional)."
        )
    if suffix not in _SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported --output format '.{suffix}'. Use one of: "
            + ", ".join(sorted(_SUPPORTED_FORMATS))
            + "."
        )
    return suffix


def validate_export_format(format_name: str) -> str:
    """Return normalized format name or raise ValueError."""
    fmt = format_name.lower().strip()
    if fmt == "htm":
        fmt = "html"
    if fmt not in _SUPPORTED_FORMATS:
        supported = ", ".join(sorted(_SUPPORTED_FORMATS))
        raise ValueError(f"Unsupported format '{format_name}'. Use one of: {supported}.")
    return fmt


def resolve_output_path(output_path: str, export_format: str | None) -> tuple[Path, str]:
    """Resolve destination path and format from CLI arguments.

    If ``export_format`` is set, it selects the serializer and normalizes the
    file suffix. If only ``output_path`` is set, the format is inferred from
    the extension (``.htm`` maps to ``html``).

    Args:
        output_path: User-provided output path.
        export_format: Optional explicit format from ``--export`` / ``-exp``.

    Returns:
        Tuple of ``(path, format)``.

    Raises:
        ValueError: If the path or format cannot be resolved.
    """
    path = Path(output_path)
    if export_format is not None:
        fmt = validate_export_format(export_format)
        path = path.with_suffix(f".{fmt}")
        return path, fmt
    return path, detect_format(path)


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text to the given file path.

    Args:
        path: Output file path.
        content: Text content to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
