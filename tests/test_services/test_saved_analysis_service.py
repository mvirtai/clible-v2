"""Tests for SavedAnalysisService."""

import pytest

from clible.services.saved_analysis_service import SavedAnalysisService


def test_save_analysis_serializes_params_and_saves(mocker):
    """save_analysis serializes params JSON before repository create."""
    repo = mocker.Mock()
    repo.create.return_value = "analysis-1"
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    analytic_service = mocker.Mock()
    service = SavedAnalysisService(repo, scope_service, analytic_service)

    analysis_id = service.save_analysis(
        name="top-words",
        reference="John 1",
        analysis_type="chapter",
        translation_id="web",
        params={"top_n": 10},
    )

    assert analysis_id == "analysis-1"
    create_args = repo.create.call_args[0]
    assert create_args[:5] == ("scope-1", "top-words", "John 1", "chapter", "web")
    assert '"top_n": 10' in create_args[5]


def test_list_saved_analyses_uses_scope_id(mocker):
    """list_saved_analyses returns repository rows for current scope."""
    repo = mocker.Mock()
    repo.list_by_scope.return_value = [{"id": "analysis-1", "scope_id": "scope-1"}]
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    analytic_service = mocker.Mock()
    service = SavedAnalysisService(repo, scope_service, analytic_service)

    result = service.list_saved_analyses()

    assert len(result) == 1
    repo.list_by_scope.assert_called_once_with("scope-1")


@pytest.mark.parametrize("analysis_type", ["reference", "chapter", "book"])
def test_get_and_run_reference_like_types_call_analyze_reference(mocker, analysis_type):
    """reference/chapter/book types call analyze_reference."""
    saved = {
        "id": "analysis-1",
        "scope_id": "scope-1",
        "name": "my-analysis",
        "reference": "John 1",
        "analysis_type": analysis_type,
        "translation_id": "web",
        "params_json": '{"top_n": 5}',
        "created_at": "2026-01-01 00:00:00",
    }
    repo = mocker.Mock()
    repo.get.return_value = saved
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    analytic_service = mocker.Mock()
    analytic_service.analyze_reference.return_value = {"ok": True}
    service = SavedAnalysisService(repo, scope_service, analytic_service)

    loaded, result = service.get_and_run("analysis-1")

    assert loaded["id"] == "analysis-1"
    assert result["ok"] is True
    analytic_service.analyze_reference.assert_called_once_with("John 1", "web", top_n=5)


def test_get_and_run_compare_calls_compare_translations(mocker):
    """compare type calls compare_translations with translation_b from params."""
    saved = {
        "id": "analysis-2",
        "scope_id": "scope-1",
        "name": "cmp",
        "reference": "John 3:16",
        "analysis_type": "compare",
        "translation_id": "web",
        "params_json": '{"translation_b": "kjv"}',
        "created_at": "2026-01-01 00:00:00",
    }
    repo = mocker.Mock()
    repo.get.return_value = saved
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    analytic_service = mocker.Mock()
    analytic_service.compare_translations.return_value = {"diff_count": 3}
    service = SavedAnalysisService(repo, scope_service, analytic_service)

    _, result = service.get_and_run("analysis-2")

    assert result["diff_count"] == 3
    analytic_service.compare_translations.assert_called_once_with("John 3:16", "web", "kjv")


def test_get_and_run_compare_raises_without_translation_b(mocker):
    """compare type requires translation_b parameter."""
    saved = {
        "id": "analysis-2",
        "scope_id": "scope-1",
        "name": "cmp",
        "reference": "John 3:16",
        "analysis_type": "compare",
        "translation_id": "web",
        "params_json": "{}",
        "created_at": "2026-01-01 00:00:00",
    }
    repo = mocker.Mock()
    repo.get.return_value = saved
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    analytic_service = mocker.Mock()
    service = SavedAnalysisService(repo, scope_service, analytic_service)

    with pytest.raises(ValueError, match="missing 'translation_b' parameter"):
        service.get_and_run("analysis-2")


def test_get_and_run_raises_on_unknown_analysis_type(mocker):
    """unknown analysis_type raises a clear ValueError."""
    saved = {
        "id": "analysis-3",
        "scope_id": "scope-1",
        "name": "unknown",
        "reference": "John 1",
        "analysis_type": "something-else",
        "translation_id": None,
        "params_json": None,
        "created_at": "2026-01-01 00:00:00",
    }
    repo = mocker.Mock()
    repo.get.return_value = saved
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    analytic_service = mocker.Mock()
    service = SavedAnalysisService(repo, scope_service, analytic_service)

    with pytest.raises(ValueError, match="Unsupported analysis type"):
        service.get_and_run("analysis-3")


def test_get_and_run_raises_when_not_found(mocker):
    """missing identifier raises not found ValueError."""
    repo = mocker.Mock()
    repo.get.return_value = None
    repo.get_by_name.return_value = None
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    analytic_service = mocker.Mock()
    service = SavedAnalysisService(repo, scope_service, analytic_service)

    with pytest.raises(ValueError, match="not found in current scope"):
        service.get_and_run("missing")


def test_delete_saved_analysis_deletes_by_id_or_name(mocker):
    """delete_saved_analysis tries id then name fallback."""
    repo = mocker.Mock()
    repo.delete.side_effect = [False, True]
    repo.get_by_name.return_value = {
        "id": "analysis-4",
        "scope_id": "scope-1",
        "name": "fallback",
        "reference": "John 1",
        "analysis_type": "reference",
        "translation_id": None,
        "params_json": None,
        "created_at": "2026-01-01 00:00:00",
    }
    scope_service = mocker.Mock()
    scope_service.get_current_scope_id.return_value = "scope-1"
    analytic_service = mocker.Mock()
    service = SavedAnalysisService(repo, scope_service, analytic_service)

    deleted = service.delete_saved_analysis("fallback")

    assert deleted is True
    assert repo.delete.call_count == 2
