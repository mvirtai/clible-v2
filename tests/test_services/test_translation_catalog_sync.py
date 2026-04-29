from clible.services.translation_catalog_sync import (
    DiscoveredTranslation,
    TranslationCatalogSyncError,
    _bytes_to_mb,
    _fetch_github_tree,
    discover_beblia_translations,
    discover_openbibles_translations,
    guess_language_from_beblia_base,
    guess_language_from_openbibles_base,
    infer_beblia_format_and_base,
    infer_openbibles_format_and_base,
    merge_translations_catalog,
    slugify_id,
    sync_translations_catalog,
)


def test_infer_openbibles_format_and_base_usfx():
    fmt_base = infer_openbibles_format_and_base("eng-web.usfx.xml")
    assert fmt_base == ("USFX", "eng-web")


def test_infer_openbibles_format_and_base_osis():
    fmt_base = infer_openbibles_format_and_base("dan-danish.osis.xml")
    assert fmt_base == ("OSIS", "dan-danish")


def test_infer_openbibles_format_and_base_zefania():
    fmt_base = infer_openbibles_format_and_base("cze-bkr.zefania.xml")
    assert fmt_base == ("ZEFANIA", "cze-bkr")


def test_infer_beblia_format_and_base():
    fmt_base = infer_beblia_format_and_base("Finnish1992Bible.xml")
    assert fmt_base == ("BEBLIA", "Finnish1992")


def test_merge_preserves_existing_id_by_filename():
    existing = {
        "web": {
            "name": "World English Bible",
            "language": "en",
            "format": "USFX",
            "filename": "eng-web.usfx.xml",
            "url": "https://old.example/eng-web.usfx.xml",
            "size_mb": 4.2,
        }
    }

    discovered = [
        DiscoveredTranslation(
            id=None,
            name="New Name From Remote",
            language="should_not_override",
            format="USFX",
            filename="eng-web.usfx.xml",
            url="https://raw.githubusercontent.com/seven1m/open-bibles/master/eng-web.usfx.xml",
            size_mb=1.1,
            base="eng-web",
        )
    ]

    merged = merge_translations_catalog(existing, discovered)
    assert "web" in merged
    assert merged["web"]["name"] == "World English Bible"  # preserved
    assert merged["web"]["language"] == "en"  # preserved
    assert merged["web"]["url"] == discovered[0].url
    assert merged["web"]["size_mb"] == discovered[0].size_mb


def test_merge_generates_new_id_for_unknown_filename():
    existing = {}
    base = "deu-luther1912"
    discovered = [
        DiscoveredTranslation(
            id=None,
            name="German Luther 1912",
            language="de",
            format="OSIS",
            filename="deu-luther1912.osis.xml",
            url="https://example.com/deu-luther1912.osis.xml",
            size_mb=0.0,
            base=base,
        )
    ]

    merged = merge_translations_catalog(existing, discovered)
    generated_id = slugify_id(base)
    assert generated_id in merged
    assert merged[generated_id]["format"] == "OSIS"
    assert merged[generated_id]["filename"] == "deu-luther1912.osis.xml"


def test_merge_avoids_id_collision_by_suffix():
    # Force a collision: both discovered items slugify to the same ID.
    existing = {
        "foo-usfx": {
            "name": "Existing Foo",
            "language": "en",
            "format": "USFX",
            "filename": "foo.usfx.xml",
            "url": "https://example.com/foo.usfx.xml",
            "size_mb": 0.0,
        }
    }

    # This will slugify `foo` to `foo`, and then collide on `foo` (not in existing),
    # so we explicitly set the base to `foo-usfx` to cause collision on that generated ID.
    discovered = [
        DiscoveredTranslation(
            id=None,
            name="Other Translation",
            language="en",
            format="OSIS",
            filename="foo2.osis.xml",
            url="https://example.com/foo2.osis.xml",
            size_mb=0.0,
            base="foo-usfx",
        )
    ]

    merged = merge_translations_catalog(existing, discovered)
    assert "foo-usfx" in merged
    # Collision should have happened; because the filename differs, it must get a suffix.
    assert any(
        tid != "foo-usfx" and merged[tid].get("filename") == "foo2.osis.xml"
        for tid in merged.keys()
    )


def test_bytes_to_mb_rounding_and_invalid_values():
    assert _bytes_to_mb(0) == 0.0
    assert _bytes_to_mb(-1) == 0.0
    assert _bytes_to_mb("oops") == 0.0
    assert _bytes_to_mb(1024 * 1024) == 1.0


