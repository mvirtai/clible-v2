"""Verse lookup service: resolve references and fetch from local DB."""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clible.db.repositories.book_repo import BookRepo
    from clible.db.repositories.translation_repo import TranslationRepo
    from clible.db.repositories.verse_repo import VerseRepo

# Matches "Book 1:2" or "Book 1:2-3" (we use first verse only for now)
_REFERENCE_PATTERN = re.compile(
    r"^\s*(.+?)\s+(\d+):(\d+)(?:-\d+)?\s*$",
    re.IGNORECASE,
)


def _parse_reference(reference: str) -> tuple[str, int, int] | None:
    """Parse 'John 3:16' -> (book_name, chapter, verse). Returns None if invalid."""
    m = _REFERENCE_PATTERN.match(reference.strip())
    if not m:
        return None
    return (m.group(1).strip(), int(m.group(2)), int(m.group(3)))


class VerseService:
    """Look up verses from the local database by reference."""

    def __init__(
        self,
        verse_repo: "VerseRepo",
        book_repo: "BookRepo",
        translation_repo: "TranslationRepo",
    ):
        """Initialize with injected repositories."""
        self._verse_repo = verse_repo
        self._book_repo = book_repo
        self._translation_repo = translation_repo

    def get_verse(
        self,
        reference: str,
        translation_id: str | None = None,
    ) -> dict | None:
        """Get a verse by reference (e.g. 'John 3:16').

        Args:
            reference: Bible reference like 'John 3:16', 'Genesis 1:1'.
            translation_id: Translation to use. Defaults to installed default (e.g. web).

        Returns:
            Verse dict with id, text, book_id, chapter, verse, etc. None if not found.
        """
        parsed = _parse_reference(reference)
        if not parsed:
            return None

        book_name, chapter, verse = parsed
        book = self._book_repo.get_by_name(book_name) or (
            self._book_repo.search(book_name)[0] if self._book_repo.search(book_name) else None
        )
        if not book:
            return None

        tid = translation_id
        if not tid:
            default = self._translation_repo.get_default()
            tid = default["id"] if default else None
        if not tid:
            return None

        return self._verse_repo.get_verse(tid, book["id"], chapter, verse)
