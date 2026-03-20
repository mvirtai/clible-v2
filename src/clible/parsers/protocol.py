"""Protocol for Bible XML parsers."""

from pathlib import Path
from typing import Protocol


class XMLParserProtocol(Protocol):
    """Protocol for XML parsers that convert Bible XML to verse dicts.

    All parsers must implement parse_file, which takes an XML file path
    and returns a list of verse dictionaries with standardized keys:
    book_id, chapter, verse, text.
    """

    def parse_file(self, xml_path: Path) -> list[dict]:
        """Parse XML file and return verse dicts.

        Args:
            xml_path: Path to the XML file to parse.

        Returns:
            List of dicts with keys: book_id, chapter, verse, text.
        """
        ...
