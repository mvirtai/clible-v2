"""Tests for AnalyticService.

Tests token counting, type-token ratio, top-N word/bigram/trigram analysis,
and concordance search functionality.
"""

import pytest

from clible.services.analytic_service import AnalyticService


@pytest.fixture
def verse_service_mock(mocker):
    """Mock VerseService for testing AnalyticService."""
    return mocker.Mock()


@pytest.fixture
def analytic_service(verse_service_mock):
    """AnalyticService instance with mocked VerseService and stopwords enabled."""
    return AnalyticService(verse_service=verse_service_mock, filter_stopwords=True)


@pytest.fixture
def analytic_service_no_filter(verse_service_mock):
    """AnalyticService instance without stopword filtering."""
    return AnalyticService(verse_service=verse_service_mock, filter_stopwords=False)


def test_token_count_single_verse(analytic_service, verse_service_mock):
    """token_count returns correct count for single verse (with stopwords filtered)."""
    verse_service_mock.get_verses.return_value = [
        {"text": "In the beginning God created the heaven and the earth."}
    ]
    count = analytic_service.token_count("Genesis 1:1")
    assert count == 5


def test_token_count_multiple_verses(analytic_service, verse_service_mock):
    """token_count sums tokens across multiple verses (with stopwords filtered)."""
    verse_service_mock.get_verses.return_value = [
        {"text": "In the beginning"},
        {"text": "God created"},
    ]
    count = analytic_service.token_count("Genesis 1:1-2")
    assert count == 3


def test_token_count_empty_returns_zero(analytic_service, verse_service_mock):
    """token_count returns 0 when no verses found."""
    verse_service_mock.get_verses.return_value = []
    count = analytic_service.token_count("Unknown 1:1")
    assert count == 0


def test_unique_token_count_single_verse(analytic_service, verse_service_mock):
    """unique_token_count returns correct count for single verse (stopwords filtered)."""
    verse_service_mock.get_verses.return_value = [
        {"text": "In the beginning God created the heaven and the earth."}
    ]
    count = analytic_service.unique_token_count("Genesis 1:1")
    assert count == 5


def test_unique_token_count_multiple_verses(analytic_service, verse_service_mock):
    """unique_token_count counts unique tokens across multiple verses."""
    verse_service_mock.get_verses.return_value = [
        {"text": "In the beginning"},
        {"text": "In the end"},
    ]
    count = analytic_service.unique_token_count("Test 1:1-2")
    assert count == 2


def test_type_token_ratio_calculates_correctly(analytic_service_no_filter, verse_service_mock):
    """type_token_ratio returns unique/total ratio (without stopword filtering)."""
    verse_service_mock.get_verses.return_value = [{"text": "the the the word"}]
    ratio = analytic_service_no_filter.type_token_ratio("Test 1:1")
    assert ratio == 0.5


def test_type_token_ratio_returns_zero_when_empty(analytic_service, verse_service_mock):
    """type_token_ratio returns 0.0 when no tokens."""
    verse_service_mock.get_verses.return_value = []
    ratio = analytic_service.type_token_ratio("Unknown 1:1")
    assert ratio == 0.0


def test_top_words_returns_most_frequent(analytic_service_no_filter, verse_service_mock):
    """top_words returns words sorted by frequency descending (no stopwords)."""
    verse_service_mock.get_verses.return_value = [{"text": "the the the word word other"}]
    top = analytic_service_no_filter.top_words("Test 1:1", n=3)
    assert top == [("the", 3), ("word", 2), ("other", 1)]


def test_top_words_returns_empty_when_no_verses(analytic_service, verse_service_mock):
    """top_words returns empty list when no verses found."""
    verse_service_mock.get_verses.return_value = []
    top = analytic_service.top_words("Unknown 1:1")
    assert top == []


def test_top_words_limits_to_n(analytic_service, verse_service_mock):
    """top_words returns at most n words."""
    verse_service_mock.get_verses.return_value = [{"text": "a b c d e f g h i j k"}]
    top = analytic_service.top_words("Test 1:1", n=3)
    assert len(top) == 3


def test_top_bigrams_returns_most_frequent_pairs(analytic_service, verse_service_mock):
    """top_bigrams returns word pairs sorted by frequency."""
    verse_service_mock.get_verses.return_value = [{"text": "God created heaven God created earth"}]
    top = analytic_service.top_bigrams("Test 1:1", n=2)
    assert top == [("god created", 2), ("created heaven", 1)]


def test_top_bigrams_returns_empty_when_too_few_tokens(analytic_service, verse_service_mock):
    """top_bigrams returns empty list when fewer than 2 tokens."""
    verse_service_mock.get_verses.return_value = [{"text": "word"}]
    top = analytic_service.top_bigrams("Test 1:1")
    assert top == []


def test_top_trigrams_returns_most_frequent_triplets(analytic_service, verse_service_mock):
    """top_trigrams returns word triplets sorted by frequency."""
    verse_service_mock.get_verses.return_value = [
        {"text": "God created heaven earth God created light"}
    ]
    top = analytic_service.top_trigrams("Test 1:1", n=2)
    assert len(top) == 2
    assert top[0] == ("god created heaven", 1)


