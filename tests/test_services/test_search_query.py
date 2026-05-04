import pytest

from clible.services.search_query import SearchQuery


def test_phrase_mode_wraps_in_quotes():
    q = SearchQuery(["grace"], mode="phrase")
    assert q.to_fts5_match() == '"grace"'


def test_phrase_mode_joins_multiple_term_tokens():
    q = SearchQuery(["in", "the", "beginning"], mode="phrase")
    assert q.to_fts5_match() == '"in the beginning"'


def test_boolean_and():
    q = SearchQuery(["love", "grace"], operator="AND", mode="boolean")
    assert q.to_fts5_match() == "love AND grace"


def test_boolean_or():
    q = SearchQuery(["faith", "hope"], operator="OR", mode="boolean")
    assert q.to_fts5_match() == "faith OR hope"


def test_boolean_single_term():
    q = SearchQuery(["love"], operator="AND", mode="boolean")
    assert q.to_fts5_match() == "love"


def test_wildcard_star():
    q = SearchQuery(["lov*"], mode="wildcard")
    assert q.to_regex_pattern() == r"lov\w*"


def test_wildcard_question_mark():
    q = SearchQuery(["wom?n"], mode="wildcard")
    assert q.to_regex_pattern() == r"wom.n"


def test_to_fts5_raises_in_wildcard_mode():
    q = SearchQuery(["lov*"], mode="wildcard")
    with pytest.raises(ValueError):
        q.to_fts5_match()


def test_to_regex_raises_outside_wildcard_mode():
    q = SearchQuery(["grace"], mode="phrase")
    with pytest.raises(ValueError):
        q.to_regex_pattern()
