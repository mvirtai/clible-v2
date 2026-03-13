"""Tests for TranslationRepo.

Covers all CRUD operations: get_all, get_by_id, exists, create, delete, get_default.
Uses in-memory SQLite with full schema via conftest db_conn fixture.
"""

from clible.db.repositories.translation_repo import TranslationRepo


def test_get_all_returns_empty_list_when_no_translations(
    translation_repo: TranslationRepo,
):
    """Fresh database has no translations; get_all returns empty list."""
    result = translation_repo.get_all()
    assert result == []


def test_create_inserts_translation_and_returns_id(translation_repo: TranslationRepo):
    """create() inserts a row and returns the translation id."""
    data = {
        "id": "web",
        "name": "World English Bible",
        "language": "en",
        "format": "USFX",
        "source_url": "https://example.com/web.xml",
    }
    returned_id = translation_repo.create(data)
    assert returned_id == "web"

    all_rows = translation_repo.get_all()
    assert len(all_rows) == 1
    assert all_rows[0]["id"] == "web"
    assert all_rows[0]["name"] == "World English Bible"
    assert all_rows[0]["language"] == "en"
    assert all_rows[0]["format"] == "USFX"
    assert all_rows[0]["source_url"] == "https://example.com/web.xml"
    assert "installed_at" in all_rows[0]


def test_create_accepts_optional_source_url_none(translation_repo: TranslationRepo):
    """create() works when source_url is omitted (defaults to None)."""
    data = {
        "id": "kjv",
        "name": "King James Version",
        "language": "en",
        "format": "OSIS",
    }
    translation_repo.create(data)
    row = translation_repo.get_by_id("kjv")
    assert row["source_url"] is None


def test_get_by_id_returns_none_when_not_found(translation_repo: TranslationRepo):
    """get_by_id returns None for non-existent translation."""
    assert translation_repo.get_by_id("web") is None
    assert translation_repo.get_by_id("") is None


def test_get_by_id_returns_dict_when_found(translation_repo: TranslationRepo):
    """get_by_id returns full row as dict when translation exists."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
            "source_url": None,
        }
    )
    row = translation_repo.get_by_id("web")
    assert row is not None
    assert row["id"] == "web"
    assert row["name"] == "World English Bible"
    assert isinstance(row, dict)


def test_exists_returns_false_when_empty(translation_repo: TranslationRepo):
    """exists() returns False when no translations are installed."""
    assert translation_repo.exists("web") is False


def test_exists_returns_true_after_create(translation_repo: TranslationRepo):
    """exists() returns True after create()."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    assert translation_repo.exists("web") is True
    assert translation_repo.exists("kjv") is False


def test_delete_removes_translation(translation_repo: TranslationRepo):
    """delete() removes the translation; exists and get_by_id reflect removal."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    assert translation_repo.exists("web") is True

    translation_repo.delete("web")
    assert translation_repo.exists("web") is False
    assert translation_repo.get_by_id("web") is None
    assert translation_repo.get_all() == []


def test_delete_on_nonexistent_does_not_raise(translation_repo: TranslationRepo):
    """delete() on non-existent id does not raise."""
    translation_repo.delete("nonexistent")


def test_get_default_returns_none_when_empty(translation_repo: TranslationRepo):
    """get_default() returns None when no translations are installed."""
    assert translation_repo.get_default() is None


def test_get_default_returns_web_when_web_installed(translation_repo: TranslationRepo):
    """get_default() prefers WEB when installed (even if others exist)."""
    translation_repo.create(
        {
            "id": "kjv",
            "name": "King James Version",
            "language": "en",
            "format": "OSIS",
        }
    )
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    default = translation_repo.get_default()
    assert default is not None
    assert default["id"] == "web"


def test_get_default_returns_first_installed_when_web_not_present(
    translation_repo: TranslationRepo,
):
    """get_default() returns first by installed_at when WEB is not installed."""
    translation_repo.create(
        {
            "id": "kjv",
            "name": "King James Version",
            "language": "en",
            "format": "OSIS",
        }
    )
    translation_repo.create(
        {
            "id": "esv",
            "name": "English Standard Version",
            "language": "en",
            "format": "OSIS",
        }
    )
    default = translation_repo.get_default()
    assert default is not None
    assert default["id"] == "kjv"


def test_get_all_ordered_by_installed_at(translation_repo: TranslationRepo):
    """get_all() returns translations ordered by installed_at."""
    translation_repo.create(
        {
            "id": "second",
            "name": "Second",
            "language": "en",
            "format": "USFX",
        }
    )
    translation_repo.create(
        {
            "id": "first",
            "name": "First",
            "language": "en",
            "format": "USFX",
        }
    )
    all_rows = translation_repo.get_all()
    ids = [r["id"] for r in all_rows]
    assert ids == ["second", "first"]


def test_create_returns_plain_dict_not_row(translation_repo: TranslationRepo):
    """Repo returns plain dicts, not sqlite3.Row objects."""
    translation_repo.create(
        {
            "id": "web",
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
        }
    )
    row = translation_repo.get_by_id("web")
    assert type(row).__name__ != "Row"
    assert isinstance(row, dict)
