"""Backup subcommands: GCS and other targets."""

import warnings

import click
from rich.console import Console
from rich.panel import Panel

from clible.config import get_config
from clible.storage.gcs import upload_file


def _timestamp_for_backup() -> str:
    """Return a timestamp string for backup object names (YYYYMMDD-HHMMSS)."""
    from datetime import datetime

    return datetime.now().strftime("%Y%m%d-%H%M%S")


@click.group("backup")
def backup() -> None:
    """Backup database and data to remote storage."""
    pass


@backup.command("gcs")
def backup_gcs() -> None:
    """Upload the SQLite database to Google Cloud Storage.

    Requires CLIBLE_GCS_BUCKET to be set. Optional: CLIBLE_GCS_BACKUP_PREFIX
    (default: backups). Uses Application Default Credentials or
    GOOGLE_APPLICATION_CREDENTIALS.
    """
    console = Console()
    cfg = get_config()
    if not cfg.gcs_bucket:
        console.print(
            Panel(
                "Backup to GCS requires CLIBLE_GCS_BUCKET to be set.\n"
                "Example: export CLIBLE_GCS_BUCKET=my-clible-bucket",
                title="[red]Missing configuration[/red]",
                border_style="red",
            )
        )
        raise SystemExit(1)

    if not cfg.db_path.exists():
        console.print(
            Panel(
                f"Database file not found: {cfg.db_path}",
                title="[red]File not found[/red]",
                border_style="red",
            )
        )
        raise SystemExit(1)

    prefix = (cfg.gcs_backup_prefix or "backups").strip("/")
    object_name = f"{prefix}/clible-{_timestamp_for_backup()}.db"
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=UserWarning,
                module="google.auth._default",
            )
            uri = upload_file(
                bucket_name=cfg.gcs_bucket,
                object_name=object_name,
                local_path=cfg.db_path,
            )
        console.print(
            Panel(
                f"Backup uploaded successfully.\n{uri}",
                title="[green]GCS backup complete[/green]",
                border_style="green",
            )
        )
    except Exception as e:
        hint = ""
        err_str = str(e).lower()
        if "invalid_grant" in err_str or "refresh" in err_str:
            hint = (
                "\n\nYour credentials may have expired. Re-authenticate with:\n"
                "  gcloud auth application-default login"
            )
        console.print(
            Panel(
                str(e) + hint,
                title="[red]GCS upload failed[/red]",
                border_style="red",
            )
        )
        raise SystemExit(1)
