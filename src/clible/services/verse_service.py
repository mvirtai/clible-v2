"""Verse lookup service: resolve references and fetch from local DB."""

from collections import Counter
from typing import TYPE_CHECKING

from clible.services.reference_parser import ReferenceScope, parse_reference

if TYPE_CHECKING:
    from clible.db.repositories.book_repo import BookRepo
    from clible.db.repositories.translation_repo import TranslationRepo
    from clible.db.repositories.verse_repo import VerseRepo


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

    def _resolve_book(self, name: str) -> dict | None:
        """Look up a book by exact name, falling back to fuzzy search."""
        book = self._book_repo.get_by_name(name)
        if not book:
            matches = self._book_repo.search(name)
            book = matches[0] if matches else None
        return book

    def _resolve_translation_id(self, translation_id: str | None) -> str | None:
        """Return the given ID, or fall back to the installed default."""
        if translation_id:
            return translation_id
        default = self._translation_repo.get_default()
        return default["id"] if default else None

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
        parsed = parse_reference(reference)
        if not parsed or parsed.scope != ReferenceScope.VERSE:
            return None

        book = self._resolve_book(parsed.book_name)
        if not book:
            return None

        tid = self._resolve_translation_id(translation_id)
        if not tid:
            return None

        return self._verse_repo.get_verse(tid, book["id"], parsed.chapter, parsed.verse_start)

    def get_verses(
        self,
        reference: str,
        translation_id: str | None = None,
    ) -> list[dict]:
        """Get verses by reference.

        Supports verse or range (``John 3:16``, ``John 3:1-6``), a chapter
        (``John 3``), or a whole book (``John``).

        Args:
            reference: Bible reference string.
            translation_id: Translation to use. Defaults to installed default.

        Returns:
            Verse dicts in canonical order. Empty list if not found or invalid.
        """
        parsed = parse_reference(reference)
        if not parsed:
            return []

        tid = self._resolve_translation_id(translation_id)
        if not tid:
            return []

        if parsed.scope == ReferenceScope.VERSE:
            if parsed.chapter is None or parsed.verse_start is None or parsed.verse_end is None:
                return []
            book = self._resolve_book(parsed.book_name)
            if not book:
                return []
            return self._verse_repo.get_verses_in_range(
                tid, book["id"], parsed.chapter, parsed.verse_start, parsed.verse_end
            )

        if parsed.scope == ReferenceScope.CHAPTER:
            if parsed.chapter is None:
                return []
            return self.get_chapter_verses(parsed.book_name, parsed.chapter, translation_id)

        if parsed.scope == ReferenceScope.BOOK:
            return self.get_book_verses(parsed.book_name, translation_id)

        return []

    def get_chapter_verses(
        self,
        book_name: str,
        chapter: int,
        translation_id: str | None = None,
    ) -> list[dict]:
        """Get all verses in a chapter.

        Args:
            book_name: Book name (e.g. "John", "Genesis").
            chapter: Chapter number.
            translation_id: Translation to use. Defaults to installed default.

        Returns:
            List of verse dicts in the chapter, ordered by verse number.
            Empty list if book not found or no verses in chapter.
        """
        book = self._resolve_book(book_name)
        if not book:
            return []

        tid = self._resolve_translation_id(translation_id)
        if not tid:
            return []

        return self._verse_repo.get_verses(tid, book["id"], chapter)

    def get_book_verses(
        self,
        book_name: str,
        translation_id: str | None = None,
    ) -> list[dict]:
        """Get all verses in a book.

        Args:
            book_name: Book name (e.g. "John", "Genesis").
            translation_id: Translation to use. Defaults to installed default.

        Returns:
            List of all verse dicts in the book, ordered by chapter then verse.
            Empty list if book not found or no verses in book.
        """
        book = self._resolve_book(book_name)
        if not book:
            return []

        tid = self._resolve_translation_id(translation_id)
        if not tid:
            return []

        return self._verse_repo.get_book_verses(tid, book["id"])

    def search_text(
        self,
        word: str,
        translation_id: str | None = None,
        scope: str = "bible",
        scope_ref: str | None = None,
    ) -> list[dict]:
        """Search for verses containing the given word using FTS5 index.

        Scope filters are applied in SQL via ``VerseRepo.search_text``.

        Args:
            word: The word to search for (case-insensitive).
            translation_id: Optional translation ID to filter by.
                If None, searches all translations.

        Returns:
            List of verse dicts that contain the word,
            ordered by book/chapter/verse.
        """
        kwargs = self._search_scope_repo_kwargs(scope, scope_ref)
        if kwargs is None:
            return []
        return self._verse_repo.search_text(word, translation_id, **kwargs)

    def _search_scope_repo_kwargs(self, scope: str, scope_ref: str | None) -> dict | None:
        """Build keyword args for ``VerseRepo.search_text``. None means invalid scope."""
        if scope == "bible" or not scope_ref:
            return {}

        if scope == "testament":
            from clible.db.repositories.book_repo import Testament

            testament_str = scope_ref.upper()
            testament_books = self._book_repo.get_by_testament(Testament(testament_str))
            book_ids = tuple(b["id"] for b in testament_books)
            if not book_ids:
                return None
            return {"book_ids": book_ids}

        if scope == "book":
            book = self._resolve_book(scope_ref)
            if not book:
                return None
            return {"book_id": book["id"]}

        if scope == "chapter":
            parsed = parse_reference(scope_ref)
            if not parsed or parsed.scope not in (ReferenceScope.CHAPTER, ReferenceScope.VERSE):
                return None
            if parsed.chapter is None:
                return None
            book = self._resolve_book(parsed.book_name)
            if not book:
                return None
            return {"book_id": book["id"], "chapter": parsed.chapter}

        if scope == "verse":
            parsed = parse_reference(scope_ref)
            if not parsed or parsed.scope != ReferenceScope.VERSE:
                return None
            if parsed.chapter is None or parsed.verse_start is None or parsed.verse_end is None:
                return None
            book = self._resolve_book(parsed.book_name)
            if not book:
                return None
            return {
                "book_id": book["id"],
                "chapter": parsed.chapter,
                "verse_min": parsed.verse_start,
                "verse_max": parsed.verse_end,
            }

        return {}

    def get_search_statistics(self, verses: list[dict], word: str) -> dict:
        """Build search statistics from matching verses."""
        total_occurrences = 0
        book_counter: Counter[str] = Counter()

        for v in verses:
            text_lower = v["text"].lower()
            word_lower = word.lower()
            count_in_verse = text_lower.count(word_lower)
            total_occurrences += count_in_verse
            book_counter[v["book_id"]] += count_in_verse

        return {
            "total_occurrences": total_occurrences,
            "unique_verses": len(verses),
            "books_with_matches": len(book_counter),
            "top_books": book_counter.most_common(5),
        }
