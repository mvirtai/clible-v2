"""Tests for BookRepo.

BookRepo is read-only; the books table is seeded from bible_structure.json
when the database is initialized. Tests verify get_all, get_by_id, get_by_name,
search, and that Testament enum is correctly applied.
"""

from clible.db.repositories.book_repo import BookRepo, Testament


def test_get_all_returns_66_books_ordered_by_position(book_repo: BookRepo):
    """Books table is seeded with 66 canonical books, ordered by position."""
    result = book_repo.get_all()
    assert len(result) == 66
    assert result[0]["id"] == "GEN"
    assert result[0]["name"] == "Genesis"
    assert result[-1]["id"] == "REV"
    assert result[-1]["name"] == "Revelation"

    positions = [b["position"] for b in result]
    assert positions == list(range(1, 67))


def test_get_by_id_returns_book_when_found(book_repo: BookRepo):
    """get_by_id returns full BookRow for valid book id."""
    row = book_repo.get_by_id("GEN")
    assert row is not None
    assert row["id"] == "GEN"
    assert row["name"] == "Genesis"
    assert row["testament"] == Testament.OT
    assert row["position"] == 1
    assert row["chapters"] == 50


def test_get_by_id_returns_none_for_invalid_id(book_repo: BookRepo):
    """get_by_id returns None for non-existent book."""
    assert book_repo.get_by_id("XXX") is None
    assert book_repo.get_by_id("") is None


def test_get_by_id_returns_nt_book_with_nt_testament(book_repo: BookRepo):
    """New Testament books have testament NT."""
    row = book_repo.get_by_id("JHN")
    assert row is not None
    assert row["testament"] == Testament.NT
    assert row["name"] == "John"
    assert row["chapters"] == 21


def test_get_by_name_returns_book_for_exact_match(book_repo: BookRepo):
    """get_by_name returns book when name matches exactly."""
    row = book_repo.get_by_name("Genesis")
    assert row is not None
    assert row["id"] == "GEN"
    assert row["name"] == "Genesis"


def test_get_by_name_returns_none_for_nonexistent(book_repo: BookRepo):
    """get_by_name returns None when no exact match."""
    assert book_repo.get_by_name("Nonexistent Book") is None
    assert book_repo.get_by_name("genesis") is None


def test_get_by_name_matches_multi_word_books(book_repo: BookRepo):
    """get_by_name handles books with numbers and multiple words."""
    row = book_repo.get_by_name("1 Corinthians")
    assert row is not None
    assert row["id"] == "1CO"
    assert row["chapters"] == 16


def test_search_by_id_partial_match(book_repo: BookRepo):
    """search() finds books by partial id match (e.g. GEN, gen)."""
    result = book_repo.search("GEN")
    assert len(result) >= 1
    assert any(b["id"] == "GEN" for b in result)

    result_lower = book_repo.search("gen")
    assert len(result_lower) >= 1
    assert any(b["id"] == "GEN" for b in result_lower)


def test_search_by_name_partial_match(book_repo: BookRepo):
    """search() finds books by partial name match."""
    result = book_repo.search("John")
    assert len(result) >= 1
    ids = [b["id"] for b in result]
    assert "JHN" in ids

    result_gen = book_repo.search("Gen")
    assert any(b["id"] == "GEN" for b in result_gen)


def test_search_returns_empty_list_for_no_match(book_repo: BookRepo):
    """search() returns empty list when no book matches."""
    result = book_repo.search("xyznonexistent")
    assert result == []


def test_search_results_ordered_by_position(book_repo: BookRepo):
    """search() returns results ordered by position in the Bible."""
    result = book_repo.search("1 ")
    assert len(result) >= 2
    positions = [b["position"] for b in result]
    assert positions == sorted(positions)


def test_search_matches_both_id_and_name(book_repo: BookRepo):
    """search() matches against both id and name columns."""
    by_id = book_repo.search("PSA")
    by_name = book_repo.search("Psalm")
    assert any(b["id"] == "PSA" for b in by_id)
    assert any(b["id"] == "PSA" for b in by_name)


def test_bookrow_contains_testament_enum(book_repo: BookRepo):
    """BookRow dicts have testament as Testament enum, not raw string."""
    ot_book = book_repo.get_by_id("GEN")
    nt_book = book_repo.get_by_id("MAT")
    assert ot_book["testament"] == Testament.OT
    assert nt_book["testament"] == Testament.NT
    assert isinstance(ot_book["testament"], Testament)


def test_repo_returns_plain_dicts_not_row(book_repo: BookRepo):
    """BookRepo returns dict-like BookRow, not sqlite3.Row."""
    row = book_repo.get_by_id("GEN")
    assert isinstance(row, dict)
    assert type(row).__name__ != "Row"


def test_get_by_testament_returns_ot_books(book_repo: BookRepo):
    """get_by_testament(OT) returns all Old Testament books."""
    ot_books = book_repo.get_by_testament(Testament.OT)
    assert len(ot_books) == 39
    assert all(b["testament"] == Testament.OT for b in ot_books)
    assert ot_books[0]["id"] == "GEN"
    assert ot_books[-1]["id"] == "MAL"


def test_get_by_testament_returns_nt_books(book_repo: BookRepo):
    """get_by_testament(NT) returns all New Testament books."""
    nt_books = book_repo.get_by_testament(Testament.NT)
    assert len(nt_books) == 27
    assert all(b["testament"] == Testament.NT for b in nt_books)
    assert nt_books[0]["id"] == "MAT"
    assert nt_books[-1]["id"] == "REV"


def test_get_by_testament_ordered_by_position(book_repo: BookRepo):
    """get_by_testament returns books in canonical order."""
    ot_books = book_repo.get_by_testament(Testament.OT)
    positions = [b["position"] for b in ot_books]
    assert positions == sorted(positions)
