"""Tests for ScopeService."""

from unittest.mock import Mock

from clible.services.scope_service import ScopeService


def test_get_current_scope_id_returns_existing_id():
    """get_current_scope_id returns id when scope already exists."""
    scope_repo = Mock()
    scope_repo.get_by_name.return_value = {
        "id": "scope-1",
        "name": "default",
        "created_at": "2026-01-01 00:00:00",
    }
    config = Mock()
    config.scope_name = "default"

    service = ScopeService(scope_repo=scope_repo, config=config)

    scope_id = service.get_current_scope_id()

    assert scope_id == "scope-1"
    scope_repo.create.assert_not_called()


def test_get_current_scope_id_creates_scope_when_missing():
    """get_current_scope_id bootstraps scope if not present."""
    scope_repo = Mock()
    scope_repo.get_by_name.return_value = None
    scope_repo.create.return_value = "new-scope-id"
    config = Mock()
    config.scope_name = "study-paul"

    service = ScopeService(scope_repo=scope_repo, config=config)

    scope_id = service.get_current_scope_id()

    assert scope_id == "new-scope-id"
    scope_repo.create.assert_called_once_with("study-paul")


def test_list_scopes_delegates_to_repo():
    """list_scopes returns repository list_all output."""
    scope_repo = Mock()
    expected = [{"id": "scope-1", "name": "default", "created_at": "2026-01-01 00:00:00"}]
    scope_repo.list_all.return_value = expected
    config = Mock()
    config.scope_name = "default"

    service = ScopeService(scope_repo=scope_repo, config=config)

    assert service.list_scopes() == expected


def test_create_scope_returns_existing_id_when_name_exists():
    """create_scope returns existing id without creating a new row."""
    scope_repo = Mock()
    scope_repo.get_by_name.return_value = {
        "id": "scope-1",
        "name": "default",
        "created_at": "2026-01-01 00:00:00",
    }
    config = Mock()
    config.scope_name = "default"

    service = ScopeService(scope_repo=scope_repo, config=config)

    scope_id = service.create_scope("default")

    assert scope_id == "scope-1"
    scope_repo.create.assert_not_called()


def test_create_scope_creates_new_scope_when_not_found():
    """create_scope creates and returns id when name does not exist."""
    scope_repo = Mock()
    scope_repo.get_by_name.return_value = None
    scope_repo.create.return_value = "scope-2"
    config = Mock()
    config.scope_name = "default"

    service = ScopeService(scope_repo=scope_repo, config=config)

    scope_id = service.create_scope("study-john")

    assert scope_id == "scope-2"
    scope_repo.create.assert_called_once_with("study-john")
