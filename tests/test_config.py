"""Tests for the configuration module."""

import importlib
import os

import pytest

# Import after we may have patched env, so we do a fresh import in the test.
import clible.config as config_module


def test_default_config_loads_correctly():
    """With no CLIBLE_* env vars set, get_config() returns defaults."""
    # Save and remove CLIBLE_* so module reload uses defaults.
    saved = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("CLIBLE_")}
    try:
        importlib.reload(config_module)
        cfg = config_module.get_config()
        assert cfg.api_base_url == "https://api.bible-api.com"
        assert cfg.request_timeout == 10
        assert cfg.request_delay == 1
        assert cfg.translations == ["KJV", "ESV", "NIV"]
        assert cfg.data_dir.name == "data"
        assert cfg.db_path.name == "clible.db"
        assert cfg.db_path.parent == cfg.data_dir
    finally:
        for k, v in saved.items():
            os.environ[k] = v
        importlib.reload(config_module)
