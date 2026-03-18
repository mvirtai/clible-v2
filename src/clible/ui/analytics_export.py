"""
Analytics export helpers.

This module converts analytics result dictionaries into a user-selected file
format. It performs no database access and no network calls.
"""

from __future__ import annotations

import csv
import html
import io
import json
from pathlib import Path
from typing import Any

_SUPPORTED_FORMATS: set[str] = {"json", "csv", "html", "md"}


def detect_format(output_path: Path) -> str:
    """Detect output format by file extension.

    Args:
        output_path: Output file path. Format is inferred from the extension.

    Returns:
        A lower-case format string: one of ``json/csv/html/md``.

    Raises:
        ValueError: If the extension is missing or unsupported.
    """
    suffix = output_path.suffix.lower().lstrip(".")
    if not suffix:
        raise ValueError("Missing file extension for --output. Use .json/.csv/.html/.md.")
    if suffix not in _SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported --output format '.{suffix}'. Use one of: "
            + ", ".join(sorted(_SUPPORTED_FORMATS))
            + "."
        )
    return suffix


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text to the given file path.

    Args:
        path: Output file path.
        content: Text content to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def export_analysis(analysis: dict[str, Any], *, scope_label: str, format: str) -> str:
    """Export a token-based analysis dictionary.

    Args:
        analysis: Result of ``AnalyticService.analyze_reference/analyze_chapter/analyze_book``.
        scope_label: Human-readable scope string (e.g. ``"John 3:16-18"``).
        format: Output format string (``json/csv/html/md``).

    Returns:
        Serialized output as a string.
    """
    fmt = _validate_format(format)
    if fmt == "json":
        return _analysis_to_json(analysis, scope_label)
    if fmt == "csv":
        return _analysis_to_csv(analysis, scope_label)
    if fmt == "html":
        return _analysis_to_html(analysis, scope_label)
    return _analysis_to_md(analysis, scope_label)


def export_compare(comparison: dict[str, Any], *, format: str) -> str:
    """Export a translation comparison dictionary.

    Args:
        comparison: Result of ``AnalyticService.compare_translations``.
        format: Output format string (``json/csv/html/md``).

    Returns:
        Serialized output as a string.
    """
    fmt = _validate_format(format)
    if fmt == "json":
        return _compare_to_json(comparison)
    if fmt == "csv":
        return _compare_to_csv(comparison)
    if fmt == "html":
        return _compare_to_html(comparison)
    return _compare_to_md(comparison)


def _validate_format(format: str) -> str:
    fmt = format.lower().strip()
    if fmt not in _SUPPORTED_FORMATS:
        supported = ", ".join(sorted(_SUPPORTED_FORMATS))
        raise ValueError(f"Unsupported format '{format}'. Use one of: {supported}.")
    return fmt


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


def _stringify_number(value: Any) -> str:
    if isinstance(value, float):
        # Keep deterministic precision for tests/users; avoid long binary floats.
        return f"{value:.6f}".rstrip("0").rstrip(".") if value != int(value) else str(int(value))
    return str(value)


def _analysis_to_csv(analysis: dict[str, Any], _scope_label: str) -> str:
    # Unified CSV schema so consumers can parse the file without guessing headers.
    header = ["section", "metric", "rank", "token", "count"]
    rows: list[list[str]] = []

    for metric, value in _analysis_metrics(analysis):
        rows.append(["metrics", metric, "", "", _stringify_number(value)])

    for rank, (word, count) in enumerate(analysis.get("top_words", []), start=1):
        rows.append(["top_words", "", str(rank), word, _stringify_number(count)])

    for rank, (bigram, count) in enumerate(analysis.get("top_bigrams", []), start=1):
        rows.append(["top_bigrams", "", str(rank), bigram, _stringify_number(count)])

    for rank, (trigram, count) in enumerate(analysis.get("top_trigrams", []), start=1):
        rows.append(["top_trigrams", "", str(rank), trigram, _stringify_number(count)])

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(header)
    writer.writerows(rows)
    return out.getvalue()


