"""Tests for _fetch_github_tree retry behaviour (tenacity + requests)."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from clible.services.translation_catalog_sync import (
    TranslationCatalogSyncError,
    _fetch_github_tree,
)


@pytest.fixture(autouse=True)
def _no_tenacity_sleep(monkeypatch):
    import time

    monkeypatch.setattr(time, "sleep", lambda _s: None)


def _valid_tree_response() -> MagicMock:
    r = MagicMock()
    r.raise_for_status = MagicMock()
    r.json.return_value = {"tree": [{"type": "blob", "path": "eng-web.usfx.xml", "size": 100}]}
    return r


class TestFetchGithubTreeRetry:
    def test_succeeds_on_second_attempt(self) -> None:
        good = _valid_tree_response()
        with patch("clible.services.translation_catalog_sync.requests.get") as mock_get:
            mock_get.side_effect = [
                requests.exceptions.ConnectionError("blip"),
                good,
            ]
            out = _fetch_github_tree(
                owner="o",
                repo="r",
                ref="master",
                github_token=None,
                timeout_seconds=30,
            )
        assert mock_get.call_count == 2
        assert isinstance(out, list)
        assert out[0]["path"] == "eng-web.usfx.xml"

    def test_raises_after_three_connection_errors(self) -> None:
        with patch("clible.services.translation_catalog_sync.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("down")
            with pytest.raises(requests.exceptions.ConnectionError):
                _fetch_github_tree(
                    owner="o",
                    repo="r",
                    ref="master",
                    github_token=None,
                    timeout_seconds=30,
                )
        assert mock_get.call_count == 3

    def test_invalid_payload_not_retried(self) -> None:
        """Shape errors become TranslationCatalogSyncError without HTTP retry."""
        bad = MagicMock()
        bad.raise_for_status = MagicMock()
        bad.json.return_value = {"not_tree": True}
        with patch(
            "clible.services.translation_catalog_sync.requests.get",
            return_value=bad,
        ) as mock_get:
            with pytest.raises(TranslationCatalogSyncError):
                _fetch_github_tree(
                    owner="seven1m",
                    repo="open-bibles",
                    ref="master",
                    github_token=None,
                    timeout_seconds=30,
                )
        assert mock_get.call_count == 1
