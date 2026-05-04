import pytest

from clible.db.repositories.verse_repo import VerseRepo
from clible.db.seed_books import seed_books_if_empty


@pytest.fixture
def repo_with_verses(db_conn):
    seed_books_if_empty(db_conn)
    db_conn.execute(
        "INSERT OR IGNORE INTO translations (id, name, language, format, source_url) "
        "VALUES ('test', 'Test', 'en', 'usfx', 'http://example.com')"
    )
    db_conn.execute(
        "INSERT INTO verses (id, translation_id, book_id, chapter, verse, text) "
        "VALUES ('v1', 'test', 'JHN', 1, 1, 'In the beginning was the Word')"
    )
    db_conn.execute(
        "INSERT INTO verses (id, translation_id, book_id, chapter, verse, text) "
        "VALUES ('v2', 'test', 'JHN', 1, 2, 'He was with God in the beginning')"
    )
    db_conn.execute("INSERT INTO verses_fts(verses_fts) VALUES('rebuild')")
    db_conn.commit()
    return VerseRepo(db_conn)


def test_wildcard_star_matches_suffix(repo_with_verses):
    results = repo_with_verses.search_wildcard(r"beg\w*")
    assert len(results) == 2


def test_wildcard_is_case_insensitive(repo_with_verses):
    results = repo_with_verses.search_wildcard(r"word")
    assert len(results) == 1


def test_wildcard_book_scope(repo_with_verses):
    results = repo_with_verses.search_wildcard(r"beg\w*", book_id="PSA")
    assert len(results) == 0
