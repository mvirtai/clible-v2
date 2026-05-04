"""Tests for localized book name resolution."""

from clible.utils.book_names import get_display_name, get_fi_abbrev, resolve_book_id


def test_resolve_book_id_finnish_abbrev_evangelists():
    """Short Finnish abbreviations (FI Bible style) resolve to the right books."""
    assert resolve_book_id("matt") == "MAT"
    assert resolve_book_id("mark") == "MRK"
    assert resolve_book_id("luuk") == "LUK"
    assert resolve_book_id("joh") == "JHN"
    assert resolve_book_id("Matt.") == "MAT"
    assert resolve_book_id("Luuk.") == "LUK"


def test_get_fi_abbrev_returns_short_code():
    """get_fi_abbrev returns citation-style slug for stats / UI."""
    assert get_fi_abbrev("LUK") == "luuk"
    assert get_fi_abbrev("MAT") == "matt"


def test_get_display_name_fi_returns_finnish_title():
    """get_display_name returns KR92-style Finnish titles (not the short evangelist-only form)."""
    assert get_display_name("LUK", "fi") == "Evankeliumi Luukkaan mukaan"
    assert get_display_name("1CO", "fi") == "1. kirje korinttilaisille"
    assert get_display_name("REV", "fi") == "Johanneksen ilmestys"


def test_get_display_name_en_returns_english():
    """get_display_name returns English for Luke."""
    assert get_display_name("LUK", "en") == "Luke"


def test_get_display_name_unknown_book_returns_id():
    """Unknown book id falls back to raw id."""
    assert get_display_name("ZZZ", "fi") == "ZZZ"


def test_resolve_book_id_finnish_name_and_alias():
    """Finnish book names and aliases resolve to canonical ids."""
    assert resolve_book_id("Luukas") == "LUK"
    assert resolve_book_id("LUUKAS") == "LUK"
    assert resolve_book_id("Johanneksen evankeliumi") == "JHN"


def test_resolve_kr92_and_1938_corinthians_aliases():
    """KR92 canonical titles and 1938 *-kirje* forms resolve the same."""
    assert resolve_book_id("1. kirje korinttilaisille") == "1CO"
    assert resolve_book_id("1. Korinttolaiskirje") == "1CO"


def test_resolve_revelation_fi_alternate_titles():
    """Ilmestyskirja / Ilmestys resolve; primary FI label is Johanneksen ilmestys."""
    assert resolve_book_id("Ilmestyskirja") == "REV"
    assert resolve_book_id("Ilmestys") == "REV"


def test_resolve_book_id_english_and_id():
    """English names and abbreviations still resolve."""
    assert resolve_book_id("Luke") == "LUK"
    assert resolve_book_id("luk") == "LUK"


def test_resolve_book_id_unknown_returns_none():
    """Nonsense token does not resolve."""
    assert resolve_book_id("xyzzy") is None
