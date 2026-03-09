"""Tests for SeedService."""

from pathlib import Path
from unittest.mock import patch

import pytest

from clible.parsers.beblia_parser import BebliaParser
from clible.parsers.osis_parser import OSISParser
from clible.parsers.usfx_parser import USFXParser
from clible.services.seed_service import SeedService


@pytest.fixture
def seed_service(translation_repo, verse_repo, book_repo):
    """SeedService with real parsers and repo fixtures."""
    return SeedService(
        translation_repo=translation_repo,
        verse_repo=verse_repo,
        book_repo=book_repo,
        usfx_parser=USFXParser(),
        osis_parser=OSISParser(),
        beblia_parser=BebliaParser(),
    )


def test_list_available_returns_catalog(seed_service):
    """list_available returns translations from catalog."""
    result = seed_service.list_available()
    assert len(result) >= 1
    web = next((t for t in result if t["id"] == "web"), None)
    assert web is not None
    assert web["name"] == "World English Bible"
    assert web["format"] == "USFX"
    assert "url" in web


def test_list_installed_returns_empty_when_none(seed_service):
    """list_installed returns empty list when no translations installed."""
    assert seed_service.list_installed() == []


def test_seed_translation_downloads_parses_and_saves(seed_service, verse_repo):
    """seed_translation downloads XML, parses, and saves verses."""
    sample_xml = (Path(__file__).parent.parent / "fixtures" / "sample.usfx.xml").read_bytes()

    with patch("clible.services.seed_service.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = sample_xml
        mock_get.return_value.raise_for_status = lambda: None

        result = seed_service.seed_translation("web")

    assert result["translation_id"] == "web"
    assert result["verses_installed"] == 5
    assert result["duration_seconds"] >= 0

    verse = verse_repo.get_verse("web", "JHN", 1, 1)
    assert verse is not None
    assert "In the beginning was the Word" in verse["text"]


def test_seed_translation_raises_if_unknown(seed_service):
    """seed_translation raises ValueError for unknown translation_id."""
    with pytest.raises(ValueError, match="Unknown translation"):
        seed_service.seed_translation("nonexistent")


def test_seed_translation_raises_if_already_installed(seed_service):
    """seed_translation raises ValueError if translation already installed."""
    sample_xml = (Path(__file__).parent.parent / "fixtures" / "sample.usfx.xml").read_bytes()

    with patch("clible.services.seed_service.requests.get") as mock_get:
        mock_get.return_value.content = sample_xml
        mock_get.return_value.raise_for_status = lambda: None

        seed_service.seed_translation("web")

    with pytest.raises(ValueError, match="already installed"):
        seed_service.seed_translation("web")


def test_seed_translation_raises_for_unsupported_format(seed_service):
    """seed_translation raises ValueError for formats other than USFX/OSIS/BEBLIA."""
    fake_catalog = {
        "bad": {
            "name": "Bad",
            "language": "en",
            "format": "Zefania",
            "url": "http://example.com/bad.xml",
        },
    }
    with patch(
        "clible.services.seed_service._load_translations_catalog",
        return_value=fake_catalog,
    ):
        with pytest.raises(ValueError, match="not supported"):
            seed_service.seed_translation("bad")


def test_seed_translation_osis_fin_biblia_succeeds(seed_service, verse_repo):
    """seed_translation with OSIS format (e.g. fin-biblia-33-38) downloads, parses, saves."""
    sample_osis = (Path(__file__).parent.parent / "fixtures" / "sample.osis.xml").read_bytes()

    with patch("clible.services.seed_service.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = sample_osis
        mock_get.return_value.raise_for_status = lambda: None

        result = seed_service.seed_translation("fin-biblia-33-38")

    assert result["translation_id"] == "fin-biblia-33-38"
    assert result["verses_installed"] == 5
    assert result["duration_seconds"] >= 0

    verse = verse_repo.get_verse("fin-biblia-33-38", "GEN", 1, 1)
    assert verse is not None
    assert "Alussa loi Jumala" in verse["text"]


def test_seed_translation_beblia_fin_1992_succeeds(seed_service, verse_repo):
    """seed_translation with BEBLIA format (e.g. fin-1992) downloads, parses, saves."""
    sample_beblia = (Path(__file__).parent.parent / "fixtures" / "sample.beblia.xml").read_bytes()

    with patch("clible.services.seed_service.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = sample_beblia
        mock_get.return_value.raise_for_status = lambda: None

        result = seed_service.seed_translation("fin-1992")

    assert result["translation_id"] == "fin-1992"
    assert result["verses_installed"] == 2
    assert result["duration_seconds"] >= 0

    verse = verse_repo.get_verse("fin-1992", "GEN", 1, 1)
    assert verse is not None
    assert "Alussa Jumala loi taivaan ja maan" in verse["text"]


def test_remove_translation_deletes_and_cascades(seed_service, verse_repo):
    """remove_translation deletes translation and verses."""
    sample_xml = (Path(__file__).parent.parent / "fixtures" / "sample.usfx.xml").read_bytes()

    with patch("clible.services.seed_service.requests.get") as mock_get:
        mock_get.return_value.content = sample_xml
        mock_get.return_value.raise_for_status = lambda: None
        seed_service.seed_translation("web")

    seed_service.remove_translation("web")
    assert verse_repo.get_verse("web", "JHN", 1, 1) is None
    assert seed_service.list_installed() == []


def test_remove_translation_raises_if_not_installed(seed_service):
    """remove_translation raises ValueError for non-installed translation."""
    with pytest.raises(ValueError, match="not installed"):
        seed_service.remove_translation("web")


def test_seed_translation_uses_seed_base_url_when_set(seed_service, verse_repo):
    """When CLIBLE_SEED_BASE_URL is set, seed fetches from base_url + filename."""
    sample_xml = (Path(__file__).parent.parent / "fixtures" / "sample.usfx.xml").read_bytes()
    base_url = "https://storage.googleapis.com/my-bucket/seed"

    mock_config = patch("clible.services.seed_service.get_config")
    mock_get = patch("clible.services.seed_service.requests.get")

    with mock_config as m_config:
        cfg = m_config.return_value
        cfg.seed_base_url = base_url
        with mock_get as m_get:
            m_get.return_value.status_code = 200
            m_get.return_value.content = sample_xml
            m_get.return_value.raise_for_status = lambda: None

            seed_service.seed_translation("web")

    call_args = m_get.call_args
    assert call_args[0][0] == f"{base_url}/eng-web.usfx.xml"
