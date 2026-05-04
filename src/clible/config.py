"""Application configuration.

All configurable values (paths, API settings, timeouts) are defined here.
"""

import os
from dataclasses import dataclass
from pathlib import Path

# -----------------------------
# CONFIG DATA MODEL
# -----------------------------


@dataclass
class Config:
    """Immutable configuration for the clible application.

    Attributes:
        db_path: Path to the SQLite database file. Defaults to data_dir/clible.db
            unless CLIBLE_DB_PATH is set.
        data_dir: Directory for data files (exports, stop words). The default
            db_path is placed inside this directory.
        request_timeout: HTTP request timeout in seconds for seed downloads.
            Set via CLIBLE_REQUEST_TIMEOUT; default 60.
        gcs_bucket: GCS bucket name for backup (optional). Set via CLIBLE_GCS_BUCKET.
        gcs_backup_prefix: Object name prefix for backups (e.g. backups). Set via
            CLIBLE_GCS_BACKUP_PREFIX; default backups.
        gcs_upload_timeout: Timeout in seconds for GCS upload (large DB or slow network).
            Set via CLIBLE_GCS_UPLOAD_TIMEOUT; default 300.
        seed_base_url: Optional base URL for seed XML; when set, seed uses
            seed_base_url + catalog filename instead of catalog url. Set via
            CLIBLE_SEED_BASE_URL.
        scope_name: Name of the current research context (scope).
            Set via CLIBLE_SCOPE; default 'default'.
        analytics_language: Language code for analytics stopword filtering (e.g. en, fi).
            Set via CLIBLE_ANALYTICS_LANGUAGE. When unset in the environment, commands
            may infer a language from the active translation (see analytics command).
        ui_language: Display language for localized book names in exports (en, fi).
            Set via CLIBLE_UI_LANGUAGE; default en.
    """

    db_path: Path
    data_dir: Path
    request_timeout: int
    gcs_bucket: str | None
    gcs_backup_prefix: str
    gcs_upload_timeout: int
    seed_base_url: str | None
    scope_name: str
    analytics_language: str
    ui_language: str


# -----------------------------
# PATH RESOLUTION
# -----------------------------

_default_data_dir = Path(__file__).resolve().parent / "data"

_data_dir = Path(os.environ.get("CLIBLE_DATA_DIR", str(_default_data_dir)))

_db_path = (
    Path(os.environ["CLIBLE_DB_PATH"])
    if "CLIBLE_DB_PATH" in os.environ
    else _data_dir / "clible.db"
)


# -----------------------------
# CONFIG INSTANCE
# -----------------------------

config = Config(
    db_path=_db_path,
    data_dir=_data_dir,
    request_timeout=int(os.environ.get("CLIBLE_REQUEST_TIMEOUT", "60")),
    gcs_bucket=os.environ.get("CLIBLE_GCS_BUCKET") or None,
    gcs_backup_prefix=os.environ.get("CLIBLE_GCS_BACKUP_PREFIX", "backups"),
    gcs_upload_timeout=int(os.environ.get("CLIBLE_GCS_UPLOAD_TIMEOUT", "300")),
    seed_base_url=os.environ.get("CLIBLE_SEED_BASE_URL") or None,
    scope_name=os.environ.get("CLIBLE_SCOPE", "default"),
    analytics_language=os.getenv("CLIBLE_ANALYTICS_LANGUAGE", "en"),
    ui_language=os.getenv("CLIBLE_UI_LANGUAGE", "en"),
)


def get_config() -> Config:
    """Return the global configuration instance."""
    return config
