"""Serialize verse lookup and FTS search results for file export."""

from __future__ import annotations

import csv
import html
import io
import json
import xml.etree.ElementTree as ET
from typing import Any, Literal

from clible.ui.analytics_export import validate_export_format

ExportKind = Literal["verse", "search"]


def _verse_ref(v: dict[str, Any]) -> str:
    return f"{v.get('book_id', '')} {v.get('chapter', '')}:{v.get('verse', '')}"


def _xml_doc(root: ET.Element) -> str:
    ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + body


def _payload_dict(
    *,
    kind: ExportKind,
    title: str,
    verses: list[dict[str, Any]],
    translation_id: str | None,
    search_word: str | None,
    scope: str | None,
    scope_ref: str | None,
    stats: dict[str, Any] | None,
) -> dict[str, Any]:
    rows = [
        {
            "book_id": v.get("book_id", ""),
            "chapter": v.get("chapter", ""),
            "verse": v.get("verse", ""),
            "text": v.get("text", ""),
        }
        for v in verses
    ]
    out: dict[str, Any] = {
        "type": "verse_lookup" if kind == "verse" else "search",
        "title": title,
        "translation_id": translation_id,
        "verses": rows,
    }
    if kind == "search":
        out["query"] = search_word
        out["scope"] = scope
        out["scope_ref"] = scope_ref
        out["statistics"] = stats or {}
    return out


def export_verses_bundle(
    verses: list[dict[str, Any]],
    *,
    kind: ExportKind,
    title: str,
    format: str,
    translation_id: str | None = None,
    search_word: str | None = None,
    scope: str | None = None,
    scope_ref: str | None = None,
    stats: dict[str, Any] | None = None,
) -> str:
    """Serialize verses (and optional search metadata) to a string.

    Args:
        verses: Verse dicts from VerseService (book_id, chapter, verse, text).
        kind: ``verse`` for lookup, ``search`` for FTS results.
        title: Human-readable heading (e.g. reference or search summary).
        format: One of the shared export formats (md, html, xml, txt, json, csv).
        translation_id: Active translation, if known.
        search_word: Search query when ``kind`` is ``search``.
        scope: Search scope name when ``kind`` is ``search``.
        scope_ref: Scope reference string when ``kind`` is ``search``.
        stats: ``get_search_statistics`` result when ``kind`` is ``search``.

    Returns:
        File content as UTF-8 text.
    """
    fmt = validate_export_format(format)
    if fmt == "json":
        return json.dumps(
            _payload_dict(
                kind=kind,
                title=title,
                verses=verses,
                translation_id=translation_id,
                search_word=search_word,
                scope=scope,
                scope_ref=scope_ref,
                stats=stats,
            ),
            ensure_ascii=False,
            indent=2,
        )
    if fmt == "csv":
        return _to_csv(verses)
    if fmt == "html":
        return _to_html(
            kind=kind,
            title=title,
            verses=verses,
            translation_id=translation_id,
            search_word=search_word,
            scope=scope,
            scope_ref=scope_ref,
            stats=stats,
        )
    if fmt == "md":
        return _to_md(
            kind=kind,
            title=title,
            verses=verses,
            translation_id=translation_id,
            search_word=search_word,
            scope=scope,
            scope_ref=scope_ref,
            stats=stats,
        )
    if fmt == "txt":
        return _to_txt(
            kind=kind,
            title=title,
            verses=verses,
            translation_id=translation_id,
            search_word=search_word,
            scope=scope,
            scope_ref=scope_ref,
            stats=stats,
        )
    return _to_xml(
        kind=kind,
        title=title,
        verses=verses,
        translation_id=translation_id,
        search_word=search_word,
        scope=scope,
        scope_ref=scope_ref,
        stats=stats,
    )


def _to_csv(verses: list[dict[str, Any]]) -> str:
    header = ["book_id", "chapter", "verse", "text"]
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(header)
    for v in verses:
        writer.writerow(
            [
                v.get("book_id", ""),
                v.get("chapter", ""),
                v.get("verse", ""),
                v.get("text", ""),
            ]
        )
    return out.getvalue()


