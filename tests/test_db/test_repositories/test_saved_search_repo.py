"""Tests for SavedSearchRepo."""

from clible.db.repositories.saved_search_repo import SavedSearchRepo
from clible.db.repositories.scope_repo import ScopeRepo


def test_create_get_and_list_by_scope(db_conn):
    """create stores a row retrievable by id and scope listing."""
    scope_repo = ScopeRepo(db_conn)
    scope_id = scope_repo.create("default")
    repo = SavedSearchRepo(db_conn)

    search_id = repo.create(
        scope_id=scope_id,
        name="grace-search",
        query_text="grace",
        search_scope="book",
        scope_value="John",
        translation_id=None,
    )

    row = repo.get(search_id)
    assert row is not None
    assert row["name"] == "grace-search"
    assert row["query_text"] == "grace"

    items = repo.list_by_scope(scope_id)
    assert len(items) == 1
    assert items[0]["id"] == search_id


def test_get_by_name_is_scope_aware(db_conn):
    """get_by_name only returns matches from the given scope."""
    scope_repo = ScopeRepo(db_conn)
    scope_a = scope_repo.create("a")
    scope_b = scope_repo.create("b")
    repo = SavedSearchRepo(db_conn)

    repo.create(scope_a, "same-name", "faith", "bible", None, None)
    row_b_id = repo.create(scope_b, "same-name", "hope", "bible", None, None)

    row_b = repo.get_by_name("same-name", scope_b)
    assert row_b is not None
    assert row_b["id"] == row_b_id
    assert row_b["query_text"] == "hope"


def test_delete_requires_id_and_scope_match(db_conn):
    """delete enforces scope ownership before removing rows."""
    scope_repo = ScopeRepo(db_conn)
    scope_a = scope_repo.create("a")
    scope_b = scope_repo.create("b")
    repo = SavedSearchRepo(db_conn)

    search_id = repo.create(scope_a, "to-delete", "grace", "bible", None, None)

    assert repo.delete(search_id, scope_b) is False
    assert repo.get(search_id) is not None

    assert repo.delete(search_id, scope_a) is True
    assert repo.get(search_id) is None
