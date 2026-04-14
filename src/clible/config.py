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
    """Immutable configuration for the clible application."""

    db_path: Path
    data_dir: Path
    request_timeout: int
    gcs_bucket: str | None
    gcs_backup_prefix: str
    gcs_upload_timeout: int
    seed_base_url: str | None
    scope_name: str

    # NEW 🔥
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
    # NEW
    analytics_language=os.getenv("CLIBLE_ANALYTICS_LANGUAGE", "en"),
    ui_language=os.getenv("CLIBLE_UI_LANGUAGE", "en"),
)


def get_config() -> Config:
    """Return the global configuration instance."""
    return config
