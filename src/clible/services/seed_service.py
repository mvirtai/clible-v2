"""Seed service: download, parse, and install Bible translations."""

import json
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

import requests

if TYPE_CHECKING:
    from clible.db.repositories.book_repo import BookRepo
    from clible.db.repositories.translation_repo import TranslationRepo
    from clible.db.repositories.verse_repo import VerseRepo


# USFX book_id variants that map to canonical books table (ENG-WEB uses NAM for Nahum)
_BOOK_ID_ALIASES = {"NAM": "NAH"}


class USFXParserProtocol(Protocol):
    """Protocol for XML parsers that return verse dicts (USFX, OSIS)."""

    def parse_file(self, xml_path: Path) -> list[dict]:
        """Parse XML file. Returns list of verse dicts with book_id, chapter, verse, text."""
        ...


_SUPPORTED_FORMATS = ("USFX", "OSIS", "BEBLIA")


def _load_translations_catalog() -> dict:
    """Load translations catalog from data dir."""
    catalog_path = Path(__file__).resolve().parent.parent / "data" / "translations.json"
    with open(catalog_path, encoding="utf-8") as f:
        return json.load(f)


class SeedService:
    """Orchestrates translation seeding: download, parse, save."""

    def __init__(
        self,
        translation_repo: "TranslationRepo",
        verse_repo: "VerseRepo",
        book_repo: "BookRepo",
        usfx_parser: USFXParserProtocol,
        osis_parser: USFXParserProtocol,
        beblia_parser: USFXParserProtocol,
    ):
        """Initialize with injected repositories and parsers (USFX, OSIS, Beblia)."""
        self._translation_repo = translation_repo
        self._verse_repo = verse_repo
        self._book_repo = book_repo
        self._usfx_parser = usfx_parser
        self._osis_parser = osis_parser
        self._beblia_parser = beblia_parser

    def list_available(self) -> list[dict]:
        """List all translations from the catalog.

        Returns:
            List of dicts with id, name, language, format, url, size_mb.
        """
        catalog = _load_translations_catalog()
        return [
            {"id": tid, **{k: v for k, v in meta.items() if k != "filename"}}
            for tid, meta in catalog.items()
        ]

    def list_installed(self) -> list[dict]:
        """List installed translations from the database."""
        return self._translation_repo.get_all()

    def remove_translation(self, translation_id: str) -> None:
        """Uninstall a translation. Verses are removed via CASCADE."""
        if not self._translation_repo.exists(translation_id):
            raise ValueError(f"Translation '{translation_id}' is not installed")
        self._translation_repo.delete(translation_id)

    def seed_translation(
        self,
        translation_id: str,
        *,
        progress_callback: Callable[[str], None] | None = None,
    ) -> dict:
        """Download, parse, and install a translation.

        Args:
            translation_id: Catalog id (e.g. 'web').

        Returns:
            Stats dict: translation_id, verses_installed, duration_seconds.

        Raises:
            ValueError: If translation_id not in catalog, already installed,
                or format is not USFX, OSIS, or BEBLIA.
        """
        catalog = _load_translations_catalog()
        if translation_id not in catalog:
            raise ValueError(f"Unknown translation: {translation_id}")

        meta = catalog[translation_id]
        if self._translation_repo.exists(translation_id):
            raise ValueError(f"Translation '{translation_id}' is already installed")

        fmt = meta.get("format")
        if fmt == "USFX":
            parser = self._usfx_parser
        elif fmt == "OSIS":
            parser = self._osis_parser
        elif fmt == "BEBLIA":
            parser = self._beblia_parser
        else:
            raise ValueError(
                f"Format '{fmt}' not supported (supported: {', '.join(_SUPPORTED_FORMATS)})"
            )

        url = meta["url"]
        start = time.monotonic()
        report = progress_callback or (lambda m: None)

        report("Downloading...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        report("Parsing XML...")
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=True) as tmp:
            tmp.write(response.content)
            tmp.flush()
            verses = parser.parse_file(Path(tmp.name))

        valid_book_ids = {b["id"] for b in self._book_repo.get_all()}
        filtered = []
        for v in verses:
            book_id = _BOOK_ID_ALIASES.get(v["book_id"], v["book_id"])
            if book_id in valid_book_ids:
                filtered.append({**v, "book_id": book_id})
        verses = filtered

        report("Saving verses...")
        translation_data = {
            "id": translation_id,
            "name": meta["name"],
            "language": meta["language"],
            "format": meta["format"],
            "source_url": meta.get("url"),
        }
        self._translation_repo.create(translation_data, commit=False)
        count = self._verse_repo.save_verses(verses, translation_id)

        duration = time.monotonic() - start
        return {
            "translation_id": translation_id,
            "verses_installed": count,
            "duration_seconds": round(duration, 2),
        }
