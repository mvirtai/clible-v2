"""Tests for ScopeRepo."""

from clible.db.repositories.scope_repo import ScopeRepo


def test_create_and_get_roundtrip(db_conn):
    """create inserts scope and get returns it."""
    repo = ScopeRepo(db_conn)

    scope_id = repo.create("default")
    row = repo.get(scope_id)

    assert row is not None
    assert row["id"] == scope_id
    assert row["name"] == "default"
    assert "created_at" in row


def test_get_by_name_returns_none_for_missing(db_conn):
    """get_by_name returns None when scope does not exist."""
    repo = ScopeRepo(db_conn)
    assert repo.get_by_name("missing") is None


def test_get_by_name_returns_scope_when_exists(db_conn):
    """get_by_name resolves existing scope by name."""
    repo = ScopeRepo(db_conn)
    scope_id = repo.create("study-john")

    row = repo.get_by_name("study-john")

    assert row is not None
    assert row["id"] == scope_id


def test_list_all_orders_by_name(db_conn):
    """list_all returns scopes in ascending name order."""
    repo = ScopeRepo(db_conn)
    repo.create("zeta")
    repo.create("alpha")

    rows = repo.list_all()
    names = [row["name"] for row in rows]

    assert names == ["alpha", "zeta"]


def test_get_or_create_default_returns_existing_or_creates(db_conn):
    """get_or_create_default is idempotent."""
    repo = ScopeRepo(db_conn)

    first = repo.get_or_create_default()
    second = repo.get_or_create_default()

    assert first == second
