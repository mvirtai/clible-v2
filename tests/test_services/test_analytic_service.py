import pytest

from clible.services.analytic_service import AnalyticService


@pytest.fixture
def verse_service_mock(mocker):
    """Mock VerseService for testing AnalyticService."""
    return mocker.Mock()


@pytest.fixture
def analytic_service(verse_service_mock):
    """AnalyticService instance with mocked VerseService."""
    return AnalyticService(verse_service=verse_service_mock)


def test_word_freq_single_verse(analytic_service, verse_service_mock):
    """word_freq returns correct frequency for single verse."""
    verse_service_mock.get_verses.return_value = [
        {"text": "In the beginning God created the heaven and the earth."}
    ]
    freq = analytic_service.word_freq("Genesis 1:1")
    expected = {
        "in": 1,
        "the": 3,
        "beginning": 1,
        "god": 1,
        "created": 1,
        "heaven": 1,
        "and": 1,
        "earth": 1,
    }
    assert freq == expected


def test_word_freq_multiple_verses(analytic_service, verse_service_mock):
    """word_freq aggregates frequency across multiple verses."""
    verse_service_mock.get_verses.return_value = [
        {"text": "In the beginning God created the heaven and the earth."},
        {
            "text": "And the earth was without form, and void; and darkness was upon the face of the deep."
        },
    ]
    freq = analytic_service.word_freq("Genesis 1:1-2")
    expected = {
        "in": 1,
        "the": 6,
        "beginning": 1,
        "god": 1,
        "created": 1,
        "heaven": 1,
        "and": 4,
        "earth": 2,
        "was": 2,
        "without": 1,
        "form": 1,
        "void": 1,
        "darkness": 1,
        "upon": 1,
        "face": 1,
        "of": 1,
        "deep": 1,
    }
    assert freq == expected


def test_word_freq_no_verses(analytic_service, verse_service_mock):
    """word_freq returns empty dict if no verses found."""
    verse_service_mock.get_verses.return_value = []
    freq = analytic_service.word_freq("Unknown 1:1")
    assert freq == {}
