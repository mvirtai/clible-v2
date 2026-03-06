"""Tests for GCS storage helpers."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from clible.storage.gcs import download_file, parse_gcs_uri, upload_file


@patch("clible.storage.gcs.Client")
def test_upload_file_calls_client_and_upload(mock_client: MagicMock) -> None:
    """upload_file creates a client, gets bucket and blob, uploads from path."""
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    try:
        uri = upload_file(
            bucket_name="my-bucket",
            object_name="backups/clible-20250306-120000.db",
            local_path=path,
        )
        assert uri == "gs://my-bucket/backups/clible-20250306-120000.db"
        mock_client.return_value.bucket.assert_called_once_with("my-bucket")
        mock_bucket.blob.assert_called_once_with("backups/clible-20250306-120000.db")
        mock_blob.upload_from_filename.assert_called_once_with(str(path))
    finally:
        path.unlink()


def test_upload_file_raises_when_file_missing() -> None:
    """upload_file raises FileNotFoundError when local path does not exist."""
    with pytest.raises(FileNotFoundError, match="Local file not found"):
        upload_file(
            bucket_name="my-bucket",
            object_name="backups/clible.db",
            local_path=Path("/nonexistent/clible.db"),
        )


def test_parse_gcs_uri_returns_bucket_and_object() -> None:
    """parse_gcs_uri splits a valid gs:// URI into bucket and object path."""
    assert parse_gcs_uri("gs://my-bucket/backups/clible.db") == (
        "my-bucket",
        "backups/clible.db",
    )


def test_parse_gcs_uri_raises_for_invalid_uri() -> None:
    """parse_gcs_uri rejects malformed GCS URIs."""
    with pytest.raises(ValueError, match="gs://"):
        parse_gcs_uri("https://storage.googleapis.com/my-bucket/clible.db")


@patch("clible.storage.gcs.Client")
def test_download_file_calls_client_and_download(mock_client: MagicMock) -> None:
    """download_file resolves the blob and downloads it to local disk."""
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    with tempfile.TemporaryDirectory() as temp_dir:
        destination = Path(temp_dir) / "restored.db"
        result = download_file("gs://my-bucket/backups/clible.db", destination)

    assert result == destination
    mock_client.return_value.bucket.assert_called_once_with("my-bucket")
    mock_bucket.blob.assert_called_once_with("backups/clible.db")
    mock_blob.download_to_filename.assert_called_once_with(str(destination))