def test_top_trigrams_returns_empty_when_too_few_tokens(analytic_service, verse_service_mock):
    """top_trigrams returns empty list when fewer than 3 tokens."""
    verse_service_mock.get_verses.return_value = [{"text": "one two"}]
    top = analytic_service.top_trigrams("Test 1:1")
    assert top == []


def test_concordance_calls_search_text(analytic_service, verse_service_mock):
    """concordance delegates to verse_service.search_text."""
    verse_service_mock.search_text.return_value = [
        {"book_id": "GEN", "chapter": 1, "verse": 1, "text": "God created"}
    ]
    results = analytic_service.concordance("God", "web")
    verse_service_mock.search_text.assert_called_once_with("God", "web")
    assert len(results) == 1
    assert results[0]["text"] == "God created"


def test_concordance_raises_on_empty_word(analytic_service, verse_service_mock):
    """concordance raises ValueError for empty word."""
    with pytest.raises(ValueError, match="Search word cannot be empty"):
        analytic_service.concordance("")

    with pytest.raises(ValueError, match="Search word cannot be empty"):
        analytic_service.concordance("   ")


def test_stopword_filtering_removes_common_words(analytic_service, verse_service_mock):
    """Stopword filtering removes common English words from token counts."""
    verse_service_mock.get_verses.return_value = [
        {"text": "In the beginning God created the heaven and the earth"}
    ]
    tokens = analytic_service.token_count("Genesis 1:1")
    unique = analytic_service.unique_token_count("Genesis 1:1")
    top = analytic_service.top_words("Genesis 1:1", n=5)

    assert tokens == 5
    assert unique == 5
    assert len(top) == 5
    assert all(word not in ["in", "the", "and"] for word, _ in top)


def test_no_stopword_filter_keeps_all_words(analytic_service_no_filter, verse_service_mock):
    """Without stopword filtering, all tokens are counted."""
    verse_service_mock.get_verses.return_value = [{"text": "In the beginning God created"}]
    tokens = analytic_service_no_filter.token_count("Genesis 1:1")
    top = analytic_service_no_filter.top_words("Genesis 1:1", n=5)

    assert tokens == 5
    assert any(word in ["in", "the"] for word, _ in top)


def test_analyze_reference_returns_all_metrics(analytic_service, verse_service_mock):
    """analyze_reference returns complete analysis dict."""
    verse_service_mock.get_verses.return_value = [{"text": "In the beginning God created"}]
    result = analytic_service.analyze_reference("Genesis 1:1")
    assert "token_count" in result
    assert "unique_token_count" in result
    assert "type_token_ratio" in result
    assert "character_count" in result
    assert "avg_word_length" in result
    assert "top_words" in result
    assert "top_bigrams" in result
    assert "top_trigrams" in result
    assert result["token_count"] == 3
    assert result["unique_token_count"] == 3
    assert result["character_count"] == len("In the beginning God created")
    assert result["avg_word_length"] == pytest.approx(28 / 5)


def test_analyze_chapter_returns_all_metrics(analytic_service, verse_service_mock):
    """analyze_chapter returns complete analysis dict."""
    verse_service_mock.get_chapter_verses.return_value = [
        {"text": "In the beginning"},
        {"text": "God created"},
    ]
    result = analytic_service.analyze_chapter("Genesis", 1)
    assert result["token_count"] == 3
    assert result["unique_token_count"] == 3
    joined = "In the beginning God created"
    assert result["character_count"] == len(joined)
    assert result["avg_word_length"] == pytest.approx(len(joined) / len(joined.split()))
    assert len(result["top_words"]) > 0


def test_analyze_chapter_returns_empty_metrics_when_no_verses(analytic_service, verse_service_mock):
    """analyze_chapter returns zero metrics when chapter has no verses."""
    verse_service_mock.get_chapter_verses.return_value = []
    result = analytic_service.analyze_chapter("Unknown", 1)
    assert result["token_count"] == 0
    assert result["unique_token_count"] == 0
    assert result["type_token_ratio"] == 0.0
    assert result["character_count"] == 0
    assert result["avg_word_length"] == 0.0
    assert result["top_words"] == []


def test_analyze_book_returns_all_metrics(analytic_service, verse_service_mock):
    """analyze_book returns complete analysis dict."""
    verse_service_mock.get_book_verses.return_value = [
        {"text": "In the beginning God created the heaven"},
        {"text": "And the earth was without form"},
    ]
    result = analytic_service.analyze_book("Genesis")
    assert result["token_count"] == 7
    assert result["unique_token_count"] == 7
    joined = (
        "In the beginning God created the heaven "
        "And the earth was without form"
    )
    assert result["character_count"] == len(joined)
    assert result["avg_word_length"] == pytest.approx(len(joined) / len(joined.split()))
    assert len(result["top_words"]) > 0


