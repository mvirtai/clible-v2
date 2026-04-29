"""Tests for SavedAnalysisRepo."""

from clible.db.repositories.saved_analysis_repo import SavedAnalysisRepo
from clible.db.repositories.scope_repo import ScopeRepo


def test_create_get_and_list_by_scope(db_conn):
    """create stores a row retrievable by id and scope listing."""
    scope_repo = ScopeRepo(db_conn)
    scope_id = scope_repo.create("default")
    repo = SavedAnalysisRepo(db_conn)

    analysis_id = repo.create(
        scope_id=scope_id,
        name="john-analysis",
        reference="John 1",
        analysis_type="chapter",
        translation_id=None,
        params_json='{"top_n": 10}',
    )

    row = repo.get(analysis_id)
    assert row is not None
    assert row["name"] == "john-analysis"
    assert row["reference"] == "John 1"
    assert row["analysis_type"] == "chapter"

    items = repo.list_by_scope(scope_id)
    assert len(items) == 1
    assert items[0]["id"] == analysis_id


def test_get_by_name_is_scope_aware(db_conn):
    """get_by_name only returns row from requested scope."""
    scope_repo = ScopeRepo(db_conn)
    scope_a = scope_repo.create("a")
    scope_b = scope_repo.create("b")
    repo = SavedAnalysisRepo(db_conn)

    repo.create(scope_a, "same-name", "John 1", "reference", None, None)
    row_b_id = repo.create(scope_b, "same-name", "John 3:16", "reference", None, None)

    row_b = repo.get_by_name("same-name", scope_b)
    assert row_b is not None
    assert row_b["id"] == row_b_id
    assert row_b["reference"] == "John 3:16"


def test_delete_requires_id_and_scope_match(db_conn):
    """delete enforces scope match before deleting."""
    scope_repo = ScopeRepo(db_conn)
    scope_a = scope_repo.create("a")
    scope_b = scope_repo.create("b")
    repo = SavedAnalysisRepo(db_conn)

    analysis_id = repo.create(scope_a, "to-delete", "John 1", "reference", None, None)

    assert repo.delete(analysis_id, scope_b) is False
    assert repo.get(analysis_id) is not None

    assert repo.delete(analysis_id, scope_a) is True
    assert repo.get(analysis_id) is None
