"""Token analysis result serialization (analytics export)."""

from __future__ import annotations

import csv
import html
import io
import json
import xml.etree.ElementTree as ET
from typing import Any

from clible.ui.export.html_document import render_html_document
from clible.ui.export.io import validate_export_format
from clible.ui.export.scope import parse_and_format_scope
from clible.ui.export.shared import stringify_number, xml_document


def export_analysis(analysis: dict[str, Any], *, scope_label: str, format: str) -> str:
    """Export a token-based analysis dictionary.

    Args:
        analysis: Result of ``AnalyticService.analyze_reference/analyze_chapter/analyze_book``.
        scope_label: Human-readable scope string (e.g. ``"John 3:16-18"``).
        format: Output format string (``json``/``csv``/``html``/``md``/``txt``/``xml``).

    Returns:
        Serialized output as a string.
    """
    fmt = validate_export_format(format)
    if fmt == "json":
        return _analysis_to_json(analysis, scope_label)
    if fmt == "csv":
        return _analysis_to_csv(analysis, scope_label)
    if fmt == "html":
        return _analysis_to_html(analysis, scope_label)
    if fmt == "txt":
        return _analysis_to_txt(analysis, scope_label)
    if fmt == "xml":
        return _analysis_to_xml(analysis, scope_label)
    return _analysis_to_md(analysis, scope_label)


def _analysis_metrics(analysis: dict[str, Any]) -> list[tuple[str, Any]]:
    return [
        ("token_count", analysis.get("token_count", 0)),
        ("unique_token_count", analysis.get("unique_token_count", 0)),
        ("type_token_ratio", analysis.get("type_token_ratio", 0.0)),
    ]


def _analysis_to_json(analysis: dict[str, Any], scope_label: str) -> str:
    top_words = [{"word": w, "count": c} for w, c in analysis.get("top_words", [])]
    top_bigrams = [{"bigram": b, "count": c} for b, c in analysis.get("top_bigrams", [])]
    top_trigrams = [{"trigram": t, "count": c} for t, c in analysis.get("top_trigrams", [])]

    return json.dumps(
        {
            "type": "analysis",
            "scope": scope_label,
            "token_count": analysis.get("token_count", 0),
            "unique_token_count": analysis.get("unique_token_count", 0),
            "type_token_ratio": analysis.get("type_token_ratio", 0.0),
            "top_words": top_words,
            "top_bigrams": top_bigrams,
            "top_trigrams": top_trigrams,
        },
        ensure_ascii=False,
        indent=2,
    )


def _analysis_to_csv(analysis: dict[str, Any], _scope_label: str) -> str:
    # Unified CSV schema so consumers can parse the file without guessing headers.
    header = ["section", "metric", "rank", "token", "count"]
    rows: list[list[str]] = []

    for metric, value in _analysis_metrics(analysis):
        rows.append(["metrics", metric, "", "", stringify_number(value)])

    for rank, (word, count) in enumerate(analysis.get("top_words", []), start=1):
        rows.append(["top_words", "", str(rank), word, stringify_number(count)])

    for rank, (bigram, count) in enumerate(analysis.get("top_bigrams", []), start=1):
        rows.append(["top_bigrams", "", str(rank), bigram, stringify_number(count)])

    for rank, (trigram, count) in enumerate(analysis.get("top_trigrams", []), start=1):
        rows.append(["top_trigrams", "", str(rank), trigram, stringify_number(count)])

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(header)
    writer.writerows(rows)
    return out.getvalue()


