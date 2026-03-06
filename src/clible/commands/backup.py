"""Backup subcommands: GCS and other targets."""

import tempfile
import warnings
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from clible.config import get_config
from clible.storage.gcs import download_file, upload_file


def _timestamp_for_backup() -> str:
    """Return a timestamp string for backup object names (YYYYMMDD-HHMMSS)."""
    from datetime import datetime

    return datetime.now().strftime("%Y%m%d-%H%M%S")


@click.group("backup")
def backup() -> None:
    """Backup database and data to remote storage."""
    pass


def _db_path() -> Path:
    """Return the configured database path as a Path instance."""
    return Path(get_config().db_path)


def _gcs_error_hint(error: Exception) -> str:
    """Return extra troubleshooting text for common GCS auth failures."""
    err_str = str(error).lower()
    if "invalid_grant" in err_str or "refresh" in err_str:
        return (
            "\n\nYour credentials may have expired. Re-authenticate with:\n"
            "  gcloud auth application-default login"
        )
    return ""


@backup.command("gcs")
def backup_gcs() -> None:
    """Upload the SQLite database to Google Cloud Storage.

    Requires CLIBLE_GCS_BUCKET to be set. Optional: CLIBLE_GCS_BACKUP_PREFIX
    (default: backups). Uses Application Default Credentials or
    GOOGLE_APPLICATION_CREDENTIALS.
    """
    console = Console()
    cfg = get_config()
    db_path = _db_path()
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

    if not db_path.exists():
        console.print(
            Panel(
                f"Database file not found: {db_path}",
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
                local_path=db_path,
            )
        console.print(
            Panel(
                f"Backup uploaded successfully.\n{uri}",
                title="[green]GCS backup complete[/green]",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(
            Panel(
                str(e) + _gcs_error_hint(e),
                title="[red]GCS upload failed[/red]",
                border_style="red",
            )
        )
        raise SystemExit(1)


@backup.command("restore-gcs")
@click.argument("gcs_uri")
@click.option(
    "--force",
    is_flag=True,
    help="Skip the confirmation prompt before replacing the local database.",
)
def restore_gcs(gcs_uri: str, force: bool) -> None:
    """Restore the local SQLite database from a GCS object.

    Downloads the remote database to a temporary file, writes a local backup of
    the current database (if present), and then replaces the configured DB file.
    """
    console = Console()
    db_path = _db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not force:
        confirmed = click.confirm(
            f"This will replace the local database at '{db_path}'. Continue?",
            default=False,
        )
        if not confirmed:
            console.print(
                Panel(
                    "Restore cancelled. Local database was not changed.",
                    title="[yellow]Restore aborted[/yellow]",
                    border_style="yellow",
                )
            )
            raise SystemExit(1)

    temp_path: Path | None = None
    backup_path: Path | None = None
    timestamp = _timestamp_for_backup()

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".db",
            prefix="clible-restore-",
            dir=db_path.parent,
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=UserWarning,
                module="google.auth._default",
            )
            download_file(gcs_uri, temp_path)

        if db_path.exists():
            backup_path = db_path.with_name(f"{db_path.name}.pre-restore-{timestamp}.bak")
            db_path.replace(backup_path)

        temp_path.replace(db_path)

        message = f"Database restored successfully from:\n{gcs_uri}\n\nLocal path:\n{db_path}"
        if backup_path is not None:
            message += f"\n\nPrevious database backup:\n{backup_path}"

        console.print(
            Panel(
                message,
                title="[green]GCS restore complete[/green]",
                border_style="green",
            )
        )
    except Exception as e:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
        if backup_path is not None and backup_path.exists() and not db_path.exists():
            backup_path.replace(db_path)

        console.print(
            Panel(
                str(e) + _gcs_error_hint(e),
                title="[red]GCS restore failed[/red]",
                border_style="red",
            )
        )
        raise SystemExit(1)
