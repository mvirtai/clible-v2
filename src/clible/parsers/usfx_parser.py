"""USFX (Unified Scripture Format XML) parser for Bible text."""

import xml.etree.ElementTree as ET
from pathlib import Path

# USFX book IDs to skip (front/back matter, not canonical text)
_SKIP_BOOK_IDS = {"FRT", "BAK"}

# Inline elements whose content we exclude from verse text (e.g. footnotes)
_SKIP_INLINE_TAGS = {"f", "ref"}


def _collect_verse_text(parent: ET.Element, verse_elem: ET.Element) -> str:
    """Extract verse text from between <v> and <ve/>.

    In USFX, verse text lives in the tail of <v> and in the tails of
    following sibling elements until <ve/>. We skip footnote (<f>) and
    cross-reference (<ref>) content but keep their trailing text.
    """
    parts = [verse_elem.tail or ""]
    found = False
    for child in parent:
        if child is verse_elem:
            found = True
            continue
        if not found:
            continue
        if child.tag == "ve":
            break
        if child.tag in _SKIP_INLINE_TAGS:
            parts.append(child.tail or "")
        else:
            text_content = "".join(child.itertext())
            parts.append(text_content + (child.tail or ""))
    return " ".join("".join(parts).split())


def _process_book(book: ET.Element, book_id: str) -> list[dict]:
    """Extract verse dicts from a single book element."""
    verses: list[dict] = []
    chapter = [0]  # mutable so nested calls can update

    def recurse(parent: ET.Element, elem: ET.Element) -> None:
        if elem.tag == "c" and elem.get("id"):
            chapter[0] = int(elem.get("id", 0))
        elif elem.tag == "v" and elem.get("id"):
            raw_id = elem.get("id", "0")
            try:
                verse_num = int(raw_id.split("-")[0])
            except (ValueError, AttributeError):
                verse_num = 0
            if verse_num > 0 and chapter[0] > 0:
                text = _collect_verse_text(parent, elem)
                verses.append(
                    {
                        "book_id": book_id,
                        "chapter": chapter[0],
                        "verse": verse_num,
                        "text": text,
                    }
                )
        for child in elem:
            recurse(elem, child)

    for child in book:
        recurse(book, child)
    return verses


class USFXParser:
    """Parse USFX format XML into verse dictionaries."""

    def parse_file(self, xml_path: Path) -> list[dict]:
        """Parse a USFX XML file and return verse dicts.

        Returns list of dicts with keys: book_id, chapter, verse, text.
        Skips front matter (FRT), back matter (BAK), and footnote content.

        Args:
            xml_path: Path to the USFX XML file.

        Returns:
            List of verse dicts suitable for bulk insert.
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()
        all_verses: list[dict] = []
        for book in root.findall("book"):
            book_id = book.get("id", "")
            if book_id in _SKIP_BOOK_IDS:
                continue
            all_verses.extend(_process_book(book, book_id))
        return all_verses
