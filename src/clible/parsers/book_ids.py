"""Canonical book ID ordering shared by number-based parsers (Beblia, Zefania)."""

import json
from functools import cache
from pathlib import Path


@cache
def ordered_book_ids() -> tuple[str, ...]:
    """Return clible book IDs in canonical order (position 1-66).

    Uses functools.cache so the JSON file is read at most once per process,
    and only when a parser actually needs the mapping.
    """
    path = Path(__file__).resolve().parent.parent / "data" / "bible_structure.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    books = sorted(data["books"], key=lambda b: b["position"])
    return tuple(b["id"] for b in books)
