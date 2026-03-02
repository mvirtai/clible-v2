import xml.etree.ElementTree as ET
from pathlib import Path

from clible.parsers.osis_book_map import to_clible_id

NS = "{http://www.bibletechnologies.net/2003/OSIS/namespace}"
_SKIP_TAGS = {f"{NS}note", f"{NS}reference"}


def _collect_verse_text(verse_elem: ET.Element) -> str:
    """Collect verse text from a container <verse>...</verse>, skipping note/reference."""
    parts: list[str] = []

    for elem in verse_elem.iter():
        if elem is verse_elem:
            if elem.text:
                parts.append(elem.text)
        elif elem.tag in _SKIP_TAGS:
            if elem.tail:
                parts.append(elem.tail)
        else:
            if elem.text:
                parts.append(elem.text)
            if elem.tail:
                parts.append(elem.tail)

    return " ".join("".join(parts).split())


def _collect_milestone_verse_text(parent: ET.Element, start_verse_elem: ET.Element) -> str:
    """Collect text between milestone <verse sID="..."/> and <verse eID="..."/>.

    Text lives in start_verse_elem.tail and in following siblings until the
    verse element with matching eID. Skips note/reference element content.
    """
    s_id = start_verse_elem.get("sID")
    if not s_id:
        return ""

    parts: list[str] = [start_verse_elem.tail or ""]
    found_start = False

    for child in parent:
        if child is start_verse_elem:
            found_start = True
            continue
        if not found_start:
            continue
        if child.tag == f"{NS}verse" and child.get("eID") == s_id:
            break
        if child.tag in _SKIP_TAGS:
            parts.append(child.tail or "")
        else:
            parts.append("".join(child.itertext()) + (child.tail or ""))

    return " ".join("".join(parts).split())


class OSISParser:
    """Parse OSIS format XML into verse dictionaries.

    Supports both container form (<verse osisID="...">text</verse>) and
    milestone form (<verse sID="..." osisID="..."/> text <verse eID="..."/>).
    Returns a list of dicts with keys: book_id, chapter, verse, text.
    Skips note/reference content, mapping OSIS book codes to clible book IDs.
    """

    def parse_file(self, xml_path: Path) -> list[dict]:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        parent_map: dict[ET.Element, ET.Element] = {}
        for p in root.iter():
            for c in p:
                parent_map[c] = p

        verse_dicts: list[dict] = []

        for v in root.findall(f".//{NS}verse"):
            osis_id = v.get("osisID")
            s_id = v.get("sID")
            e_id = v.get("eID")

            if e_id and not osis_id:
                continue

            if not osis_id:
                continue

            parts = osis_id.split(".")
            if len(parts) != 3:
                continue

            book_code, chapter_str, verse_str = parts
            book_id = to_clible_id(book_code)
            if book_id is None:
                continue

            try:
                chapter = int(chapter_str)
                verse = int(verse_str)
            except ValueError:
                continue

            if s_id:
                parent = parent_map.get(v)
                if parent is None:
                    continue
                text = _collect_milestone_verse_text(parent, v)
            else:
                text = _collect_verse_text(v)

            verse_dicts.append(
                {
                    "book_id": book_id,
                    "chapter": chapter,
                    "verse": verse,
                    "text": text,
                }
            )

        return verse_dicts
