"""Translation comparison result serialization (analytics export)."""

from __future__ import annotations

import csv
import html
import io
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from clible.ui.export.html_document import render_html_document
from clible.ui.export.io import validate_export_format
from clible.ui.export.scope import parse_and_format_scope
from clible.ui.export.shared import full_verse_ref, stringify_number, xml_document


def export_compare(comparison: dict[str, Any], *, format: str) -> str:
    """Export a translation comparison dictionary.

    Args:
        comparison: Result of ``AnalyticService.compare_translations``.
        format: Output format string (``json``/``csv``/``html``/``md``/``txt``/``xml``).

    Returns:
        Serialized output as a string.
    """
    fmt = validate_export_format(format)
    if fmt == "json":
        return _compare_to_json(comparison)
    if fmt == "csv":
        return _compare_to_csv(comparison)
    if fmt == "html":
        return _compare_to_html(comparison)
    if fmt == "txt":
        return _compare_to_txt(comparison)
    if fmt == "xml":
        return _compare_to_xml(comparison)
    return _compare_to_md(comparison)


def _compare_to_txt(comparison: dict[str, Any]) -> str:
    reference = str(comparison.get("reference", ""))
    translation_a = str(comparison.get("translation_a", ""))
    translation_b = str(comparison.get("translation_b", ""))
    summary = comparison.get("summary", {}) or {}

    lines: list[str] = [
        f"Translation comparison: {reference}",
        f"Left: {translation_a}",
        f"Right: {translation_b}",
        "",
        "Summary",
        "-" * 40,
    ]
    for key in [
        "total_verses",
        "fully_aligned_verses",
        "exact_matches",
        "exact_match_ratio",
        "average_similarity",
    ]:
        if key in summary:
            lines.append(f"  {key}: {stringify_number(summary.get(key))}")
    lines.append("")
    lines.append("Aligned verses")
    lines.append("-" * 40)

    for row in comparison.get("aligned_verses", []):
        ref = f"{row.get('book_id', '')} {row.get('chapter', '')}:{row.get('verse', '')}"
        lines.append(f"[{ref}]")
        lines.append(f"  A: {row.get('text_a', '')}")
        lines.append(f"  B: {row.get('text_b', '')}")
        lines.append(f"  similarity: {stringify_number(row.get('similarity', 0.0))}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _compare_to_xml(comparison: dict[str, Any]) -> str:
    root = ET.Element("comparison")
    root.set("type", "translation-compare")
    ET.SubElement(root, "reference").text = str(comparison.get("reference", ""))
    ET.SubElement(root, "translation_a").text = str(comparison.get("translation_a", ""))
    ET.SubElement(root, "translation_b").text = str(comparison.get("translation_b", ""))

    summary = comparison.get("summary", {}) or {}
    sum_el = ET.SubElement(root, "summary")
    for key in [
        "total_verses",
        "fully_aligned_verses",
        "exact_matches",
        "exact_match_ratio",
        "average_similarity",
    ]:
        if key in summary:
            child = ET.SubElement(sum_el, key.replace("_", "-"))
            child.text = stringify_number(summary.get(key))

    if "top_shared_words" in summary:
        tsw = ET.SubElement(sum_el, "top-shared-words")
        for word, count in summary.get("top_shared_words", []):
            w = ET.SubElement(tsw, "word")
            w.set("count", stringify_number(count))
            w.text = str(word)

    av = ET.SubElement(root, "aligned-verses")
    for row in comparison.get("aligned_verses", []):
        v = ET.SubElement(av, "verse")
        v.set("book", str(row.get("book_id", "")))
        v.set("chapter", stringify_number(row.get("chapter", "")))
        v.set("verse", stringify_number(row.get("verse", "")))
        v.set("similarity", stringify_number(row.get("similarity", 0.0)))
        v.set("exact-match", str(bool(row.get("exact_match", False))).lower())
        ta = ET.SubElement(v, "text-a")
        ta.text = str(row.get("text_a", ""))
        tb = ET.SubElement(v, "text-b")
        tb.text = str(row.get("text_b", ""))

    return xml_document(root)


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
                    stringify_number(summary.get(metric)),
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
                stringify_number(row.get("chapter", "")),
                stringify_number(row.get("verse", "")),
                str(row.get("text_a", "")),
                str(row.get("text_b", "")),
                stringify_number(row.get("similarity", 0.0)),
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
    full_title, acronym = parse_and_format_scope(reference)

    translations_catalog = _load_translations_catalog()

    def _language_label(language_code: str) -> str:
        code = language_code.lower().strip()
        return {
            "fi": "Finnish",
            "en": "English",
            "grc": "Greek",
            "el": "Greek",
            "he": "Hebrew",
            "la": "Latin",
            "sv": "Swedish",
            "de": "German",
            "fr": "French",
            "es": "Spanish",
        }.get(code, code or "Unknown")

    def _translation_display(translation_id: str) -> tuple[str, str]:
        item = translations_catalog.get(translation_id, {}) or {}
        language_code = str(item.get("language", "")).strip()
        name = str(item.get("name", "")).strip() or translation_id
        if translation_id.lower().startswith("greek"):
            # Some catalog entries use "en" even when the translation is Greek.
            language_code = "grc"
        language = _language_label(language_code)
        return language, name

    def _translation_header(*, translation_id: str, show_title: bool) -> str:
        language, name = _translation_display(translation_id)
        title = (
            name
            if language.lower() == name.lower() or name.lower().startswith(f"{language.lower()} ")
            else f"{language} · {name}"
        )
        title_html = (
            "".join(
                [
                    "<p class='compare-translation-title'>",
                    html.escape(title),
                    "</p>",
                ]
            )
            if show_title
            else ""
        )
        id_html = f"<p class='compare-translation-id'>{html.escape(translation_id)}</p>"
        return "".join(["<div class='compare-translation-head'>", title_html, id_html, "</div>"])

    fragments: list[str] = []
    fragments.append(
        "<section class='page-card glow'>"
        "<div class='title-stack'>"
        "<p class='eyebrow'>Translation comparison</p>"
        f"<h1>{html.escape(full_title)}</h1>"
        + (f"<p class='title-acronym'>{html.escape(acronym)}</p>" if acronym else "")
        + "</div>"
        "<p class='section-title'><span>Aligned verses meet similarity scores</span></p>"
        "</section>"
    )

    fragments.append(
        "<section class='page-card'>"
        "<div class='section-title section-title--center'>"
        "<h2>Translations</h2>"
        "<span>Languages & editions</span>"
        "</div>"
        "<div class='compare-grid'>"
        f"<article class='compare-card'>{_translation_header(translation_id=translation_a, show_title=True)}</article>"  # noqa: E501
        f"<article class='compare-card'>{_translation_header(translation_id=translation_b, show_title=True)}</article>"  # noqa: E501
        "</div></section>"
    )

    def _summary_row(label: str, value: Any) -> str:
        return (
            "<div class='summary-row'>"
            f"<span class='summary-label'>{html.escape(label)}</span>"
            f"<span class='summary-value'>{html.escape(stringify_number(value))}</span>"
            "</div>"
        )

    if summary:
        fragments.append(
            "<section class='page-card'>"
            "<div class='section-title'>"
            "<h2>Summary statistics</h2>"
            "<span>Correlation & coverage</span>"
            "</div>"
            "<div class='glow'>"
            + "".join(
                _summary_row(key.replace("_", " ").title(), summary[key])
                for key in (
                    "total_verses",
                    "fully_aligned_verses",
                    "exact_matches",
                    "exact_match_ratio",
                    "average_similarity",
                )
                if key in summary
            )
        )
        if "top_shared_words" in summary:
            shared_words = [
                f"{html.escape(word)} ({html.escape(stringify_number(count))})"
                for word, count in summary.get("top_shared_words", [])
            ]
            fragments.append(
                "<div class='summary-row'>"
                "<span class='summary-label'>Top shared words</span>"
                "<span class='summary-value'>" + ", ".join(shared_words) + "</span></div>"
            )
        fragments.append("</div></section>")

    aligned = comparison.get("aligned_verses", [])
    if aligned:

        def _verse_card(row: dict[str, Any]) -> str:
            full_ref, acronym_ref = full_verse_ref(row)
            left = html.escape(str(row.get("text_a", "")))
            right = html.escape(str(row.get("text_b", "")))
            similarity = stringify_number(row.get("similarity", 0.0))
            return (
                "<article class='verse-pair'>"
                "<div class='title-stack'>"
                f"<h3>{html.escape(full_ref)}</h3>"
                f"<p class='title-acronym'>{html.escape(acronym_ref)}</p>"
                "</div>"
                f"{_translation_header(translation_id=translation_a, show_title=False)}"
                f"<p class='verse-text'>{left}</p>"
                f"{_translation_header(translation_id=translation_b, show_title=False)}"
                f"<p class='verse-text'>{right}</p>"
                "<p class='verse-text compare-similarity'>"
                f"<strong>Similarity:</strong> {html.escape(similarity)}"
                "</p>"
                "</article>"
            )

        fragments.append("<section class='page-card'>")
        fragments.append(
            "<div class='section-title section-title--center'>"
            "<h2>Aligned verses</h2>"
            "<span>Verse-by-verse view</span>"
            "</div>"
        )
        fragments.append("".join(_verse_card(row) for row in aligned))
        fragments.append("</section>")

    return render_html_document(f"Translation comparison — {reference}", fragments)


_TRANSLATIONS_CATALOG_CACHE: dict[str, dict[str, Any]] | None = None


def _load_translations_catalog() -> dict[str, dict[str, Any]]:
    global _TRANSLATIONS_CATALOG_CACHE
    if _TRANSLATIONS_CATALOG_CACHE is not None:
        return _TRANSLATIONS_CATALOG_CACHE
    catalog_path = Path(__file__).resolve().parents[2] / "data" / "translations.json"
    with catalog_path.open("r", encoding="utf-8") as f:
        _TRANSLATIONS_CATALOG_CACHE = json.load(f)
    return _TRANSLATIONS_CATALOG_CACHE


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
    lines.append(f"| total_verses | {stringify_number(summary.get('total_verses', 0))} |")
    lines.append(
        f"| fully_aligned_verses | {stringify_number(summary.get('fully_aligned_verses', 0))} |"
    )
    lines.append(f"| exact_matches | {stringify_number(summary.get('exact_matches', 0))} |")
    lines.append(
        f"| exact_match_ratio | {stringify_number(summary.get('exact_match_ratio', 0.0))} |"
    )
    lines.append(
        f"| average_similarity | {stringify_number(summary.get('average_similarity', 0.0))} |"
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
        lines.append(f"| {verse_ref} | {left} | {right} | {stringify_number(similarity)} |")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"
