import re
from dataclasses import dataclass
from enum import Enum


class ReferenceScope(Enum):
    BOOK = "book"
    CHAPTER = "chapter"
    VERSE = "verse"


@dataclass
class ParsedReference:
    book_name: str
    chapter: int | None = None
    verse_start: int | None = None
    verse_end: int | None = None
    scope: ReferenceScope = ReferenceScope.BOOK


_VERSE_PATTERN = re.compile(r"^\s*(.+?)\s+(\d+):(\d+)(?:-(\d+))?\s*$")
_CHAPTER_PATTERN = re.compile(r"^\s*(.+?)\s+(\d+)\s*$")


def parse_reference(ref: str) -> ParsedReference | None:
    """Parse Bible reference into ParsedReference object.

    Handles:
    - "John" (Book)
    - "John 3" (Chapter)
    - "John 3:16" (Verse)
    - "John 3:16-18" (Verse range)
    """
    ref = ref.strip()
    if not ref:
        return None

    # Try verse/range first
    m = _VERSE_PATTERN.match(ref)
    if m:
        v_start = int(m.group(3))
        v_end = int(m.group(4)) if m.group(4) is not None else v_start
        return ParsedReference(
            book_name=m.group(1).strip(),
            chapter=int(m.group(2)),
            verse_start=v_start,
            verse_end=v_end,
            scope=ReferenceScope.VERSE,
        )

    # Try chapter
    m = _CHAPTER_PATTERN.match(ref)
    if m:
        return ParsedReference(
            book_name=m.group(1).strip(),
            chapter=int(m.group(2)),
            scope=ReferenceScope.CHAPTER,
        )

    # Default to book
    return ParsedReference(book_name=ref, scope=ReferenceScope.BOOK)