def _analysis_to_html(analysis: dict[str, Any], scope_label: str) -> str:
    metrics = _analysis_metrics(analysis)

    def _row(metric: str, value: Any) -> str:
        return (
            f"<tr><td>{html.escape(metric)}</td>"
            f"<td>{html.escape(_stringify_number(value))}</td></tr>"
        )

    parts: list[str] = []
    parts.append("<!doctype html>")
    parts.append("<html><head><meta charset='utf-8'>")
    parts.append(f"<title>Analytics - {html.escape(scope_label)}</title>")
    parts.append(
        "<style>"
        "body{font-family:Arial,Helvetica,sans-serif;max-width:980px;"
        "margin:24px auto;line-height:1.4}"
        "table{border-collapse:collapse;width:100%}"
        "th,td{border:1px solid #ddd;padding:8px;vertical-align:top}"
        "th{background:#f6f6f6;text-align:left}"
        "</style>"
    )
    parts.append("</head><body>")
    parts.append(f"<h1>Text Analysis: {html.escape(scope_label)}</h1>")

    parts.append("<h2>Metrics</h2>")
    parts.append("<table><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>")
    parts.extend(_row(metric, value) for metric, value in metrics)
    parts.append("</tbody></table>")

    if analysis.get("top_words"):
        parts.append("<h2>Top Words</h2>")
        parts.append(
            "<table><thead><tr><th>Rank</th><th>Word</th><th>Count</th></tr></thead><tbody>"
        )
        for i, (word, count) in enumerate(analysis.get("top_words", []), start=1):
            parts.append(
                "<tr>"
                f"<td>{i}</td><td>{html.escape(word)}</td><td>{html.escape(_stringify_number(count))}</td>"
                "</tr>"
            )
        parts.append("</tbody></table>")

    if analysis.get("top_bigrams"):
        parts.append("<h2>Top Bigrams</h2>")
        parts.append(
            "<table><thead><tr><th>Rank</th><th>Bigram</th><th>Count</th></tr></thead><tbody>"
        )
        for i, (bigram, count) in enumerate(analysis.get("top_bigrams", []), start=1):
            parts.append(
                "<tr>"
                f"<td>{i}</td><td>{html.escape(bigram)}</td><td>{html.escape(_stringify_number(count))}</td>"
                "</tr>"
            )
        parts.append("</tbody></table>")

    if analysis.get("top_trigrams"):
        parts.append("<h2>Top Trigrams</h2>")
        parts.append(
            "<table><thead><tr><th>Rank</th><th>Trigram</th><th>Count</th></tr></thead><tbody>"
        )
        for i, (trigram, count) in enumerate(analysis.get("top_trigrams", []), start=1):
            parts.append(
                "<tr>"
                f"<td>{i}</td><td>{html.escape(trigram)}</td><td>{html.escape(_stringify_number(count))}</td>"
                "</tr>"
            )
        parts.append("</tbody></table>")

    parts.append("</body></html>")
    return "".join(parts)


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
        lines.append(f"| {metric} | {_stringify_number(value)} |")
    lines.append("")

    def _token_table(title: str, rows: list[tuple[str, int]], token_label: str) -> None:
        if not rows:
            return
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"| Rank | {token_label} | Count |")
        lines.append("|---:|---|---:|")
        for i, (token, count) in enumerate(rows, start=1):
            lines.append(f"| {i} | {token} | {_stringify_number(count)} |")
        lines.append("")

    _token_table("Top Words", analysis.get("top_words", []), "Word")
    _token_table("Top Bigrams", analysis.get("top_bigrams", []), "Bigram")
    _token_table("Top Trigrams", analysis.get("top_trigrams", []), "Trigram")
    return "\n".join(lines).rstrip() + "\n"


def _compare_to_json(comparison: dict[str, Any]) -> str:
    return json.dumps(
        {
            "type": "compare",
            "reference": comparison.get("reference"),
            "translation_a": comparison.get("translation_a"),
            "translation_b": comparison.get("translation_b"),
            "summary": comparison.get("summary"),
            "aligned_verses": comparison.get("aligned_verses", []),
        },
        ensure_ascii=False,
        indent=2,
    )


