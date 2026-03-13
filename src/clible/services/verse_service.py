"""Verse lookup service: resolve references and fetch from local DB."""

from collections import Counter
from typing import TYPE_CHECKING

from clible.services.reference_parser import ReferenceScope, parse_reference

if TYPE_CHECKING:
    from clible.db.repositories.book_repo import BookRepo
    from clible.db.repositories.translation_repo import TranslationRepo
    from clible.db.repositories.verse_repo import VerseRepo

# IDEA (AI): The reference parsing is currently quite strict and tied to VerseService.
# Consider creating a dedicated ReferenceParser class or utility that can handle:
# 1. "John" (Full book)
# 2. "John 3" (Full chapter)
# 3. "John 3:16" (Single verse)
# 4. "John 3:16-18" (Verse range)


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
        parsed = parse_reference(reference)
        if not parsed or parsed.scope != ReferenceScope.VERSE:
            return None

        book = self._book_repo.get_by_name(parsed.book_name)
        if not book:
            matches = self._book_repo.search(parsed.book_name)
            book = matches[0] if matches else None
        if not book:
            return None

        tid = translation_id
        if not tid:
            default = self._translation_repo.get_default()
            tid = default["id"] if default else None
        if not tid:
            return None

        return self._verse_repo.get_verse(tid, book["id"], parsed.chapter, parsed.verse_start)

    def get_verses(
        self,
        reference: str,
        translation_id: str | None = None,
    ) -> list[dict]:
        """Get verses by reference (e.g. 'John 3:16' or 'John 3:16-18').

        Args:
            reference: Bible reference like 'John 3:16', 'John 3:1-6'.
            translation_id: Translation to use. Defaults to installed default.

        Returns:
            List of verse dicts in order (one for single reference, multiple for range).
            Empty list if not found or invalid reference.
        """
        parsed = parse_reference(reference)
        if not parsed or parsed.scope != ReferenceScope.VERSE:
            return []

        book = self._book_repo.get_by_name(parsed.book_name)
        if not book:
            matches = self._book_repo.search(parsed.book_name)
            book = matches[0] if matches else None
        if not book:
            return []

        tid = translation_id
        if not tid:
            default = self._translation_repo.get_default()
            tid = default["id"] if default else None
        if not tid:
            return []

        return self._verse_repo.get_verses_in_range(
            tid, book["id"], parsed.chapter, parsed.verse_start, parsed.verse_end
        )

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
        book = self._book_repo.get_by_name(book_name)
        if not book:
            matches = self._book_repo.search(book_name)
            book = matches[0] if matches else None
        if not book:
            return []

        tid = translation_id
        if not tid:
            default = self._translation_repo.get_default()
            tid = default["id"] if default else None
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
        book = self._book_repo.get_by_name(book_name)
        if not book:
            matches = self._book_repo.search(book_name)
            book = matches[0] if matches else None
        if not book:
            return []

        tid = translation_id
        if not tid:
            default = self._translation_repo.get_default()
            tid = default["id"] if default else None
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

        Args:
            word: The word to search for (case-insensitive).
            translation_id: Optional translation ID to filter by.
                If None, searches all translations.

        Returns:
            List of verse dicts that contain the word,
            ordered by book/chapter/verse.
        """
        # IDEA (AI): Expand this to support scoping (bible, testament, book, chapter).
        # Currently, the search command handles scoping by filtering the full result set.
        # Moving that logic here (and possibly into the repository for more efficient
        # SQL filtering) would be a significant architectural improvement.
        all_verses = self._verse_repo.search_text(word, translation_id)
        return self.filter_verses_by_scope(all_verses, scope, scope_ref)

    def filter_verses_by_scope(
        self,
        verses: list[dict],
        scope: str,
        scope_value: str | None,
    ) -> list[dict]:
        """Filter verses based on scope type and value."""
        if scope == "bible" or not scope_value:
            return verses

        if scope == "testament":
            from clible.db.repositories.book_repo import Testament

            testament_str = scope_value.upper()
            testament_books = self._book_repo.get_by_testament(Testament(testament_str))
            book_ids = {b["id"] for b in testament_books}
            return [v for v in verses if v["book_id"] in book_ids]

        if scope == "book":
            book = self._book_repo.get_by_name(scope_value)
            if not book:
                matches = self._book_repo.search(scope_value)
                book = matches[0] if matches else None
            if not book:
                return []
            return [v for v in verses if v["book_id"] == book["id"]]

        if scope == "chapter":
            parsed = parse_reference(scope_value)
            if not parsed or parsed.scope not in (ReferenceScope.CHAPTER, ReferenceScope.VERSE):
                return []
            book = self._book_repo.get_by_name(parsed.book_name)
            if not book:
                matches = self._book_repo.search(parsed.book_name)
                book = matches[0] if matches else None
            if not book:
                return []
            return [
                v
                for v in verses
                if v["book_id"] == book["id"] and v["chapter"] == parsed.chapter
            ]

        if scope == "verse":
            parsed = parse_reference(scope_value)
            if not parsed or parsed.scope != ReferenceScope.VERSE:
                return []
            book = self._book_repo.get_by_name(parsed.book_name)
            if not book:
                matches = self._book_repo.search(parsed.book_name)
                book = matches[0] if matches else None
            if not book:
                return []
            return [
                v
                for v in verses
                if v["book_id"] == book["id"]
                and v["chapter"] == parsed.chapter
                and parsed.verse_start <= v["verse"] <= parsed.verse_end
            ]

        return verses

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
