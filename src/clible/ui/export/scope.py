"""Scope labels and book-name helpers for export titles."""

from __future__ import annotations

import json
import re
from pathlib import Path

from clible.config import get_config
from clible.utils.book_names import get_display_name, resolve_book_id

_BOOK_NAMES_CACHE: dict[str, str] | None = None


def _load_book_names() -> dict[str, str]:
    """Load book ID -> name mapping from bible_structure.json."""
    global _BOOK_NAMES_CACHE
    if _BOOK_NAMES_CACHE is not None:
        return _BOOK_NAMES_CACHE
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    structure_path = data_dir / "bible_structure.json"
    with structure_path.open(encoding="utf-8") as f:
        structure = json.load(f)
    _BOOK_NAMES_CACHE = {book["id"]: book["name"] for book in structure.get("books", [])}
    return _BOOK_NAMES_CACHE


def parse_and_format_scope(scope_label: str) -> tuple[str, str]:
    """Try to parse scope_label and return (full_title, acronym).

    If scope_label looks like a verse reference, try to expand book name.
    Handles EN/FI names, aliases, book IDs (e.g. JHN 3:16), and English structure names.

    Returns:
        Tuple of (full_title, acronym_ref).
    """
    pattern = r"^(.+?)\s+(\d+):(\d+(?:-\d+)?)$"
    match = re.match(pattern, scope_label.strip())
    if not match:
        return scope_label, ""

    book_part, chapter, verse_range = match.groups()
    lang = (get_config().ui_language or "en").lower()
    bid = resolve_book_id(book_part.strip())
    if bid:
        book_name = get_display_name(bid, lang)
        acronym = f"({bid} {chapter}:{verse_range})"
        full_title = f"{book_name} {chapter}:{verse_range}"
        return full_title, acronym

    book_names = _load_book_names()
    if book_part in book_names:
        book_id = book_part
        book_name = get_display_name(book_id, lang)
        acronym = f"({book_id} {chapter}:{verse_range})"
    else:
        book_id = None
        for b_id, bname in book_names.items():
            if bname.lower() == book_part.lower():
                book_id = b_id
                break
        if book_id:
            acronym = f"({book_id} {chapter}:{verse_range})"
            book_name = get_display_name(book_id, lang)
        else:
            return scope_label, ""

    full_title = f"{book_name} {chapter}:{verse_range}"
    return full_title, acronym
