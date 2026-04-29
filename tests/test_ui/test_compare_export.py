"""Unit tests for translation comparison export serializers."""

import json

from clible.ui.export.compare import export_compare


def _sample_comparison() -> dict:
    return {
        "reference": "John 3:16",
        "translation_a": "web",
        "translation_b": "kjv",
        "summary": {
            "total_verses": 1,
            "fully_aligned_verses": 1,
            "exact_matches": 0,
            "exact_match_ratio": 0.0,
            "average_similarity": 0.84,
            "top_shared_words": [("god", 1), ("world", 1)],
            "most_similar_verse": {"book_id": "JHN", "chapter": 3, "verse": 16},
        },
        "aligned_verses": [
            {
                "book_id": "JHN",
                "chapter": 3,
                "verse": 16,
                "text_a": "For God so loved the world",
                "text_b": "For God so loved the world",
                "similarity": 1.0,
                "exact_match": True,
            }
        ],
    }


def test_export_compare_json_structure():
    result = export_compare(_sample_comparison(), format="json")
    payload = json.loads(result)
    assert payload["type"] == "compare"
    assert payload["reference"] == "John 3:16"
    assert len(payload["aligned_verses"]) == 1


def test_export_compare_csv_contains_summary_and_verses():
    result = export_compare(_sample_comparison(), format="csv")
    lines = [line.rstrip("\r") for line in result.strip().split("\n")]
    assert lines[0].startswith("section,metric,value,book_id")
    assert any("summary,total_verses,1" in line for line in lines)
    assert any("aligned_verses,,,JHN,3,16" in line for line in lines)


def test_export_compare_txt_has_sections():
    result = export_compare(_sample_comparison(), format="txt")
    assert "Translation comparison: John 3:16" in result
    assert "Summary" in result
    assert "Aligned verses" in result
    assert "similarity:" in result


def test_export_compare_xml_has_expected_nodes():
    result = export_compare(_sample_comparison(), format="xml")
    assert '<?xml version="1.0"' in result
    assert "<comparison type=\"translation-compare\">" in result
    assert "<reference>John 3:16</reference>" in result
    assert "<aligned-verses>" in result


def test_export_compare_md_fallback_and_table():
    result = export_compare(_sample_comparison(), format="md")
    assert result.startswith("# Translation Comparison: John 3:16")
    assert "## Similarity Summary" in result
    assert "| Verse | Left | Right | Similarity |" in result


def test_export_compare_html_contains_translations_and_verse_pair():
    result = export_compare(_sample_comparison(), format="html")
    assert "<!doctype html>" in result.lower()
    assert "Translation comparison" in result
    assert "John 3:16" in result
    assert "Aligned verses" in result
