"""Service layer for text analytics: word frequency, n-grams, concordance, comparison."""

import json
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from clible.services.verse_service import VerseService


class AnalyticService:
    """Text analytics for Bible verses: tokens, frequencies, n-grams, concordance."""

    def __init__(
        self,
        verse_service: VerseService,
        filter_stopwords: bool = True,
        language: str = "en",
    ):
        """Initialize with injected VerseService.

        Args:
            verse_service: VerseService instance for fetching verses.
            filter_stopwords: If True, filters stopwords for the given language.
            language: Language code to select stopword list (e.g. "en", "fin").
                Defaults to "en". Ignored when filter_stopwords is False.
        """
        self._verse_service = verse_service
        self._filter_stopwords = filter_stopwords
        self._stopwords = self._load_stopwords(language) if filter_stopwords else set()

    def _load_stopwords(self, language: str) -> set[str]:
        """Load stopwords for the given language from the shared stopwords file.

        Args:
            language: Language code matching a key in stopwords.json (e.g. "en", "fin").

        Returns:
            Set of lowercase stopwords. Empty set if language not found or file missing.
        """
        data_dir = Path(__file__).parent.parent / "data"
        stopwords_file = data_dir / "stopwords.json"

        if not stopwords_file.exists():
            return set()

        with open(stopwords_file, encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get(language, {}).get("words", []))

    # TODO: regex tokenizer to handle apostrophes (don't) and hyphens properly
    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into normalized words.

        Tokenization rules:
        - Split on whitespace
        - Strip common punctuation: ,.?!;:"()[]{}
        - Convert to lowercase
        - Filter stopwords (if enabled)
        - Filter empty strings

        Args:
            text: Raw text to tokenize.

        Returns:
            List of normalized tokens (stopwords filtered if enabled).
        """
        words = text.split()
        tokens = []
        for word in words:
            token = word.strip(',.?!;:"()[]{}').lower()
            if token and token not in self._stopwords:
                tokens.append(token)
        return tokens

    def _align_verses(self, verses_a: list[dict], verses_b: list[dict]) -> list[dict]:
        """Align two verse lists by book/chapter/verse key."""
        aligned_map: dict[tuple[str, int, int], dict] = {}

        for verse in verses_a:
            key = (verse["book_id"], verse["chapter"], verse["verse"])
            aligned_map[key] = {
                "book_id": verse["book_id"],
                "chapter": verse["chapter"],
                "verse": verse["verse"],
                "text_a": verse["text"],
                "text_b": "",
            }

        for verse in verses_b:
            key = (verse["book_id"], verse["chapter"], verse["verse"])
            row = aligned_map.get(key)
            if row is None:
                aligned_map[key] = {
                    "book_id": verse["book_id"],
                    "chapter": verse["chapter"],
                    "verse": verse["verse"],
                    "text_a": "",
                    "text_b": verse["text"],
                }
            else:
                row["text_b"] = verse["text"]

        sorted_keys = sorted(aligned_map.keys(), key=lambda k: (k[0], k[1], k[2]))
        return [aligned_map[key] for key in sorted_keys]

    def _token_overlap_ratio(self, text_a: str, text_b: str) -> float:
        """Compute token-set overlap ratio for two texts."""
        tokens_a = set(self._tokenize(text_a))
        tokens_b = set(self._tokenize(text_b))
        union = tokens_a | tokens_b
        if not union:
            return 1.0
        return len(tokens_a & tokens_b) / len(union)

    @staticmethod
    def _joined_scope_metrics(verses: list[dict]) -> tuple[int, float]:
        """Character count and avg word length (whitespace-split) over joined verse text."""
        full_text = " ".join(v["text"] for v in verses)
        raw_words = full_text.split()
        if not raw_words:
            return 0, 0.0
        return len(full_text), len(full_text) / len(raw_words)

    def _get_all_tokens(self, reference: str, translation_id: str | None = None) -> list[str]:
        """Get all tokens from verses in the given reference.

        Args:
            reference: Bible reference string.
            translation_id: Translation ID to use.

        Returns:
            List of all tokens (may contain duplicates).
        """
        verses = self._verse_service.get_verses(reference, translation_id)
        all_tokens = []
        for verse in verses:
            all_tokens.extend(self._tokenize(verse["text"]))
        return all_tokens

    def token_count(self, reference: str, translation_id: str | None = None) -> int:
        """Count total number of tokens in the given reference.

        Args:
            reference: Bible reference string ("John 3:16" or "John 3:16-18")
            translation_id: Translation ID to use. If None, uses the default.

        Returns:
            Total token count.
        """
        return len(self._get_all_tokens(reference, translation_id))

    def unique_token_count(self, reference: str, translation_id: str | None = None) -> int:
        """Count unique tokens in the given reference.

        Args:
            reference: Bible reference string ("John 3:16" or "John 3:16-18")
            translation_id: Translation ID to use. If None, uses the default.

        Returns:
            Number of unique tokens.
        """
        tokens = self._get_all_tokens(reference, translation_id)
        return len(set(tokens))

    def type_token_ratio(self, reference: str, translation_id: str | None = None) -> float:
        """Calculate type-token ratio (unique tokens / total tokens).

        Args:
            reference: Bible reference string ("John 3:16" or "John 3:16-18")
            translation_id: Translation ID to use. If None, uses the default.

        Returns:
            Ratio between 0.0 and 1.0. Returns 0.0 if no tokens found.
        """
        total = self.token_count(reference, translation_id)
        if total == 0:
            return 0.0
        unique = self.unique_token_count(reference, translation_id)
        return unique / total

    def top_words(
        self, reference: str, translation_id: str | None = None, n: int = 10
    ) -> list[tuple[str, int]]:
        """Get the top N most frequent words in the given reference.

        Args:
            reference: Bible reference string ("John 3:16" or "John 3:16-18")
            translation_id: Translation ID to use. If None, uses the default.
            n: Number of top words to return (default 10).

        Returns:
            List of (word, count) tuples, sorted by count descending,
            then alphabetically for ties.
        """
        tokens = self._get_all_tokens(reference, translation_id)
        if not tokens:
            return []
        counter = Counter(tokens)
        return counter.most_common(n)

    def top_bigrams(
        self, reference: str, translation_id: str | None = None, n: int = 10
    ) -> list[tuple[str, int]]:
        """Get the top N most frequent word pairs (bigrams).

        Args:
            reference: Bible reference string ("John 3:16" or "John 3:16-18")
            translation_id: Translation ID to use. If None, uses the default.
            n: Number of top bigrams to return (default 10).

        Returns:
            List of (bigram, count) tuples where bigram is "word1 word2",
            sorted by count descending, then alphabetically for ties.
        """
        tokens = self._get_all_tokens(reference, translation_id)
        if len(tokens) < 2:
            return []

        bigrams = []
        for i in range(len(tokens) - 1):
            bigrams.append(f"{tokens[i]} {tokens[i + 1]}")

        counter = Counter(bigrams)
        return counter.most_common(n)

    def top_trigrams(
        self, reference: str, translation_id: str | None = None, n: int = 10
    ) -> list[tuple[str, int]]:
        """Get the top N most frequent word triplets (trigrams).

        Args:
            reference: Bible reference string ("John 3:16" or "John 3:16-18")
            translation_id: Translation ID to use. If None, uses the default.
            n: Number of top trigrams to return (default 10).

        Returns:
            List of (trigram, count) tuples where trigram is "word1 word2 word3",
            sorted by count descending, then alphabetically for ties.
        """
        tokens = self._get_all_tokens(reference, translation_id)
        if len(tokens) < 3:
            return []

        trigrams = []
        for i in range(len(tokens) - 2):
            trigrams.append(f"{tokens[i]} {tokens[i + 1]} {tokens[i + 2]}")

        counter = Counter(trigrams)
        return counter.most_common(n)

    def analyze_reference(
        self, reference: str, translation_id: str | None = None, top_n: int = 10
    ) -> dict:
        """Analyze verses in a reference (e.g. 'John 3:16' or 'John 3:16-18').

        Args:
            reference: Bible reference string.
            translation_id: Translation ID to use. If None, uses the default.
            top_n: Number of top items to return for words/bigrams/trigrams.

        Returns:
            Dict with keys: token_count, unique_token_count, type_token_ratio,
            character_count, avg_word_length,
            top_words, top_bigrams, top_trigrams.
        """
        verses = self._verse_service.get_verses(reference, translation_id)
        if not verses:
            return {
                "token_count": 0,
                "unique_token_count": 0,
                "type_token_ratio": 0.0,
                "character_count": 0,
                "avg_word_length": 0.0,
                "top_words": [],
                "top_bigrams": [],
                "top_trigrams": [],
            }

        character_count, avg_word_length = self._joined_scope_metrics(verses)

        all_tokens: list[str] = []
        for verse in verses:
            all_tokens.extend(self._tokenize(verse["text"]))

        if not all_tokens:
            return {
                "token_count": 0,
                "unique_token_count": 0,
                "type_token_ratio": 0.0,
                "character_count": character_count,
                "avg_word_length": avg_word_length,
                "top_words": [],
                "top_bigrams": [],
                "top_trigrams": [],
            }

        unique = len(set(all_tokens))
        total = len(all_tokens)

        return {
            "token_count": total,
            "unique_token_count": unique,
            "type_token_ratio": unique / total,
            "character_count": character_count,
            "avg_word_length": avg_word_length,
            "top_words": Counter(all_tokens).most_common(top_n),
            "top_bigrams": self._get_bigrams(all_tokens, top_n),
            "top_trigrams": self._get_trigrams(all_tokens, top_n),
        }

    def analyze_chapter(
        self,
        book_name: str,
        chapter: int,
        translation_id: str | None = None,
        top_n: int = 10,
    ) -> dict:
        """Analyze all verses in a chapter.

        Args:
            book_name: Book name (e.g. "John", "Genesis").
            chapter: Chapter number.
            translation_id: Translation ID to use. If None, uses the default.
            top_n: Number of top items to return for words/bigrams/trigrams.

        Returns:
            Dict with keys: token_count, unique_token_count, type_token_ratio,
            character_count, avg_word_length,
            top_words, top_bigrams, top_trigrams.
        """
        verses = self._verse_service.get_chapter_verses(book_name, chapter, translation_id)
        if not verses:
            return {
                "token_count": 0,
                "unique_token_count": 0,
                "type_token_ratio": 0.0,
                "character_count": 0,
                "avg_word_length": 0.0,
                "top_words": [],
                "top_bigrams": [],
                "top_trigrams": [],
            }

        character_count, avg_word_length = self._joined_scope_metrics(verses)

        all_tokens = []
        for verse in verses:
            all_tokens.extend(self._tokenize(verse["text"]))

        unique = len(set(all_tokens))
        total = len(all_tokens)

        return {
            "token_count": total,
            "unique_token_count": unique,
            "type_token_ratio": unique / total if total > 0 else 0.0,
            "character_count": character_count,
            "avg_word_length": avg_word_length,
            "top_words": Counter(all_tokens).most_common(top_n),
            "top_bigrams": self._get_bigrams(all_tokens, top_n),
            "top_trigrams": self._get_trigrams(all_tokens, top_n),
        }

    def analyze_book(
        self, book_name: str, translation_id: str | None = None, top_n: int = 10
    ) -> dict:
        """Analyze all verses in a book.

        Args:
            book_name: Book name (e.g. "John", "Genesis").
            translation_id: Translation ID to use. If None, uses the default.
            top_n: Number of top items to return for words/bigrams/trigrams.

        Returns:
            Dict with keys: token_count, unique_token_count, type_token_ratio,
            character_count, avg_word_length,
            top_words, top_bigrams, top_trigrams.
        """
        verses = self._verse_service.get_book_verses(book_name, translation_id)
        if not verses:
            return {
                "token_count": 0,
                "unique_token_count": 0,
                "type_token_ratio": 0.0,
                "character_count": 0,
                "avg_word_length": 0.0,
                "top_words": [],
                "top_bigrams": [],
                "top_trigrams": [],
            }

        character_count, avg_word_length = self._joined_scope_metrics(verses)

        all_tokens = []
        for verse in verses:
            all_tokens.extend(self._tokenize(verse["text"]))

        unique = len(set(all_tokens))
        total = len(all_tokens)

        return {
            "token_count": total,
            "unique_token_count": unique,
            "type_token_ratio": unique / total if total > 0 else 0.0,
            "character_count": character_count,
            "avg_word_length": avg_word_length,
            "top_words": Counter(all_tokens).most_common(top_n),
            "top_bigrams": self._get_bigrams(all_tokens, top_n),
            "top_trigrams": self._get_trigrams(all_tokens, top_n),
        }

    def compare_translations(
        self,
        reference: str,
        translation_a: str,
        translation_b: str,
    ) -> dict:
        """Compare two translations for one reference and return similarity analytics."""
        verses_a = self._verse_service.get_verses(reference, translation_a)
        verses_b = self._verse_service.get_verses(reference, translation_b)
        aligned_verses = self._align_verses(verses_a, verses_b)

        if not aligned_verses:
            return {
                "reference": reference,
                "translation_a": translation_a,
                "translation_b": translation_b,
                "aligned_verses": [],
                "summary": {
                    "total_verses": 0,
                    "fully_aligned_verses": 0,
                    "exact_matches": 0,
                    "exact_match_ratio": 0.0,
                    "average_similarity": 0.0,
                    "top_shared_words": [],
                    "most_similar_verse": None,
                },
            }

        shared_tokens_counter: Counter[str] = Counter()
        exact_matches = 0
        fully_aligned = 0
        similarity_sum = 0.0
        most_similar_verse: dict | None = None

        for row in aligned_verses:
            text_a = row["text_a"]
            text_b = row["text_b"]
            if text_a and text_b:
                fully_aligned += 1
                normalized_a = text_a.strip().lower()
                normalized_b = text_b.strip().lower()
                is_exact = normalized_a == normalized_b
                if is_exact:
                    exact_matches += 1

                sequence_ratio = SequenceMatcher(None, normalized_a, normalized_b).ratio()
                overlap_ratio = self._token_overlap_ratio(text_a, text_b)
                similarity = (sequence_ratio + overlap_ratio) / 2
                similarity_sum += similarity

                shared_tokens_counter.update(
                    set(self._tokenize(text_a)) & set(self._tokenize(text_b))
                )

                if most_similar_verse is None or similarity > most_similar_verse["similarity"]:
                    most_similar_verse = {
                        "reference": f"{row['book_id']} {row['chapter']}:{row['verse']}",
                        "similarity": similarity,
                    }
            else:
                is_exact = False
                similarity = 0.0

            row["similarity"] = similarity
            row["exact_match"] = is_exact

        average_similarity = similarity_sum / fully_aligned if fully_aligned > 0 else 0.0
        exact_match_ratio = exact_matches / fully_aligned if fully_aligned > 0 else 0.0

        return {
            "reference": reference,
            "translation_a": translation_a,
            "translation_b": translation_b,
            "aligned_verses": aligned_verses,
            "summary": {
                "total_verses": len(aligned_verses),
                "fully_aligned_verses": fully_aligned,
                "exact_matches": exact_matches,
                "exact_match_ratio": exact_match_ratio,
                "average_similarity": average_similarity,
                "top_shared_words": shared_tokens_counter.most_common(8),
                "most_similar_verse": most_similar_verse,
            },
        }

    def _get_bigrams(self, tokens: list[str], n: int) -> list[tuple[str, int]]:
        """Extract top N bigrams from token list."""
        if len(tokens) < 2:
            return []
        bigrams = []
        for i in range(len(tokens) - 1):
            bigrams.append(f"{tokens[i]} {tokens[i + 1]}")
        return Counter(bigrams).most_common(n)

    def _get_trigrams(self, tokens: list[str], n: int) -> list[tuple[str, int]]:
        """Extract top N trigrams from token list."""
        if len(tokens) < 3:
            return []
        trigrams = []
        for i in range(len(tokens) - 2):
            trigrams.append(f"{tokens[i]} {tokens[i + 1]} {tokens[i + 2]}")
        return Counter(trigrams).most_common(n)

    def concordance(self, word: str, translation_id: str | None = None) -> list[dict]:
        """Generate a concordance for a given word using FTS5 full-text search.

        Args:
            word: The word to search for (case-insensitive).
            translation_id: Optional translation ID to filter by.
                If None, searches all translations.

        Returns:
            List of verse dicts that contain the specified word,
            ordered by book/chapter/verse.
        """
        if not word or not word.strip():
            raise ValueError("Search word cannot be empty.")
        return self._verse_service.search_text(word, translation_id)
