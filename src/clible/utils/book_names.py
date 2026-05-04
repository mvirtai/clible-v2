"""Localized Bible book names and resolving user input (EN/FI aliases)."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path


def _data_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "book_names.json"


@lru_cache(maxsize=1)
def _book_names_data() -> dict[str, dict[str, object]]:
    """Load book_names.json (cached)."""
    path = _data_path()
    with path.open(encoding="utf-8") as f:
        raw: object = json.load(f)
    if not isinstance(raw, dict):
        return {}
    out: dict[str, dict[str, object]] = {}
    for bid, meta in raw.items():
        if isinstance(bid, str) and isinstance(meta, dict):
            out[bid] = meta
    return out


def _normalize_for_match(s: str) -> str:
    """Lowercase, collapse whitespace, strip trailing punctuation noise."""
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _fi_match_strings(meta: dict[str, object]) -> list[str]:
    """Collect user-facing FI / EN tokens used for resolving a typed book name."""
    out: list[str] = []
    for key in ("en", "fi", "abbr_fi"):
        v = meta.get(key)
        if isinstance(v, str) and v.strip():
            out.append(v)
    aliases = meta.get("aliases_fi")
    if isinstance(aliases, list):
        for a in aliases:
            if isinstance(a, str) and a.strip():
                out.append(a)
    return out


def get_display_name(book_id: str, language: str = "en") -> str:
    """Return the display name for a book ID in the given UI language.

    Args:
        book_id: Canonical book code (e.g. LUK).
        language: ``en`` or ``fi`` (other values fall back to English).

    Returns:
        Localized name, or ``book_id`` if unknown.
    """
    meta = _book_names_data().get(book_id)
    if not meta:
        return book_id
    lang = language.lower() if language else "en"
    if lang == "fi":
        fi = meta.get("fi")
        if isinstance(fi, str) and fi:
            return fi
    en = meta.get("en")
    if isinstance(en, str) and en:
        return en
    return book_id


def get_fi_abbrev(book_id: str) -> str | None:
    """Return the Finnish citation-style abbreviation for ``book_id``, if defined."""
    meta = _book_names_data().get(book_id)
    if not meta:
        return None
    ab = meta.get("abbr_fi")
    if isinstance(ab, str) and ab.strip():
        return ab.strip()
    return None


def resolve_book_id(name: str) -> str | None:
    """Resolve a user-typed book name or alias to a canonical book ID.

    Matches English names, Finnish names, ``abbr_fi``, Finnish aliases, and book IDs
    (case-insensitive). Uses normalized equality and prefix matching on
    normalized strings so partial names work when unambiguous.

    Args:
        name: Book token from a reference (e.g. ``Luukas``, ``Luke``, ``luuk``).

    Returns:
        Book ID (e.g. LUK) or None if no match.
    """
    raw = name.strip()
    if not raw:
        return None

    data = _book_names_data()
    if not data:
        return None

    key = _normalize_for_match(raw)
    if not key:
        return None

    # Exact ID match
    for bid in data:
        if _normalize_for_match(bid) == key:
            return bid

    candidates: set[str] = set()

    for bid, meta in data.items():
        for label in _fi_match_strings(meta):
            if _normalize_for_match(label) == key:
                candidates.add(bid)
                break

    if len(candidates) == 1:
        return next(iter(candidates))

    prefix_hits: set[str] = set()
    for bid, meta in data.items():
        labels = [_normalize_for_match(lab) for lab in _fi_match_strings(meta)]
        labels = [lab for lab in labels if lab]
        if any(lab.startswith(key) for lab in labels):
            prefix_hits.add(bid)

    if len(prefix_hits) == 1:
        return next(iter(prefix_hits))

    return None