def test_analyze_book_returns_empty_metrics_when_no_verses(analytic_service, verse_service_mock):
    """analyze_book returns zero metrics when book has no verses."""
    verse_service_mock.get_book_verses.return_value = []
    result = analytic_service.analyze_book("Unknown")
    assert result["token_count"] == 0
    assert result["unique_token_count"] == 0
    assert result["type_token_ratio"] == 0.0
    assert result["character_count"] == 0
    assert result["avg_word_length"] == 0.0
    assert result["top_words"] == []


def test_compare_translations_returns_aligned_rows_and_similarity_summary(
    analytic_service_no_filter, verse_service_mock
):
    """compare_translations returns side-by-side rows and aggregate similarity metrics."""

    def _verses_for_translation(_reference: str, translation_id: str) -> list[dict]:
        if translation_id == "fin-1992":
            return [
                {
                    "book_id": "JHN",
                    "chapter": 3,
                    "verse": 16,
                    "text": "Sillä niin on Jumala maailmaa rakastanut",
                },
                {
                    "book_id": "JHN",
                    "chapter": 3,
                    "verse": 17,
                    "text": "Jumala ei lähettänyt Poikaansa tuomitsemaan maailmaa",
                },
            ]
        return [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä Jumala on rakastanut maailmaa niin paljon",
            },
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 17,
                "text": "Jumala ei lähettänyt Poikaansa tuomitsemaan maailmaa",
            },
        ]

    verse_service_mock.get_verses.side_effect = _verses_for_translation

    result = analytic_service_no_filter.compare_translations(
        "John 3:16-17",
        "fin-1992",
        "fin-1776",
    )

    assert result["translation_a"] == "fin-1992"
    assert result["translation_b"] == "fin-1776"
    assert len(result["aligned_verses"]) == 2
    assert result["summary"]["total_verses"] == 2
    assert result["summary"]["fully_aligned_verses"] == 2
    assert result["summary"]["exact_matches"] == 1
    assert 0.0 < result["summary"]["average_similarity"] <= 1.0
    assert result["summary"]["most_similar_verse"]["reference"] == "JHN 3:17"
    assert result["summary"]["top_shared_words"]


def test_compare_translations_handles_missing_verses_between_translations(
    analytic_service_no_filter, verse_service_mock
):
    """compare_translations keeps unmatched verses and sets their similarity to zero."""

    def _verses_for_translation(_reference: str, translation_id: str) -> list[dict]:
        if translation_id == "fin-1992":
            return [
                {
                    "book_id": "JHN",
                    "chapter": 3,
                    "verse": 16,
                    "text": "Sillä niin on Jumala maailmaa rakastanut",
                }
            ]
        return [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text": "Sillä niin on Jumala maailmaa rakastanut",
            },
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 17,
                "text": "Hän ei lähettänyt Poikaansa maailmaan tuomitsemaan",
            },
        ]

    verse_service_mock.get_verses.side_effect = _verses_for_translation

    result = analytic_service_no_filter.compare_translations(
        "John 3:16-17",
        "fin-1992",
        "fin-1776",
    )

    assert result["summary"]["total_verses"] == 2
    assert result["summary"]["fully_aligned_verses"] == 1
    assert result["summary"]["exact_matches"] == 1

    second_row = result["aligned_verses"][1]
    assert second_row["verse"] == 17
    assert second_row["text_a"] == ""
    assert second_row["text_b"] != ""
    assert second_row["similarity"] == 0.0
    assert not second_row["exact_match"]


def test_compare_translations_returns_empty_summary_when_no_verses_found(
    analytic_service_no_filter, verse_service_mock
):
    """compare_translations returns zeroed summary when neither translation has verses."""
    verse_service_mock.get_verses.return_value = []

    result = analytic_service_no_filter.compare_translations(
        "Unknown 1:1",
        "fin-1992",
        "fin-1776",
    )

    assert result["aligned_verses"] == []
    assert result["summary"]["total_verses"] == 0
    assert result["summary"]["fully_aligned_verses"] == 0
    assert result["summary"]["exact_matches"] == 0
    assert result["summary"]["average_similarity"] == 0.0
    assert result["summary"]["most_similar_verse"] is None


def test_compare_translations_ignores_unaligned_verses_in_most_similar_summary(
    analytic_service_no_filter, verse_service_mock
):
    """compare_translations leaves most_similar_verse empty when no verse pair aligns."""

    def _verses_for_translation(_reference: str, translation_id: str) -> list[dict]:
        if translation_id == "fin-1992":
            return [
                {
                    "book_id": "JHN",
                    "chapter": 3,
                    "verse": 16,
                    "text": "Sillä niin on Jumala maailmaa rakastanut",
                }
            ]
        return [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 17,
                "text": "Hän ei lähettänyt Poikaansa maailmaan tuomitsemaan",
            }
        ]

    verse_service_mock.get_verses.side_effect = _verses_for_translation

    result = analytic_service_no_filter.compare_translations(
        "John 3:16-17",
        "fin-1992",
        "fin-1776",
    )

    assert result["summary"]["total_verses"] == 2
    assert result["summary"]["fully_aligned_verses"] == 0
    assert result["summary"]["average_similarity"] == 0.0
    assert result["summary"]["most_similar_verse"] is None
