"""Tests for SavedSearchService."""

import pytest

from clible.services.saved_search_service import SavedSearchService


def test_save_search_uses_current_scope_and_repo_create(mocker):
    """save_search delegates to repo.create with resolved scope id."""
    repo = mocker.Mock()
    repo.create.return_value = "search-1"
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    verse_service = mocker.Mock()

    service = SavedSearchService(
        saved_search_repo=repo,
        scope_service=scope_service,
        verse_service=verse_service,
    )

    search_id = service.save_search("grace-search", "grace", "book", "John", "web")

    assert search_id == "search-1"
    repo.create.assert_called_once_with("scope-1", "grace-search", "grace", "book", "John", "web")


def test_list_saved_searches_uses_scope_id(mocker):
    """list_saved_searches returns list_by_scope output."""
    repo = mocker.Mock()
    repo.list_by_scope.return_value = [{"id": "search-1", "scope_id": "scope-1"}]
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    verse_service = mocker.Mock()
    service = SavedSearchService(repo, scope_service, verse_service)

    result = service.list_saved_searches()

    assert len(result) == 1
    repo.list_by_scope.assert_called_once_with("scope-1")


def test_get_and_run_finds_by_id_and_executes_search(mocker):
    """get_and_run loads saved search by id and re-runs verse search."""
    saved = {
        "id": "search-1",
        "scope_id": "scope-1",
        "name": "grace-search",
        "query_text": "grace",
        "search_scope": "book",
        "scope_value": "John",
        "translation_id": "web",
        "created_at": "2026-01-01 00:00:00",
    }
    repo = mocker.Mock()
    repo.get.return_value = saved
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    verse_service = mocker.Mock()
    verse_service.search_text.return_value = [{"book_id": "JHN", "chapter": 1, "verse": 1}]

    service = SavedSearchService(repo, scope_service, verse_service)

    loaded, verses = service.get_and_run("search-1")

    assert loaded["id"] == "search-1"
    assert len(verses) == 1
    verse_service.search_text.assert_called_once_with(
        word="grace",
        translation_id="web",
        scope="book",
        scope_ref="John",
    )


def test_get_and_run_falls_back_to_name_lookup(mocker):
    """get_and_run tries name lookup when id lookup is missing/wrong scope."""
    by_name_saved = {
        "id": "search-2",
        "scope_id": "scope-1",
        "name": "mercy-search",
        "query_text": "mercy",
        "search_scope": "bible",
        "scope_value": None,
        "translation_id": None,
        "created_at": "2026-01-01 00:00:00",
    }
    repo = mocker.Mock()
    repo.get.return_value = {"id": "other", "scope_id": "other-scope"}
    repo.get_by_name.return_value = by_name_saved
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    verse_service = mocker.Mock()
    verse_service.search_text.return_value = []

    service = SavedSearchService(repo, scope_service, verse_service)

    loaded, _ = service.get_and_run("mercy-search")

    assert loaded["name"] == "mercy-search"
    repo.get_by_name.assert_called_once_with("mercy-search", "scope-1")


def test_get_and_run_raises_when_not_found(mocker):
    """get_and_run raises ValueError when search not found in scope."""
    repo = mocker.Mock()
    repo.get.return_value = None
    repo.get_by_name.return_value = None
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    verse_service = mocker.Mock()

    service = SavedSearchService(repo, scope_service, verse_service)

    with pytest.raises(ValueError, match="not found in current scope"):
        service.get_and_run("missing")


def test_delete_saved_search_deletes_by_id_or_name(mocker):
    """delete_saved_search tries id first, then name-based delete fallback."""
    repo = mocker.Mock()
    repo.delete.side_effect = [False, True]
    repo.get_by_name.return_value = {
        "id": "search-3",
        "scope_id": "scope-1",
        "name": "hope-search",
        "query_text": "hope",
        "search_scope": "bible",
        "scope_value": None,
        "translation_id": None,
        "created_at": "2026-01-01 00:00:00",
    }
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    verse_service = mocker.Mock()

    service = SavedSearchService(repo, scope_service, verse_service)

    deleted = service.delete_saved_search("hope-search")

    assert deleted is True
    assert repo.delete.call_count == 2
