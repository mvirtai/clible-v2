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


def test_all_translations_have_required_keys():
    """Every entry in translations.json has the required keys."""
    path = DATA_DIR / "translations.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    required_keys = {"name", "language", "format", "filename", "url", "size_mb"}

    for tid, entry in data.items():
        for key in required_keys:
            assert key in entry, f"translation '{tid}' is missing key '{key}'"
        assert isinstance(entry["name"], str) and entry["name"], f"'{tid}' name is empty"
        assert isinstance(entry["language"], str) and entry["language"], (
            f"'{tid}' language is empty"
        )
        assert isinstance(entry["url"], str) and entry["url"].startswith("http"), (
            f"'{tid}' url looks invalid: {entry['url']!r}"
        )


def test_greek_translations_have_correct_language_codes():
    """Greek translation entries use 'grc' (ancient) or 'el' (modern), not 'en'."""
    path = DATA_DIR / "translations.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    ancient_greek_ids = {
        "greek",
        "greek1550",
        "greekbyz04",
        "greekbyz18",
        "greekelzevir",
        "greekf35",
        "greekfpb",
        "greekgnt",
        "greeklmgnt",
        "greekntv",
        "greeksblgnt",
        "greektcgnt",
        "greektgv",
        "greekthgnt",
        "greektr1894",
        "originalgreek",
    }
    modern_greek_ids = {"greekmodern1904", "greekmodernfpb"}

    for tid in ancient_greek_ids:
        assert data[tid]["language"] == "grc", (
            f"'{tid}' should have language='grc', got {data[tid]['language']!r}"
        )
    for tid in modern_greek_ids:
        assert data[tid]["language"] == "el", (
            f"'{tid}' should have language='el', got {data[tid]['language']!r}"
        )


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
