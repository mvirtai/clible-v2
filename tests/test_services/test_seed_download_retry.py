"""Tests for _download_xml retry behaviour (tenacity + requests)."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from clible.services.seed_service import _download_xml


@pytest.fixture(autouse=True)
def _no_tenacity_sleep(monkeypatch):
    """Skip real waits between retries so tests stay fast."""
    import time

    monkeypatch.setattr(time, "sleep", lambda _s: None)


class TestDownloadXmlRetry:
    """_download_xml retries on transient failures."""

    def test_succeeds_on_second_attempt(self) -> None:
        good_response = MagicMock()
        good_response.content = b"<xml/>"
        good_response.raise_for_status = MagicMock()

        with patch("clible.services.seed_service.requests.get") as mock_get:
            mock_get.side_effect = [
                requests.exceptions.ConnectionError("network blip"),
                good_response,
            ]
            result = _download_xml("https://example.com/bible.xml", timeout=5)

        assert result == b"<xml/>"
        assert mock_get.call_count == 2

    def test_raises_after_three_failed_attempts(self) -> None:
        with patch("clible.services.seed_service.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("down")

            with pytest.raises(requests.exceptions.ConnectionError):
                _download_xml("https://example.com/bible.xml", timeout=5)

        assert mock_get.call_count == 3

    def test_retries_on_http_500(self) -> None:
        bad_response = MagicMock()
        bad_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=500)
        )

        with patch("clible.services.seed_service.requests.get") as mock_get:
            mock_get.return_value = bad_response

            with pytest.raises(requests.exceptions.HTTPError):
                _download_xml("https://example.com/bible.xml", timeout=5)

        assert mock_get.call_count == 3