def _compare_to_csv(comparison: dict[str, Any]) -> str:
    # Same technique as analysis CSV: a single header and a "section" discriminator.
    header = [
        "section",
        "metric",
        "value",
        "book_id",
        "chapter",
        "verse",
        "text_a",
        "text_b",
        "similarity",
        "exact_match",
    ]
    rows: list[list[str]] = []

    summary = comparison.get("summary", {}) or {}
    for metric in [
        "total_verses",
        "fully_aligned_verses",
        "exact_matches",
        "exact_match_ratio",
        "average_similarity",
    ]:
        if metric in summary:
            rows.append(
                [
                    "summary",
                    metric,
                    _stringify_number(summary.get(metric)),
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )

    if "top_shared_words" in summary:
        rows.append(
            [
                "summary",
                "top_shared_words",
                json.dumps(summary.get("top_shared_words", []), ensure_ascii=False),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )

    if "most_similar_verse" in summary:
        most_similar = summary.get("most_similar_verse")
        rows.append(
            [
                "summary",
                "most_similar_verse",
                json.dumps(most_similar, ensure_ascii=False) if most_similar is not None else "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )

    for row in comparison.get("aligned_verses", []):
        rows.append(
            [
                "aligned_verses",
                "",
                "",
                str(row.get("book_id", "")),
                _stringify_number(row.get("chapter", "")),
                _stringify_number(row.get("verse", "")),
                str(row.get("text_a", "")),
                str(row.get("text_b", "")),
                _stringify_number(row.get("similarity", 0.0)),
                str(row.get("exact_match", False)),
            ]
        )

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(header)
    writer.writerows(rows)
    return out.getvalue()


def _compare_to_html(comparison: dict[str, Any]) -> str:
    reference = str(comparison.get("reference", ""))
    translation_a = str(comparison.get("translation_a", ""))
    translation_b = str(comparison.get("translation_b", ""))
    summary = comparison.get("summary", {}) or {}

    parts: list[str] = []
    parts.append("<!doctype html>")
    parts.append("<html><head><meta charset='utf-8'>")
    parts.append(f"<title>Analytics Compare - {html.escape(reference)}</title>")
    parts.append(
        "<style>"
        "body{font-family:Arial,Helvetica,sans-serif;max-width:1200px;"
        "margin:24px auto;line-height:1.4}"
        "table{border-collapse:collapse;width:100%}"
        "th,td{border:1px solid #ddd;padding:8px;vertical-align:top}"
        "th{background:#f6f6f6;text-align:left}"
        ".small{color:#555;font-size:12px}"
        "</style>"
    )
    parts.append("</head><body>")
    parts.append(f"<h1>Translation Comparison: {html.escape(reference)}</h1>")
    parts.append("<h2>Similarity Summary</h2>")
    parts.append("<table><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>")

    metrics: list[tuple[str, Any]] = [
        ("total_verses", summary.get("total_verses", 0)),
        ("fully_aligned_verses", summary.get("fully_aligned_verses", 0)),
        ("exact_matches", summary.get("exact_matches", 0)),
        ("exact_match_ratio", summary.get("exact_match_ratio", 0.0)),
        ("average_similarity", summary.get("average_similarity", 0.0)),
    ]
    for metric, value in metrics:
        parts.append(
            f"<tr><td>{html.escape(metric)}</td><td>{html.escape(_stringify_number(value))}</td></tr>"
        )

    parts.append("</tbody></table>")

    parts.append("<h2>Aligned Verses</h2>")
    parts.append("<table><thead><tr>")
    parts.append("<th>Verse</th>")
    parts.append(f"<th>{html.escape(translation_a)}</th>")
    parts.append(f"<th>{html.escape(translation_b)}</th>")
    parts.append("<th>Similarity</th>")
    parts.append("</tr></thead><tbody>")

    for row in comparison.get("aligned_verses", []):
        verse_ref = f"{row.get('book_id', '')} {row.get('chapter', '')}:{row.get('verse', '')}"
        similarity = row.get("similarity", 0.0)
        parts.append(
            "<tr>"
            f"<td>{html.escape(str(verse_ref))}</td>"
            f"<td>{html.escape(str(row.get('text_a', '')))}</td>"
            f"<td>{html.escape(str(row.get('text_b', '')))}</td>"
            f"<td>{html.escape(_stringify_number(similarity))}</td>"
            "</tr>"
        )

    parts.append("</tbody></table>")
    parts.append("</body></html>")
    return "".join(parts)


def _compare_to_md(comparison: dict[str, Any]) -> str:
    reference = str(comparison.get("reference", ""))
    summary = comparison.get("summary", {}) or {}

    lines: list[str] = []
    lines.append(f"# Translation Comparison: {reference}")
    lines.append("")
    lines.append("## Similarity Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| total_verses | {_stringify_number(summary.get('total_verses', 0))} |")
    lines.append(
        f"| fully_aligned_verses | {_stringify_number(summary.get('fully_aligned_verses', 0))} |"
    )
    lines.append(f"| exact_matches | {_stringify_number(summary.get('exact_matches', 0))} |")
    lines.append(
        f"| exact_match_ratio | {_stringify_number(summary.get('exact_match_ratio', 0.0))} |"
    )
    lines.append(
        f"| average_similarity | {_stringify_number(summary.get('average_similarity', 0.0))} |"
    )
    lines.append("")

    lines.append("## Aligned Verses")
    lines.append("")
    lines.append("| Verse | Left | Right | Similarity |")
    lines.append("|---|---|---|---:|")
    for row in comparison.get("aligned_verses", []):
        verse_ref = f"{row.get('book_id', '')} {row.get('chapter', '')}:{row.get('verse', '')}"
        left = str(row.get("text_a", ""))
        right = str(row.get("text_b", ""))
        similarity = row.get("similarity", 0.0)
        lines.append(f"| {verse_ref} | {left} | {right} | {_stringify_number(similarity)} |")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"
