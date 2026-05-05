"""Focused tests for analysis export serializers."""

import json

from clible.ui.export.analysis import export_analysis


def _analysis_payload() -> dict:
    return {
        "token_count": 10,
        "unique_token_count": 6,
        "type_token_ratio": 0.6,
        "character_count": 42,
        "avg_word_length": 4.2,
        "top_words": [("grace", 3), ("peace", 2)],
        "top_bigrams": [("in christ", 2)],
        "top_trigrams": [("peace be with", 1)],
    }


def test_export_analysis_json_contains_ranked_lists():
    out = export_analysis(_analysis_payload(), scope_label="John 1:1", format="json")
    data = json.loads(out)
    assert data["type"] == "analysis"
    assert data["scope"] == "John 1:1"
    assert data["top_words"][0] == {"word": "grace", "count": 3}
    assert data["top_bigrams"][0]["bigram"] == "in christ"
    assert data["top_trigrams"][0]["trigram"] == "peace be with"


def test_export_analysis_csv_has_unified_header_and_sections():
    out = export_analysis(_analysis_payload(), scope_label="John 1:1", format="csv")
    lines = [ln.strip("\r") for ln in out.strip().split("\n")]
    assert lines[0] == "section,metric,rank,token,count"
    assert any("metrics,token_count,,,10" in ln for ln in lines)
    assert any("top_words,,1,grace,3" in ln for ln in lines)
    assert any("top_bigrams,,1,in christ,2" in ln for ln in lines)
    assert any("top_trigrams,,1,peace be with,1" in ln for ln in lines)


def test_export_analysis_md_fallback_includes_tables():
    out = export_analysis(_analysis_payload(), scope_label="Psalm 1:1", format="md")
    assert out.startswith("# Text Analysis: Psalm 1:1")
    assert "## Metrics" in out
    assert "## Top Words" in out
    assert "| Rank | Word | Count |" in out


def test_export_analysis_txt_includes_sections_when_rows_exist():
    out = export_analysis(_analysis_payload(), scope_label="Psalm 1:1", format="txt")
    assert "Text analysis: Psalm 1:1" in out
    assert "Top words" in out
    assert "Top bigrams" in out
    assert "Top trigrams" in out


def test_export_analysis_xml_contains_metrics_and_ranked_nodes():
    out = export_analysis(_analysis_payload(), scope_label="Psalm 1:1", format="xml")
    assert '<?xml version="1.0" encoding="UTF-8"?>' in out
    assert '<analysis type="token-stats">' in out
    assert '<metric name="token_count">10</metric>' in out
    assert '<top_words>' in out
    assert '<item rank="1" count="3">grace</item>' in out


def test_export_analysis_html_handles_scope_acronym(monkeypatch):
    monkeypatch.setattr(
        "clible.ui.export.analysis.parse_and_format_scope",
        lambda _: ("John 3:16", "(JHN 3:16)"),
    )
    out = export_analysis(_analysis_payload(), scope_label="JHN 3:16", format="html")
    assert "<h1>John 3:16</h1>" in out
    assert "title-acronym" in out
    assert "(JHN 3:16)" in out
    assert "<h2>Top Words</h2>" in out


def test_export_analysis_html_skips_token_sections_when_empty():
    minimal = {
        "token_count": 1,
        "unique_token_count": 1,
        "type_token_ratio": 1.0,
        "character_count": 3,
        "avg_word_length": 3.0,
        "top_words": [],
        "top_bigrams": [],
        "top_trigrams": [],
    }
    out = export_analysis(minimal, scope_label="GEN 1:1", format="html")
    assert "<h2>Key metrics</h2>" in out
    assert "<h2>Top Words</h2>" not in out
    assert "<h2>Top Bigrams</h2>" not in out
    assert "<h2>Top Trigrams</h2>" not in out

