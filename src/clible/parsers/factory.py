"""Factory for creating appropriate XML parser based on file format."""

import xml.etree.ElementTree as ET
from pathlib import Path

from clible.parsers.beblia_parser import BebliaParser
from clible.parsers.osis_parser import OSISParser
from clible.parsers.protocol import XMLParserProtocol
from clible.parsers.usfx_parser import USFXParser


def create_parser(xml_path: Path) -> XMLParserProtocol:
    """Detect XML format and return appropriate parser instance.

    Inspects the root element tag to determine format:
    - <usfx> → USFXParser
    - <osis> → OSISParser
    - <bible> with <testament> → BebliaParser
    - <XMLBIBLE> → ZefaniaParser

    Args:
        xml_path: Path to XML file to parse.

    Returns:
        Parser instance for the detected format.

    Raises:
        ValueError: If format cannot be determined or is not supported.
        ET.ParseError: If XML is malformed.
    """
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML file: {e}") from e

    root = tree.getroot()
    localname = root.tag.split("}")[-1].lower()

    if localname == "usfx":
        return USFXParser()
    elif localname == "osis":
        return OSISParser()
    elif localname == "bible":
        if root.find(".//testament") is not None:
            return BebliaParser()
        else:
            raise ValueError(
                "Unknown <bible> format variant: expected Beblia structure with <testament>"
            )
    elif localname == "xmlbible":
        from clible.parsers.zefania_parser import ZefaniaParser

        return ZefaniaParser()
    else:
        raise ValueError(
            f"Unsupported XML format: root element is <{localname}>. "
            f"Supported formats: USFX, OSIS, BEBLIA, ZEFANIA"
        )
