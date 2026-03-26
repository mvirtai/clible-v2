"""Serialize verse lookup and FTS search results for file export."""

from __future__ import annotations

import csv
import html
import io
import json
import xml.etree.ElementTree as ET
from typing import Any, Literal

from clible.ui.export import render_html_document, validate_export_format
from clible.ui.export.shared import format_title_with_acronym, full_verse_ref

ExportKind = Literal["verse", "search"]


def _verse_ref(v: dict[str, Any]) -> str:
    return f"{v.get('book_id', '')} {v.get('chapter', '')}:{v.get('verse', '')}"


def _format_number(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".") if value != int(value) else str(int(value))
    return str(value)


def _full_verse_ref(v: dict[str, Any]) -> tuple[str, str]:
    """Return (full_ref, acronym_ref) for a verse dict."""
    return full_verse_ref(v)


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
    fragments: list[str] = []
    if kind == "verse" and verses:
        first_verse = verses[0]
        full_title, acronym = format_title_with_acronym(
            first_verse.get("book_id", ""),
            first_verse.get("chapter", 0),
            first_verse.get("verse", 0),
        )
        eyebrow = "Verse export"
    else:
        full_title = title
        acronym = ""
        eyebrow = "Search results" if kind == "search" else "Verse export"

    fragments.append(
        "<section class='page-card glow'>"
        "<div class='title-stack'>"
        f"<p class='eyebrow'>{eyebrow}</p>"
        f"<h1>{html.escape(full_title)}</h1>"
        + (f"<p class='title-acronym'>{html.escape(acronym)}</p>" if acronym else "")
        + "</div>"
        "<p class='section-title'><span>Readable, export-ready format</span></p>"
        "</section>"
    )

    if translation_id:
        fragments.append(
            "<section class='page-card'><div class='summary-row'>"
            "<span class='summary-label'>Translation</span>"
            f"<span class='summary-value'>{html.escape(translation_id)}</span></div></section>"
        )

    def _meta_row(label: str, value: str) -> str:
        return (
            "<div class='summary-row'>"
            f"<span class='summary-label'>{html.escape(label)}</span>"
            f"<span class='summary-value'>{html.escape(value)}</span>"
            "</div>"
        )

    if kind == "search":
        meta_fragments = [
            _meta_row("Query", str(search_word or "")),
            _meta_row("Scope", " — ".join(filter(bool, [scope or "", scope_ref or ""]))),
        ]
        if stats:
            meta_fragments.append(
                _meta_row("Total occurrences", _format_number(stats.get("total_occurrences", 0)))
            )
            meta_fragments.append(
                _meta_row("Unique verses", _format_number(stats.get("unique_verses", 0)))
            )
            meta_fragments.append(
                _meta_row(
                    "Books with matches",
                    _format_number(stats.get("books_with_matches", 0)),
                )
            )
        fragments.append(
            "<section class='page-card'>"
            "<div class='section-title'>"
            "<h2>Search statistics</h2>"
            "<span>Scope & performance</span>"
            "</div>"
            "<div class='glow'>" + "".join(meta_fragments) + "</div>"
            "</section>"
        )

    def _verse_card(v: dict[str, Any]) -> str:
        full_ref, acronym_ref = _full_verse_ref(v)
        text = html.escape(v.get("text", ""))
        return (
            "<article class='verse-pair'>"
            "<div class='title-stack'>"
            f"<h3>{html.escape(full_ref)}</h3>"
            f"<p class='title-acronym'>{html.escape(acronym_ref)}</p>"
            "</div>"
            f"<p class='verse-text'>{text}</p>"
            "</article>"
        )

    fragments.append(
        "<section class='page-card'>"
        "<div class='section-title'><h2>Verses</h2><span>Study-ready text</span></div>"
        + "".join(_verse_card(v) for v in verses)
        + "</section>"
    )

    return render_html_document(title, fragments)


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
