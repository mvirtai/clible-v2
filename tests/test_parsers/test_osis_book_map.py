"""Tests for OSIS book ID mapping."""

from clible.parsers.osis_book_map import OSIS_TO_CLIBLE, to_clible_id


def test_to_clible_id_genesis():
    """Gen maps to GEN."""
    assert to_clible_id("Gen") == "GEN"


def test_to_clible_id_matthew():
    """Matt maps to MAT."""
    assert to_clible_id("Matt") == "MAT"


def test_to_clible_id_mark():
    """Mark maps to MRK."""
    assert to_clible_id("Mark") == "MRK"


def test_to_clible_id_john():
    """John maps to JHN."""
    assert to_clible_id("John") == "JHN"


def test_to_clible_id_nahum():
    """Nah maps to NAH (OSIS uses Nah, not NAM)."""
    assert to_clible_id("Nah") == "NAH"


def test_to_clible_id_numbered_books():
    """Numbered books map correctly."""
    assert to_clible_id("1Sam") == "1SA"
    assert to_clible_id("2Kgs") == "2KI"
    assert to_clible_id("1Cor") == "1CO"
    assert to_clible_id("1John") == "1JN"


def test_to_clible_id_unknown_returns_none():
    """Unknown OSIS ID returns None."""
    assert to_clible_id("Tob") is None
    assert to_clible_id("Jdt") is None
    assert to_clible_id("Wis") is None
    assert to_clible_id("") is None


def test_osis_to_clible_has_66_canonical_books():
    """Mapping covers all 66 canonical books."""
    assert len(OSIS_TO_CLIBLE) == 66


def test_all_clible_ids_are_expected_format():
    """Clible IDs are 2-3 chars, valid format (e.g. GEN, 1SA)."""
    for clible_id in OSIS_TO_CLIBLE.values():
        assert 2 <= len(clible_id) <= 3
        assert all(c.isupper() or c.isdigit() for c in clible_id)