def _to_txt(
    *,
    kind: ExportKind,
    title: str,
    verses: list[dict[str, Any]],
    translation_id: str | None,
    search_word: str | None,
    scope: str | None,
    scope_ref: str | None,
    stats: dict[str, Any] | None,
) -> str:
    lines: list[str] = [title, ""]
    if translation_id:
        lines.append(f"Translation: {translation_id}")
    if kind == "search":
        lines.append(f"Query: {search_word}")
        lines.append(f"Scope: {scope}" + (f" ({scope_ref})" if scope_ref else ""))
        lines.append("")
        if stats:
            lines.append("Statistics")
            lines.append("-" * 40)
            lines.append(f"  total_occurrences: {stats.get('total_occurrences', 0)}")
            lines.append(f"  unique_verses: {stats.get('unique_verses', 0)}")
            lines.append(f"  books_with_matches: {stats.get('books_with_matches', 0)}")
            lines.append("")
    lines.append("Verses")
    lines.append("-" * 40)
    for v in verses:
        lines.append(_verse_ref(v))
        lines.append(f"  {v.get('text', '')}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _to_md(
    *,
    kind: ExportKind,
    title: str,
    verses: list[dict[str, Any]],
    translation_id: str | None,
    search_word: str | None,
    scope: str | None,
    scope_ref: str | None,
    stats: dict[str, Any] | None,
) -> str:
    lines: list[str] = [f"# {title}", ""]
    if translation_id:
        lines.append(f"**Translation:** `{translation_id}`  ")
        lines.append("")
    if kind == "search":
        lines.append(f"**Query:** `{search_word}`  ")
        if scope or scope_ref:
            bits: list[str] = []
            if scope:
                bits.append(f"`{scope}`")
            if scope_ref:
                bits.append(f"`{scope_ref}`")
            lines.append(f"**Scope:** {' — '.join(bits)}  ")
            lines.append("")
        if stats:
            lines.append("## Statistics")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|---|---:|")
            lines.append(f"| Total occurrences | {stats.get('total_occurrences', 0)} |")
            lines.append(f"| Unique verses | {stats.get('unique_verses', 0)} |")
            lines.append(f"| Books with matches | {stats.get('books_with_matches', 0)} |")
            lines.append("")
    lines.append("## Verses")
    lines.append("")
    for v in verses:
        lines.append(f"### {_verse_ref(v)}")
        lines.append("")
        lines.append(v.get("text", ""))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _to_html(
    *,
    kind: ExportKind,
    title: str,
    verses: list[dict[str, Any]],
    translation_id: str | None,
    search_word: str | None,
    scope: str | None,
    scope_ref: str | None,
    stats: dict[str, Any] | None,
) -> str:
    parts: list[str] = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'>",
        f"<title>{html.escape(title)}</title>",
        "<style>"
        "body{font-family:Arial,Helvetica,sans-serif;max-width:880px;"
        "margin:24px auto;line-height:1.45}"
        "article{border-bottom:1px solid #e0e0e0;padding:16px 0}"
        "table{border-collapse:collapse;margin:12px 0}"
        "th,td{border:1px solid #ddd;padding:6px 10px}"
        "th{background:#f5f5f5;text-align:left}"
        "</style>",
        "</head><body>",
        f"<h1>{html.escape(title)}</h1>",
    ]
    if translation_id:
        parts.append(f"<p><strong>Translation:</strong> {html.escape(translation_id)}</p>")
    if kind == "search":
        parts.append(f"<p><strong>Query:</strong> {html.escape(str(search_word or ''))}</p>")
        scope_bits = [html.escape(str(scope or ""))]
        if scope_ref:
            scope_bits.append(html.escape(str(scope_ref)))
        parts.append(f"<p><strong>Scope:</strong> {' — '.join(scope_bits)}</p>")
        if stats:
            parts.append("<h2>Statistics</h2><table>")
            parts.append("<thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>")
            parts.append(
                f"<tr><td>Total occurrences</td><td>{stats.get('total_occurrences', 0)}</td></tr>"
            )
            parts.append(f"<tr><td>Unique verses</td><td>{stats.get('unique_verses', 0)}</td></tr>")
            parts.append(
                f"<tr><td>Books with matches</td><td>{stats.get('books_with_matches', 0)}</td></tr>"
            )
            parts.append("</tbody></table>")
    parts.append("<h2>Verses</h2>")
    for v in verses:
        ref = html.escape(_verse_ref(v))
        text = html.escape(v.get("text", ""))
        parts.append(f"<article><h3>{ref}</h3><p>{text}</p></article>")
    parts.append("</body></html>")
    return "".join(parts)


def _to_xml(
    *,
    kind: ExportKind,
    title: str,
    verses: list[dict[str, Any]],
    translation_id: str | None,
    search_word: str | None,
    scope: str | None,
    scope_ref: str | None,
    stats: dict[str, Any] | None,
) -> str:
    root = ET.Element("clible-export")
    root.set("kind", kind)
    ET.SubElement(root, "title").text = title
    if translation_id:
        ET.SubElement(root, "translation-id").text = translation_id
    if kind == "search":
        ET.SubElement(root, "query").text = str(search_word or "")
        sc = ET.SubElement(root, "scope")
        sc.set("name", str(scope or ""))
        if scope_ref:
            sc.set("reference", str(scope_ref))
        if stats:
            st = ET.SubElement(root, "statistics")
            for key in ("total_occurrences", "unique_verses", "books_with_matches"):
                if key in stats:
                    el = ET.SubElement(st, key.replace("_", "-"))
                    el.text = str(stats[key])
            tb = stats.get("top_books") or []
            if tb:
                top = ET.SubElement(st, "top-books")
                for book_id, count in tb:
                    b = ET.SubElement(top, "book")
                    b.set("occurrences", str(count))
                    b.text = str(book_id)
    vers_el = ET.SubElement(root, "verses")
    for v in verses:
        item = ET.SubElement(vers_el, "verse")
        item.set("book", str(v.get("book_id", "")))
        item.set("chapter", str(v.get("chapter", "")))
        item.set("verse", str(v.get("verse", "")))
        item.text = str(v.get("text", ""))
    return _xml_doc(root)
