"""Tests for static data files (translations.json, progress_quotes.json).

Verifies JSON validity and expected structure. Prevents accidental breakage.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "clible" / "data"


def test_translations_json_loads_and_has_expected_structure():
    """translations.json is valid and contains expected entries with required keys."""
    path = DATA_DIR / "translations.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    assert isinstance(data, dict)
    required_ids = {"web", "kjv", "fin-biblia-33-38", "fin-1992"}
    required_keys = {"name", "language", "format", "filename", "url", "size_mb"}

    for tid in required_ids:
        assert tid in data, f"translation {tid} missing"
        entry = data[tid]
        for key in required_keys:
            assert key in entry, f"translation {tid} missing key {key}"

    assert data["web"]["format"] == "USFX"
    assert data["web"]["language"] == "en"
    assert "open-bibles" in data["web"]["url"]
    assert data["fin-1992"]["format"] == "BEBLIA"
    assert "Beblia" in data["fin-1992"]["url"]


def test_progress_quotes_json_loads_and_has_expected_structure():
    """progress_quotes.json is valid and each entry has text and reference."""
    path = DATA_DIR / "progress_quotes.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    assert isinstance(data, list)
    assert len(data) >= 1
    for item in data:
        assert "text" in item
        assert "reference" in item
        assert isinstance(item["text"], str)
        assert isinstance(item["reference"], str)
