# feat: add Finnish localization to CLI and web UI

Adds end-to-end Finnish language support across both the CLI and the web
frontend. Builds on the existing translation infrastructure and settings
system introduced in previous PRs.

## Summary

- **book_names.json** — canonical data file with English and Finnish book
  names following Kirkkoraamattu 1992 conventions (long Gospel titles,
  "kirje"-form epistles, "Johanneksen ilmestys" for Revelation). Every
  entry includes KR92 and 1938-style aliases plus abbreviations for search.
- **book_names.py** — new Python utility with `resolve_book_id`,
  `get_display_name`, and `list_books`; enables Finnish verse lookups and
  localized output without touching the repository layer.
- **VerseService** — `_resolve_book` gains a third fallback via
  `resolve_book_id`, so Finnish names and abbreviations (e.g. "joh 3:16")
  resolve correctly.
- **Analytics command** — stopword language is now inferred from the active
  translation when `CLIBLE_ANALYTICS_LANGUAGE` is not set (Finnish
  translations → fi, Greek → grc, else en).
- **Config** — new `ui_language` field (env `CLIBLE_UI_LANGUAGE`, default
  `en`) controls localized book name display in exported files.
- **Export helpers** — scope and shared export utilities use
  `get_display_name` so filenames and section headers render in the
  configured UI language.
- **i18n.ts** — new TypeScript module; single source of truth for all web
  UI strings in English and Finnish. Exports a typed `strings` object and a
  `t(lang)` helper. Finnish plurals handled via function-valued entries.
- **bookNames.ts** — extended with `bookCitationAbbrevFi` and
  `formatReferenceForDisplay`; Finnish headings render as
  "Apostolien teot (Ap. 1:1)".
- **DB migration 002** — adds `ui_language` column to the user settings
  table; persisted per user.
- **All web components** — `App`, `ReaderView`, `SearchPanel`,
  `SearchView`, `SearchStatsPanel`, `AnalyticsView`, `SettingsPanel`,
  `TranslationModal`, `ExportModal`, `SaveSearchButton`,
  `SavedSearchesList`, `BookPickerModal` — accept `uiLanguage` prop and
  source every visible string through `t(uiLanguage)`.

## Files added

| File | Purpose |
|------|---------|
| `src/clible/data/book_names.json` | Canonical book name data (EN + FI KR92, aliases, abbreviations) |
| `src/clible/utils/book_names.py` | Python helpers: resolve, display name, list |
| `tests/test_utils/test_book_names.py` | Unit tests for the Python utility |
| `src/clible-web/data/book_names.json` | Frontend copy of the same data file |
| `src/clible-web/utils/i18n.ts` | Centralised EN/FI string registry and `t()` helper |
| `src/clible-web/db/migrations/002_add_ui_language.sql` | Adds `ui_language` column to user settings |

## Files modified

| File | Change |
|------|--------|
| `src/clible/config.py` | Add `ui_language` field; clean up leftover draft comments |
| `src/clible/commands/analytics.py` | Infer stopword language from active translation |
| `src/clible/services/verse_service.py` | Finnish alias fallback in `_resolve_book` |
| `src/clible/services/analytic_service.py` | Accept inferred stopword language |
| `src/clible/ui/export/scope.py` | Localized book names in export scope headers |
| `src/clible/ui/export/shared.py` | Localized book names in export filenames |
| `src/clible-web/utils/bookNames.ts` | Add `citation_abbr_fi`, `bookCitationAbbrevFi`, `formatReferenceForDisplay` |
| `src/clible-web/user/SettingsContext.tsx` | Expose and persist `uiLanguage` |
| `src/clible-web/user/settings_routes.ts` | Read/write `ui_language` from DB |
| `src/clible-web/App.tsx` | Derive `uiLang`, pass to all children, localize shell strings |
| `src/clible-web/components/*.tsx` | All components: replace hardcoded strings with `t(uiLanguage)` |

## Tests

```bash
uv run pytest -v
```

**315 tests**, all passing. Coverage 90.24% (above the 80% threshold).

```bash
cd src/clible-web && npm run lint   # tsc --noEmit, no errors
```

```bash
uv run ruff check .   # no issues
```

## Usage

```bash
# Finnish verse lookup via CLI alias
uv run clible verse "joh 3:16"
uv run clible verse "Evankeliumi Johanneksen mukaan 3:16"

# Finnish-aware analytics (auto-inferred when using a Finnish translation)
uv run clible analytics reference "joh 3:16"

# Localized exports (set env to fi for Finnish book names in filenames)
CLIBLE_UI_LANGUAGE=fi uv run clible search "rakkaus" --export md
```

In the web UI, switching Interface Language to "Suomi" in Settings
localizes all labels, buttons, and verse reference headings throughout
the application. LoginView is intentionally left in English as it is
shown before user settings are loaded.
