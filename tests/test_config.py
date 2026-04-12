"""Tests for the configuration module."""

import importlib
import os

# Import as module (not individual objects) so we can reload() it in tests.
import clible.config as config_module


def test_default_config_loads_correctly():
    """With no CLIBLE_* env vars set, get_config() returns defaults."""
    # Save and remove CLIBLE_* so module reload uses defaults.
    saved = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("CLIBLE_")}
    try:
        importlib.reload(config_module)
        cfg = config_module.get_config()
        assert cfg.request_timeout == 60
        assert cfg.data_dir.name == "data"
        assert cfg.db_path.name == "clible.db"
        assert cfg.db_path.parent == cfg.data_dir
        assert cfg.gcs_bucket is None
        assert cfg.gcs_backup_prefix == "backups"
        assert cfg.gcs_upload_timeout == 300
        assert cfg.seed_base_url is None
        assert cfg.analytics_language == "en"
    finally:
        for k, v in saved.items():
            os.environ[k] = v
        importlib.reload(config_module)


def test_analytics_language_env_var_overrides_default():
    """CLIBLE_ANALYTICS_LANGUAGE overrides the default 'en' analytics language."""
    saved = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("CLIBLE_")}
    try:
        os.environ["CLIBLE_ANALYTICS_LANGUAGE"] = "grc"
        importlib.reload(config_module)
        cfg = config_module.get_config()
        assert cfg.analytics_language == "grc"
    finally:
        for k, v in saved.items():
            os.environ[k] = v
        os.environ.pop("CLIBLE_ANALYTICS_LANGUAGE", None)
        importlib.reload(config_module)
