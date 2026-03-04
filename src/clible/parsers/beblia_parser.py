"""Beblia XML format parser.

Beblia (https://github.com/Beblia/Holy-Bible-XML-Format) uses a simple structure:
<bible><testament><book number="1..66"><chapter number="N"><verse number="N">text</verse>
Book number is canonical order: 1=Genesis, 66=Revelation. We map to clible book IDs
using the same order as bible_structure.json.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path


def _ordered_book_ids() -> list[str]:
    """Return clible book IDs in canonical order (position 1-66)."""
    path = Path(__file__).resolve().parent.parent / "data" / "bible_structure.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    books = sorted(data["books"], key=lambda b: b["position"])
    return [b["id"] for b in books]


_BOOK_IDS = _ordered_book_ids()


class BebliaParser:
    """Parse Beblia XML into verse dicts.

    Expects structure: bible > testament > book[@number] > chapter[@number] > verse[@number].
    Returns list of dicts with keys: book_id, chapter, verse, text.
    """

    def parse_file(self, xml_path: Path) -> list[dict]:
        """Parse a Beblia XML file into verse dicts.

        Args:
            xml_path: Path to the XML file.

        Returns:
            List of dicts with book_id, chapter, verse, text. Skips books whose
            number is out of range (1-66).
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()

        verse_dicts: list[dict] = []

        for book_elem in root.findall(".//book"):
            try:
                book_num = int(book_elem.get("number", 0))
            except (TypeError, ValueError):
                continue
            if book_num < 1 or book_num > len(_BOOK_IDS):
                continue
            book_id = _BOOK_IDS[book_num - 1]

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
                        {
                            "book_id": book_id,
                            "chapter": chapter,
                            "verse": verse,
                            "text": text,
                        }
                    )

        return verse_dicts
