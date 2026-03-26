"""Shared serialization helpers for export modules."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

_BOOK_NAMES_CACHE: dict[str, str] | None = None


def stringify_number(value: Any) -> str:
    if isinstance(value, float):
        # Keep deterministic precision for tests/users; avoid long binary floats.
        return f"{value:.6f}".rstrip("0").rstrip(".") if value != int(value) else str(int(value))
    return str(value)


def load_book_names() -> dict[str, str]:
    """Load book ID -> name mapping from bible_structure.json (cached)."""
    global _BOOK_NAMES_CACHE
    if _BOOK_NAMES_CACHE is not None:
        return _BOOK_NAMES_CACHE

    data_dir = Path(__file__).resolve().parents[2] / "data"
    structure_path = data_dir / "bible_structure.json"
    with structure_path.open("r", encoding="utf-8") as f:
        structure = json.load(f)

    _BOOK_NAMES_CACHE = {book["id"]: book["name"] for book in structure.get("books", [])}
    return _BOOK_NAMES_CACHE


def format_title_with_acronym(book_id: str, chapter: int, verse: int) -> tuple[str, str]:
    """Build full title and acronym reference for a single verse."""
    book_name = load_book_names().get(book_id, book_id)
    full_title = f"{book_name} {chapter}:{verse}"
    acronym = f"({book_id} {chapter}:{verse})"
    return full_title, acronym


def full_verse_ref(v: dict[str, Any]) -> tuple[str, str]:
    """Return (full_ref, acronym_ref) for a verse dict."""
    book_id = str(v.get("book_id", ""))
    chapter = int(v.get("chapter", 0) or 0)
    verse = int(v.get("verse", 0) or 0)
    return format_title_with_acronym(book_id, chapter, verse)


def xml_document(root: ET.Element) -> str:
    ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + body
