"""CLI integration tests for backup commands."""

import tempfile

from click.testing import CliRunner

from clible import config as config_module
from clible.cli import main


def test_backup_gcs_requires_bucket(monkeypatch) -> None:
    """backup gcs exits with error when CLIBLE_GCS_BUCKET is not set."""
    monkeypatch.setattr(config_module.config, "gcs_bucket", None)
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        monkeypatch.setattr(config_module.config, "db_path", f.name)
        runner = CliRunner()
        result = runner.invoke(main, ["backup", "gcs"])
    assert result.exit_code == 1
    assert "CLIBLE_GCS_BUCKET" in result.output


def test_backup_gcs_help() -> None:
    """backup gcs shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["backup", "gcs", "--help"])
    assert result.exit_code == 0
    assert "GCS" in result.output or "Google Cloud" in result.output
