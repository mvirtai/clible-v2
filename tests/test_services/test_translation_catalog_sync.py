from clible.services.translation_catalog_sync import (
    DiscoveredTranslation,
    infer_beblia_format_and_base,
    infer_openbibles_format_and_base,
    merge_translations_catalog,
    slugify_id,
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
        tid != "foo-usfx"
        and merged[tid].get("filename") == "foo2.osis.xml"
        for tid in merged.keys()
    )