def test_guess_language_helpers():
    assert guess_language_from_openbibles_base("fin-1992") == "fi"
    assert guess_language_from_openbibles_base("xyz-demo") == "xy"
    assert guess_language_from_beblia_base("Finnish1992") == "fi"
    assert guess_language_from_beblia_base("UnknownLanguageBible") == "en"


def test_fetch_github_tree_raises_on_invalid_shape(mocker):
    response = mocker.Mock()
    response.json.return_value = {"not_tree": []}
    response.raise_for_status.return_value = None
    mock_get = mocker.patch("clible.services.translation_catalog_sync.requests.get")
    mock_get.return_value = response

    try:
        _fetch_github_tree(
            owner="owner",
            repo="repo",
            ref="main",
            github_token="token123",
            timeout_seconds=30,
        )
        assert False, "Expected TranslationCatalogSyncError"
    except TranslationCatalogSyncError as exc:
        assert "Unexpected GitHub API response shape" in str(exc)

    headers = mock_get.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer token123"


def test_discover_openbibles_translations_filters_tree_entries(mocker):
    mocker.patch(
        "clible.services.translation_catalog_sync._fetch_github_tree",
        return_value=[
            {"type": "tree", "path": "folder"},
            {"type": "blob", "path": "eng-web.usfx.xml", "size": 1048576},
            {"type": "blob", "path": "README.md", "size": 100},
            {"type": "blob", "path": ""},
        ],
    )

    discovered = discover_openbibles_translations(github_token=None, timeout_seconds=5)

    assert len(discovered) == 1
    item = discovered[0]
    assert item.format == "USFX"
    assert item.base == "eng-web"
    assert item.language == "en"
    assert item.size_mb == 1.0
    assert item.url.endswith("/eng-web.usfx.xml")


def test_discover_beblia_translations_only_includes_bible_xml(mocker):
    mocker.patch(
        "clible.services.translation_catalog_sync._fetch_github_tree",
        return_value=[
            {"type": "blob", "path": "Finnish1992Bible.xml", "size": 2097152},
            {"type": "blob", "path": "notes.xml", "size": 123},
            {"type": "blob", "path": "README.md", "size": 123},
        ],
    )

    discovered = discover_beblia_translations(github_token=None, timeout_seconds=5)

    assert len(discovered) == 1
    item = discovered[0]
    assert item.format == "BEBLIA"
    assert item.base == "Finnish1992"
    assert item.language == "fi"
    assert item.size_mb == 2.0


def test_sync_translations_catalog_writes_merged_output(tmp_path, mocker):
    catalog_path = tmp_path / "translations.json"
    catalog_path.write_text(
        """{
  "web": {
    "name": "World English Bible",
    "language": "en",
    "format": "USFX",
    "filename": "eng-web.usfx.xml",
    "url": "https://old.example/eng-web.usfx.xml",
    "size_mb": 4.2
  }
}
""",
        encoding="utf-8",
    )

    mocker.patch(
        "clible.services.translation_catalog_sync.discover_openbibles_translations",
        return_value=[
            DiscoveredTranslation(
                id=None,
                name="WEB",
                language="en",
                format="USFX",
                filename="eng-web.usfx.xml",
                url="https://new.example/eng-web.usfx.xml",
                size_mb=4.3,
                base="eng-web",
            )
        ],
    )
    mocker.patch(
        "clible.services.translation_catalog_sync.discover_beblia_translations",
        return_value=[
            DiscoveredTranslation(
                id=None,
                name="Finnish 1992",
                language="fi",
                format="BEBLIA",
                filename="Finnish1992Bible.xml",
                url="https://new.example/Finnish1992Bible.xml",
                size_mb=5.0,
                base="Finnish1992",
            )
        ],
    )

    result = sync_translations_catalog(
        catalog_path=catalog_path, github_token=None, timeout_seconds=5
    )

    assert result == {"existing_count": 1, "discovered_count": 2, "merged_count": 2}
    content = catalog_path.read_text(encoding="utf-8")
    assert '"web"' in content
    assert "Finnish1992Bible.xml" in content


def test_sync_translations_catalog_raises_when_file_missing(tmp_path):
    missing_path = tmp_path / "missing.json"
    try:
        sync_translations_catalog(
            catalog_path=missing_path, github_token=None, timeout_seconds=5
        )
        assert False, "Expected TranslationCatalogSyncError"
    except TranslationCatalogSyncError as exc:
        assert "Catalog file not found" in str(exc)
