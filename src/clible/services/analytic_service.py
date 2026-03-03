"""Service layer for text analytic services like word frequency, concordance, etc."""

from clible.services.verse_service import VerseService


class AnalyticService:
    def __init__(self, verse_service: VerseService):
        """Initialize with injected VerseService."""
        self._verse_service = verse_service

    def word_freq(
        self, reference: str, translation_id: str | None = None
    ) -> dict[str, int]:
        """Calculate word frequency for verses in the given reference.

        Args:
            reference: Bible reference string ("John 3:16" or "John 3:16-18")
            translation_id: Translation ID to use. If None, uses the default installed.

        Returns:
            Dictionary mapping words (lowercase, stripped of punctuation) to their frequency count.

        Raises:
            Exception: Propagates any error encountered while fetching or analyzing verses.

        Note:
            This method will raise exceptions for the caller to handle.
            If no verses are found, returns an empty dictionary.
        """
        if not reference or not reference.strip():
            raise ValueError("Reference cannot be empty.")
        # translation_id can be None (for default), so only validate if provided
        if translation_id is not None and not translation_id.strip():
            raise ValueError("Translation ID cannot be empty string.")

        verses = self._verse_service.get_verses(reference, translation_id)
        if not verses:
            return {}

        freq: dict[str, int] = {}
        for verse in verses:
            # Basic tokenization: split on whitespace, strip some punctuation, lowercase
            words = verse["text"].split()
            for word in words:
                word = word.strip(',.?!;:"()').lower()
                if word:
                    freq[word] = freq.get(word, 0) + 1
        return freq
