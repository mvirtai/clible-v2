"""Unified XML parser for all supported Bible formats (USFX, OSIS, Beblia, Zefania)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from clible.parsers.book_ids import ordered_book_ids
from clible.parsers.osis_book_map import to_clible_id


class CombinedParser:
    """Parse various XML formats into verse dictionaries.

    Supports:
    - USFX (Unified Scripture Format XML)
    - OSIS (Open Scripture Information Standard)
    - Beblia (Simple book/chapter/verse structure)
    - Zefania (XMLBIBLE/BIBLEBOOK structure)
    """

    def parse_file(self, xml_path: Path) -> list[dict]:
        """Parse an XML file and return list of verse dicts.

        Args:
            xml_path: Path to the XML file.

        Returns:
            List of dicts with: book_id, chapter, verse, text.

        Raises:
            ValueError: If format cannot be determined or XML is malformed.
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Malformed XML file: {e}") from e

        localname = root.tag.split("}")[-1].lower()

        if localname == "usfx":
            return self._parse_usfx(root)
        if localname == "osis":
            return self._parse_osis(root)
        if localname == "bible":
            # Verify it has <testament> as required by Beblia format
            if root.find(".//testament") is not None:
                return self._parse_beblia(root)
            raise ValueError("Unknown <bible> variant: expected Beblia structure with <testament>")
        if localname == "xmlbible":
            return self._parse_zefania(root)

        supported = "USFX, OSIS, BEBLIA, ZEFANIA"
        raise ValueError(
            f"Unsupported XML format: root element is <{localname}>. Supported: {supported}"
        )

    # --- USFX Implementation ---

    def _parse_usfx(self, root: ET.Element) -> list[dict]:
        skip_book_ids = {"FRT", "BAK"}
        all_verses: list[dict] = []
        for book in root.findall("book"):
            book_id = book.get("id", "")
            if book_id in skip_book_ids:
                continue
            all_verses.extend(self._process_usfx_book(book, book_id))
        return all_verses

    def _process_usfx_book(self, book: ET.Element, book_id: str) -> list[dict]:
        verses: list[dict] = []
        chapter = [0]
        skip_inline = {"f", "ref"}

        def collect_text(parent: ET.Element, verse_elem: ET.Element) -> str:
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
                if child.tag in skip_inline:
                    parts.append(child.tail or "")
                else:
                    text_content = "".join(child.itertext())
                    parts.append(text_content + (child.tail or ""))
            return " ".join("".join(parts).split())

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
                    text = collect_text(parent, elem)
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

    # --- OSIS Implementation ---

    def _parse_osis(self, root: ET.Element) -> list[dict]:
        ns = "{http://www.bibletechnologies.net/2003/OSIS/namespace}"
        skip_tags = {f"{ns}note", f"{ns}reference"}

        parent_map: dict[ET.Element, ET.Element] = {}
        for p in root.iter():
            for c in p:
                parent_map[c] = p

        verse_dicts: list[dict] = []

        def collect_container_text(v_elem: ET.Element) -> str:
            p_text: list[str] = []
            for elem in v_elem.iter():
                if elem is v_elem:
                    if elem.text:
                        p_text.append(elem.text)
                elif elem.tag in skip_tags:
                    if elem.tail:
                        p_text.append(elem.tail)
                else:
                    if elem.text:
                        p_text.append(elem.text)
                    if elem.tail:
                        p_text.append(elem.tail)
            return " ".join("".join(p_text).split())

        def collect_milestone_text(parent: ET.Element, s_elem: ET.Element) -> str:
            s_id = s_elem.get("sID")
            if not s_id:
                return ""
            p_text: list[str] = [s_elem.tail or ""]
            found_start = False
            for child in parent:
                if child is s_elem:
                    found_start = True
                    continue
                if not found_start:
                    continue
                if child.tag == f"{ns}verse" and child.get("eID") == s_id:
                    break
                if child.tag in skip_tags:
                    p_text.append(child.tail or "")
                else:
                    p_text.append("".join(child.itertext()) + (child.tail or ""))
            return " ".join("".join(p_text).split())

        for v in root.findall(f".//{ns}verse"):
            osis_id = v.get("osisID")
            s_id = v.get("sID")
            e_id = v.get("eID")

            if (e_id and not osis_id) or not osis_id:
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
                text = collect_milestone_text(parent, v)
            else:
                text = collect_container_text(v)

            verse_dicts.append(
                {"book_id": book_id, "chapter": chapter, "verse": verse, "text": text}
            )

        return verse_dicts

    # --- Beblia Implementation ---

    def _parse_beblia(self, root: ET.Element) -> list[dict]:
        verse_dicts: list[dict] = []
        book_ids = ordered_book_ids()

        for book_elem in root.findall(".//book"):
            try:
                book_num = int(book_elem.get("number", 0))
            except (TypeError, ValueError):
                continue
            if book_num < 1 or book_num > len(book_ids):
                continue
            book_id = book_ids[book_num - 1]

            for chapter_elem in book_elem.findall("chapter"):
                try:
                    chapter = int(chapter_elem.get("number", 0))
                except (TypeError, ValueError):
                    continue
                for verse_elem in chapter_elem.findall("verse"):
                    try:
                        verse = int(verse_elem.get("number", 0))
                    except (TypeError, ValueError):
                        continue
                    text = (verse_elem.text or "").strip()
                    verse_dicts.append(
                        {"book_id": book_id, "chapter": chapter, "verse": verse, "text": text}
                    )
        return verse_dicts

    # --- Zefania Implementation ---

    def _parse_zefania(self, root: ET.Element) -> list[dict]:
        verse_dicts: list[dict] = []
        book_ids = ordered_book_ids()

        for book_elem in root.findall(".//BIBLEBOOK"):
            try:
                book_num = int(book_elem.get("bnumber", 0))
            except (TypeError, ValueError):
                continue
            if book_num < 1 or book_num > len(book_ids):
                continue
            book_id = book_ids[book_num - 1]

            for chapter_elem in book_elem.findall("CHAPTER"):
                try:
                    chapter = int(chapter_elem.get("cnumber", 0))
                except (TypeError, ValueError):
                    continue
                for verse_elem in chapter_elem.findall("VERS"):
                    try:
                        verse = int(verse_elem.get("vnumber", 0))
                    except (TypeError, ValueError):
                        continue
                    if verse < 1:
                        continue
                    text = (verse_elem.text or "").strip()
                    verse_dicts.append(
                        {"book_id": book_id, "chapter": chapter, "verse": verse, "text": text}
                    )
        return verse_dicts
