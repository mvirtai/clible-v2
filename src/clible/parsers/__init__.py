"""XML parsers for Bible text formats."""

from clible.parsers.factory import create_parser
from clible.parsers.protocol import XMLParserProtocol

__all__ = ["XMLParserProtocol", "create_parser"]
