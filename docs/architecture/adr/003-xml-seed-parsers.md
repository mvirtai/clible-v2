# ADR-003: XML seed parsers instead of a live API

**Status:** Accepted  
**Date:** 2025

---

## Context

Public domain Bible translations are available in several XML formats from open repositories (notably [seven1m/open-bibles](https://github.com/seven1m/open-bibles) and [Beblia/Holy-Bible-XML-Format](https://github.com/Beblia/Holy-Bible-XML-Format)). These cover USFX, OSIS, Beblia, and Zefania schemas — four distinct XML dialects used by different Bible software communities.

The early project design considered using bible-api.com as a live API. That approach was rejected because it would introduce a network dependency for every verse lookup (see ADR-001).

## Decision

Bible text is ingested via **XML file parsers** at seed time, not fetched at query time. The seeding flow:

1. `clible seed install <id>` downloads the XML file from a GitHub URL (listed in `translations.json`)
2. The `CombinedParser` detects the root element of the XML file to identify the format (USFX/OSIS/Beblia/Zefania)
3. The appropriate sub-parser extracts `{book_id, chapter, verse, text}` dicts
4. `SeedService` bulk-inserts the dicts into SQLite via `VerseRepo`

A single entry point (`CombinedParser.parse_file(path)`) handles all formats. This means the service and seed command do not need to know which format a translation uses.

The `xml.etree.ElementTree` module from the Python standard library is used for parsing — no additional XML dependency needed.

## Consequences

**Positive:**
- Network is only needed once (at seed time); all subsequent operations are offline
- Adding a new translation is purely a data concern: add an entry to `translations.json` and run `seed install`
- Supporting a new XML format requires adding one sub-parser under `CombinedParser` — no changes to the service or command layer
- Standard library XML parsing avoids adding a dependency

**Negative:**
- Translations are not automatically kept up to date; users must re-run `seed install` to pick up new source versions
- Large translations (e.g. full Bible, ~1 MB XML) take a few seconds to parse and insert on first seed
- Book ID normalisation across formats requires a mapping table (`osis_book_map.py`) and occasional edge-case handling

**Trade-off accepted:** The infrequency of seeding (once per translation, occasionally to update) makes the one-time cost acceptable. The offline benefit outweighs the maintenance overhead of format handling.
