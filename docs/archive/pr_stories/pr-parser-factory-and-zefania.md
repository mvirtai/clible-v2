# feat: parser factory, Zefania seed support, catalog fixture entry

This PR simplifies seed wiring around XML parsing, adds first-class Zefania support, and documents a manual CLI path to install a Zefania fixture via `clible seed install`.

## Summary

- Introduced `XMLParserProtocol` and `create_parser()`: detect format from the XML root element local name and return the correct parser instance (USFX, OSIS, Beblia, Zefania).
- Refactored `SeedService` to take a single `parser_factory` dependency instead of three parser objects; catalog `format` is still validated (case-insensitive), parsing is delegated to the factory.
- Added `ZefaniaParser` for Zefania-style XML (`XMLBIBLE` → `BIBLEBOOK` / `CHAPTER` / `VERS`).
- Added and updated tests: factory detection + negative paths, Zefania parser behaviour, seed service with the new factory.
- Extended the seed catalog with `test-zefania` pointing at `sample.zefania.xml` for local HTTP-based manual verification.

## Files added

- `src/clible/parsers/protocol.py` — shared `parse_file(Path) -> list[dict]` protocol.
- `src/clible/parsers/factory.py` — format detection and parser construction.
- `src/clible/parsers/zefania_parser.py` — Zefania XML → verse dicts.
- `tests/fixtures/sample.zefania.xml` — small Zefania fixture.
- `tests/test_parsers/test_factory.py` — factory tests for all supported fixtures plus error cases.
- `tests/test_parsers/test_zefania_parser.py` — Zefania parser tests.

## Files modified

- `src/clible/parsers/__init__.py` — public exports: `XMLParserProtocol`, `create_parser`.
- `src/clible/services/seed_service.py` — `parser_factory` injection, `_SUPPORTED_FORMATS` includes `ZEFANIA`, normalized format check.
- `src/clible/commands/seed.py` — wires `create_parser` into `SeedService`.
- `tests/test_services/test_seed_service.py` — fixture uses `create_parser`; unsupported-format test updated.
- `src/clible/data/translations.json` — `test-zefania` catalog entry for manual seed install.

## Tests

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -v
```

`uv run pytest -v` — **197 tests**, all passing.

## Usage

Serve the fixture directory locally, then install using `CLIBLE_SEED_BASE_URL` so the download URL resolves to your `filename` under that base:

```bash
# Terminal A: serve tests/fixtures
cd tests/fixtures
python -m http.server 8000

# Terminal B: install catalog id test-zefania
CLIBLE_SEED_BASE_URL=http://localhost:8000 uv run clible seed install test-zefania

# Verify
uv run clible verse "John 1:1" -t test-zefania
```

Re-install requires removal first:

```bash
uv run clible seed remove test-zefania
```
