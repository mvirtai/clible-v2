# PR: feat: Finnish localization for CLI and web UI

## Summary

This PR delivers end-to-end Finnish language support across the CLI and the web frontend. On the backend it introduces a `book_names.json` data file with canonical Finnish book names following Kirkkoraamattu 1992 conventions, a Python utility module for name resolution and display, and wiring that lets the analytics command infer its stopword language automatically from the active translation. On the frontend it introduces a centralized `i18n.ts` string registry and updates every visible component so all labels, buttons, and verse reference headings adapt to the user's chosen interface language.

## Purpose

- Finnish users could not look up verses using Finnish book names or abbreviations; the resolver only matched English and database-stored names.
- All web UI strings were hardcoded in English with no path to localization. Adding a second language required touching every component individually.
- Analytics stopword filtering always defaulted to English even when the active translation was Finnish, producing poor word-frequency results for Finnish text.
- Exported files used raw book IDs in filenames and section headers regardless of the user's language.

## Changes in This PR

### 1. Book name data (`src/clible/data/book_names.json`, `src/clible-web/data/book_names.json`)

A single JSON file (shared between CLI and web) holds canonical English and Finnish book names, search aliases, and abbreviation fields for all 66 books. Finnish names follow KR92: Gospels use the long "Evankeliumi … mukaan" form; epistles use the "… kirje …" form; Revelation is "Johanneksen ilmestys". Each entry also carries 1938-style alternative names and common abbreviations as `aliases_fi` so searches in either spelling tradition resolve correctly.

### 2. Python book name utility (`src/clible/utils/book_names.py`)

Three public helpers: `resolve_book_id` converts any raw string (English name, Finnish name, alias, abbreviation) to a canonical three-letter book ID; `get_display_name` returns the localized display name for a given ID; `list_books` iterates all known IDs. The module sits in the utility layer and has no dependency on the database or any service.

### 3. CLI wiring — verse lookup and exports

`VerseService._resolve_book` gains a third lookup pass via `resolve_book_id`, so Finnish names ("joh 3:16", "Evankeliumi Johanneksen mukaan 3:16") now resolve without changes to the repository layer. Export scope and shared helpers call `get_display_name` so filenames and section headers render in the configured UI language (`CLIBLE_UI_LANGUAGE` env var, default `en`).

### 4. Analytics stopword inference (`src/clible/commands/analytics.py`)

When `CLIBLE_ANALYTICS_LANGUAGE` is not set, the analytics command now infers the stopword language from the active translation: Finnish translations select `fi`, Greek/Ancient Greek select `grc`, everything else falls back to `en`. Setting the env var still overrides the inference.

### 5. Web i18n infrastructure (`src/clible-web/utils/i18n.ts`, `src/clible-web/utils/bookNames.ts`)

`i18n.ts` is the single source of truth for all UI strings. It exports a typed `strings` object with `en` and `fi` keys and a `t(lang)` helper that returns the correct message set. Function-valued entries handle Finnish plurals (e.g. `searchUniqueVerses` returns "1 ainutlaatuinen jae" vs "N ainutlaatuista jaetta"). `bookNames.ts` is extended with `bookCitationAbbrevFi` for heading abbreviations and `formatReferenceForDisplay`, which renders Finnish references as "Apostolien teot (Ap. 1:1)" while keeping the canonical `BOOK chapter:verse` format internally.

### 6. User settings persistence (`src/clible-web/db/migrations/002_add_ui_language.sql`, `SettingsContext`, `settings_routes.ts`)

A new DB migration adds `ui_language` to the user settings table. `SettingsContext` and the settings API route read and write this field so the chosen interface language survives page reloads and is scoped per user.

### 7. Web components

All eleven components that render user-visible text — `App`, `ReaderView`, `SearchPanel`, `SearchView`, `SearchStatsPanel`, `AnalyticsView`, `SettingsPanel`, `TranslationModal`, `ExportModal`, `SaveSearchButton`, `SavedSearchesList`, and `BookPickerModal` — now accept a `uiLanguage` prop and source every string through `t(uiLanguage)`. `LoginView` is intentionally left in English because it is shown before any user settings are available.

### 8. Tests

New unit tests cover `resolve_book_id` with English names, Finnish KR92 and 1938-style aliases, abbreviations, numeric-prefix books (1CO, 2KI), and unknown inputs. Existing service tests are extended to cover the Finnish alias lookup path in `VerseService` and the stopword inference in the analytics command.

## Files added

- `src/clible/data/book_names.json` — canonical book name data (EN + FI, aliases, abbreviations).
- `src/clible/utils/book_names.py` — Python helpers: `resolve_book_id`, `get_display_name`, `list_books`.
- `tests/test_utils/test_book_names.py` — unit tests for the above.
- `src/clible-web/data/book_names.json` — frontend copy of the same data file.
- `src/clible-web/utils/i18n.ts` — centralised EN/FI string registry and `t()` helper.
- `src/clible-web/db/migrations/002_add_ui_language.sql` — adds `ui_language` column to user settings.

## Files modified

- `src/clible/config.py` — add `ui_language` field (`CLIBLE_UI_LANGUAGE`); remove leftover draft markers.
- `src/clible/commands/analytics.py` — stopword language inference from active translation.
- `src/clible/services/verse_service.py` — Finnish alias fallback in `_resolve_book`.
- `src/clible/services/analytic_service.py` — accept externally inferred stopword language.
- `src/clible/ui/export/scope.py` / `shared.py` — localized book names in export output.
- `src/clible-web/utils/bookNames.ts` — `citation_abbr_fi`, `bookCitationAbbrevFi`, `formatReferenceForDisplay`.
- `src/clible-web/user/SettingsContext.tsx` / `settings_routes.ts` — expose and persist `uiLanguage`.
- `src/clible-web/App.tsx` — derive `uiLang`, pass to all children, localize shell strings.
- `src/clible-web/components/*.tsx` — all components: replace hardcoded strings with `t(uiLanguage)`.

## Tests

```bash
uv run pytest -v
uv run ruff check .
uv run ruff format --check .
cd src/clible-web && npm run lint
```

**315** pytest tests, all passing. Coverage 90.24% (gate ≥ 80%). TypeScript compiles without errors (`tsc --noEmit`).

## Usage

```bash
# Finnish verse lookup — both Finnish name and abbreviation resolve
uv run clible verse "joh 3:16"
uv run clible verse "Evankeliumi Johanneksen mukaan 3:16"
uv run clible verse "ilm 1:1"   # Johanneksen ilmestys

# Analytics auto-selects Finnish stopwords when the active translation is Finnish
uv run clible analytics reference "joh 3:16"

# Localized exports (Finnish book names in filenames and section headers)
CLIBLE_UI_LANGUAGE=fi uv run clible search "rakkaus" --export md
```

In the web UI, open Settings and switch Interface Language to "Suomi". All labels, navigation, search options, and verse reference headings update immediately.

## Notes

- The `LoginView` is out of scope for localization. It is rendered before the user's settings are fetched so there is no `uiLanguage` available at that point.
- The `book_names.json` file is the single data source shared by both the CLI Python code and the web TypeScript code. Changes to book names or aliases should be made once and the frontend copy updated in sync.
- Repository layer remains free of any locale logic per project architecture; localization happens at the service and UI boundaries.

## Related documentation

- `ROADMAP.md` — Finnish locale support item.
- `src/clible/data/book_names.json` — primary data source for names, aliases, and abbreviations.