def _analysis_to_html(analysis: dict[str, Any], scope_label: str) -> str:
    metrics = _analysis_metrics(analysis)
    full_title, acronym = parse_and_format_scope(scope_label)

    fragments: list[str] = []
    fragments.append(
        "<section class='page-card glow'>"
        "<div class='title-stack'>"
        "<p class='eyebrow'>Text analysis</p>"
        f"<h1>{html.escape(full_title)}</h1>"
        + (f"<p class='title-acronym'>{html.escape(acronym)}</p>" if acronym else "")
        + "</div>"
        "<p class='section-title'><span>Token metrics, vocab richness, and n-grams</span></p>"
        "</section>"
    )

    fragments.append(
        "<section class='page-card'>"
        "<div class='section-title'>"
        "<h2>Key metrics</h2>"
        "<span>Essential counts & ratios</span>"
        "</div>"
        "<div class='glow'>"
        "<table><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>"
        + "".join(
            f"<tr><td>{html.escape(metric)}</td><td>{html.escape(stringify_number(value))}</td></tr>"
            for metric, value in metrics
        )
        + "</tbody></table>"
        "</div>"
        "</section>"
    )

    def _append_token_section(title: str, rows: list[tuple[str, int]], label: str) -> None:
        if not rows:
            return

        def _token_card(i: int, token: str, count: int) -> str:
            term = html.escape(token)
            count_value = html.escape(stringify_number(count))
            return (
                "<article class='token-card'>"
                f"<p class='token-rank'>#{i}</p>"
                f"<p class='token-term'>{term}</p>"
                f"<span class='token-count'>Count: {count_value}</span>"
                "</article>"
            )

        fragments.append(
            "<section class='page-card'>"
            "<div class='section-title'>"
            f"<h2>{html.escape(title)}</h2>"
            f"<span>Top {label}s</span>"
            "</div>"
            "<div class='token-grid'>"
            + "".join(
                _token_card(i, token, count) for i, (token, count) in enumerate(rows, start=1)
            )
            + "</div>"
            "</section>"
        )

    _append_token_section("Top Words", analysis.get("top_words", []), "word")
    _append_token_section("Top Bigrams", analysis.get("top_bigrams", []), "bigram")
    _append_token_section("Top Trigrams", analysis.get("top_trigrams", []), "trigram")

    return render_html_document(f"Text Analysis — {scope_label}", fragments)


def _analysis_to_md(analysis: dict[str, Any], scope_label: str) -> str:
    metrics = _analysis_metrics(analysis)
    lines: list[str] = []
    lines.append(f"# Text Analysis: {scope_label}")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    for metric, value in metrics:
        lines.append(f"| {metric} | {stringify_number(value)} |")
    lines.append("")

    def _token_table(title: str, rows: list[tuple[str, int]], token_label: str) -> None:
        if not rows:
            return
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"| Rank | {token_label} | Count |")
        lines.append("|---:|---|---:|")
        for i, (token, count) in enumerate(rows, start=1):
            lines.append(f"| {i} | {token} | {stringify_number(count)} |")
        lines.append("")

    _token_table("Top Words", analysis.get("top_words", []), "Word")
    _token_table("Top Bigrams", analysis.get("top_bigrams", []), "Bigram")
    _token_table("Top Trigrams", analysis.get("top_trigrams", []), "Trigram")
    return "\n".join(lines).rstrip() + "\n"


def _analysis_to_txt(analysis: dict[str, Any], scope_label: str) -> str:
    lines: list[str] = [
        f"Text analysis: {scope_label}",
        "",
        "Metrics",
        "-" * 40,
    ]
    for metric, value in _analysis_metrics(analysis):
        lines.append(f"  {metric}: {stringify_number(value)}")
    lines.append("")

    def _section(title: str, rows: list[tuple[str, int]], label: str) -> None:
        if not rows:
            return
        lines.append(title)
        lines.append("-" * 40)
        for i, (token, count) in enumerate(rows, start=1):
            lines.append(f"  {i:>3}. {label}: {token!r}  count={stringify_number(count)}")
        lines.append("")

    _section("Top words", analysis.get("top_words", []), "word")
    _section("Top bigrams", analysis.get("top_bigrams", []), "bigram")
    _section("Top trigrams", analysis.get("top_trigrams", []), "trigram")
    return "\n".join(lines).rstrip() + "\n"


def _analysis_to_xml(analysis: dict[str, Any], scope_label: str) -> str:
    root = ET.Element("analysis")
    root.set("type", "token-stats")
    scope_el = ET.SubElement(root, "scope")
    scope_el.text = scope_label

    metrics_el = ET.SubElement(root, "metrics")
    for metric, value in _analysis_metrics(analysis):
        m = ET.SubElement(metrics_el, "metric")
        m.set("name", metric)
        m.text = stringify_number(value)

    def _add_ranked(parent: ET.Element, tag: str, rows: list[tuple[str, int]]) -> None:
        block = ET.SubElement(parent, tag)
        for i, (token, count) in enumerate(rows, start=1):
            item = ET.SubElement(block, "item")
            item.set("rank", str(i))
            item.set("count", stringify_number(count))
            item.text = token

    _add_ranked(root, "top_words", analysis.get("top_words", []))
    _add_ranked(root, "top_bigrams", analysis.get("top_bigrams", []))
    _add_ranked(root, "top_trigrams", analysis.get("top_trigrams", []))
    return xml_document(root)
