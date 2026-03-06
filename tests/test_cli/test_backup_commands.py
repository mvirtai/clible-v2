"""CLI integration tests for backup commands."""

import tempfile
from pathlib import Path

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


def test_restore_gcs_help() -> None:
    """restore-gcs shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["backup", "restore-gcs", "--help"])
    assert result.exit_code == 0
    assert "restore" in result.output.lower()


def test_restore_gcs_replaces_db_and_keeps_backup(monkeypatch) -> None:
    """restore-gcs replaces the DB and stores the previous file as a backup."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "clible.db"
        db_path.write_text("old-db", encoding="utf-8")

        monkeypatch.setattr(config_module.config, "db_path", db_path)

        def fake_download_file(gcs_uri: str, local_path: Path) -> Path:
            assert gcs_uri == "gs://my-bucket/backups/clible.db"
            Path(local_path).write_text("new-db", encoding="utf-8")
            return Path(local_path)

        monkeypatch.setattr("clible.commands.backup.download_file", fake_download_file)
        monkeypatch.setattr(
            "clible.commands.backup._timestamp_for_backup",
            lambda: "20260306-180000",
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["backup", "restore-gcs", "gs://my-bucket/backups/clible.db", "--force"],
        )

        backup_path = db_path.with_name("clible.db.pre-restore-20260306-180000.bak")
        assert result.exit_code == 0
        assert db_path.read_text(encoding="utf-8") == "new-db"
        assert backup_path.read_text(encoding="utf-8") == "old-db"
        assert "GCS restore complete" in result.output


def test_restore_gcs_can_be_cancelled(monkeypatch) -> None:
    """restore-gcs aborts cleanly when the confirmation prompt is declined."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "clible.db"
        db_path.write_text("old-db", encoding="utf-8")

        monkeypatch.setattr(config_module.config, "db_path", db_path)

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["backup", "restore-gcs", "gs://my-bucket/backups/clible.db"],
            input="n\n",
        )

        assert result.exit_code == 1
        assert db_path.read_text(encoding="utf-8") == "old-db"
        assert "Restore aborted" in result.output
