"""Application configuration.

All configurable values (paths, API settings, timeouts) are defined here.
Values are read from environment variables with sensible defaults; override
via CLIBLE_* env vars so the same code works in every environment:

- Dev: .env file loaded by the shell (e.g. direnv) or export in your profile.
- Test: Omit CLIBLE_* or set in pytest (e.g. CLIBLE_DB_PATH for a test DB).
- Docker: Pass -e CLIBLE_* or use env_file in compose/run.
"""

import os
from dataclasses import dataclass
from pathlib import Path


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
        analytics_language: Language code used for stopword filtering in analytics.
            Defaults to 'en' regardless of the Bible text translation's language,
            so the CLI interface and insights remain in English even when studying
            Greek or other non-English translations. Set via CLIBLE_ANALYTICS_LANGUAGE.
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


_default_data_dir = Path(__file__).resolve().parent / "data"
_data_dir = Path(os.environ.get("CLIBLE_DATA_DIR", str(_default_data_dir)))
_db_path = (
    Path(os.environ["CLIBLE_DB_PATH"])
    if "CLIBLE_DB_PATH" in os.environ
    else _data_dir / "clible.db"
)

config = Config(
    db_path=_db_path,
    data_dir=_data_dir,
    request_timeout=int(os.environ.get("CLIBLE_REQUEST_TIMEOUT", "60")),
    gcs_bucket=os.environ.get("CLIBLE_GCS_BUCKET") or None,
    gcs_backup_prefix=os.environ.get("CLIBLE_GCS_BACKUP_PREFIX", "backups"),
    gcs_upload_timeout=int(os.environ.get("CLIBLE_GCS_UPLOAD_TIMEOUT", "300")),
    seed_base_url=os.environ.get("CLIBLE_SEED_BASE_URL") or None,
    scope_name=os.environ.get("CLIBLE_SCOPE", "default"),
    analytics_language=os.environ.get("CLIBLE_ANALYTICS_LANGUAGE", "en"),
)


def get_config() -> Config:
    """Return the global configuration instance.

    Use this instead of importing the config object directly so that
    tests or alternate entry points can inject a different config if needed.

    Returns:
        The application Config (paths, API URL, translations, timeouts).
    """
    return config
