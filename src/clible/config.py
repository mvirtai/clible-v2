"""Application configuration.

All configurable values (paths, API settings, timeouts) are defined here.
Values are read from environment variables with sensible defaults; override
via CLIBLE_* env vars so the same code works in every environment:

- Dev: .env file loaded by the shell (e.g. direnv) or export in your profile.
- Test: Omit CLIBLE_* or set in pytest (e.g. CLIBLE_DB_PATH for a test DB).
- Docker: Pass -e CLIBLE_* or use env_file in compose/run.
"""

from pathlib import Path
from dataclasses import dataclass
import os


@dataclass
class Config:
    """Immutable configuration for the clible application.

    Attributes:
        db_path: Path to the SQLite database file. Defaults to data_dir/clible.db
            unless CLIBLE_DB_PATH is set.
        api_base_url: Base URL for the Bible API (e.g. bible-api.com).
        translations: List of translation codes to support (e.g. ["KJV", "ESV"]).
        data_dir: Directory for data files (exports, stop words). The default
            db_path is placed inside this directory.
        request_timeout: HTTP request timeout in seconds.
        request_delay: Delay in seconds between API calls (rate limiting).
    """

    db_path: Path
    api_base_url: str
    translations: list[str]
    data_dir: Path
    request_timeout: int
    request_delay: int


_default_data_dir = Path(__file__).resolve().parent / "data"
_data_dir = Path(os.environ.get("CLIBLE_DATA_DIR", str(_default_data_dir)))
_db_path = (
    Path(os.environ["CLIBLE_DB_PATH"])
    if "CLIBLE_DB_PATH" in os.environ
    else _data_dir / "clible.db"
)
_translations_raw = os.environ.get("CLIBLE_TRANSLATIONS", "KJV,ESV,NIV")
_translations = [s.strip() for s in _translations_raw.split(",") if s.strip()]

config = Config(
    db_path=_db_path,
    api_base_url=os.environ.get("CLIBLE_API_BASE_URL", "https://api.bible-api.com"),
    translations=_translations,
    data_dir=_data_dir,
    request_timeout=int(os.environ.get("CLIBLE_REQUEST_TIMEOUT", "10")),
    request_delay=int(os.environ.get("CLIBLE_REQUEST_DELAY", "1")),
)


def get_config() -> Config:
    """Return the global configuration instance.

    Use this instead of importing the config object directly so that
    tests or alternate entry points can inject a different config if needed.

    Returns:
        The application Config (paths, API URL, translations, timeouts).
    """
    return config
