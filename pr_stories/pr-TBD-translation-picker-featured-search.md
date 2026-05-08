# PR: feat(web): improve translation picker with featured list, search, and safer installs

## Summary

This PR improves the web translation picker so users can find and install translations reliably: it adds a featured section for the most important EN/FI/original-language packs, limits the default browse list to keep the UI scannable, and introduces a simple server-backed search. It also hardens translation installs by surfacing install feedback in the Original Study setup, switching the default Hebrew install pack to a working catalog entry, and hiding the known-broken `heb-leningrad` pack from the public UI.

## Purpose

- The translation catalog is large, making the picker hard to scan without prioritization or search.
- Installing original-language packs could fail silently or feel confusing without clear feedback.
- `heb-leningrad` is present in the catalog but its upstream XML is malformed (install fails), so it should not be offered in the public UI.

## Changes in This PR

### 1. Translation picker UX: featured, browse limit, and search (`src/clible-web/components/TranslationModal.tsx`, `src/clible-web/App.tsx`, `src/clible-web/utils/i18n.ts`)

The picker now renders a pinned **Featured** section (EN/FI + Koine Greek + Hebrew) and keeps the default **Browse** section to a Top-N subset, with results sorted to prefer the current UI language. A search input at the top queries the server-side catalog via `/api/translations/available?query=` (debounced) so users can find translations by id/name/language without scrolling through the full list.

### 2. Install safety and original-language defaults (`src/clible-web/components/OriginalStudyView.tsx`, `src/clible-web/services/originalStudyPayload.ts`, `src/clible-web/App.tsx`)

The Original Study setup now shows install success/error messages so failed installs are visible immediately. The default Hebrew install pack is switched to `hebrewaleppocodex` (verified to install successfully) and Hebrew source-language inference is hardened with an id-based fallback for catalogs that mislabel Hebrew packs.

### 3. Hide broken catalog entry from public UI (`src/clible-web/components/TranslationModal.tsx`)

The `heb-leningrad` translation is filtered out from the translation picker UI entirely, so it is not offered via featured, browse, or search results.

### 4. Tests (`src/clible-web/components/*.test.tsx`)

New and updated component tests cover the translation picker structure and search wiring, plus the updated Hebrew install target in the Original Study setup.

## Files added

- `src/clible-web/components/TranslationModal.test.tsx` — covers translation picker sections, search input wiring, and install-close safety.
- `pr_stories/pr-TBD-translation-picker-featured-search.md` — this PR story.

## Files modified

- `src/clible-web/App.tsx` — debounced translation catalog search and wiring install feedback into Original Study.
- `src/clible-web/components/TranslationModal.tsx` — featured section, browse limit, search UI, and filtering broken packs.
- `src/clible-web/components/OriginalStudyView.tsx` — install feedback display and Hebrew pack default switch.
- `src/clible-web/components/OriginalStudyView.test.tsx` — expects Hebrew install to target `hebrewaleppocodex`.
- `src/clible-web/services/originalStudyPayload.ts` — Hebrew source-language inference fallback.
- `src/clible-web/utils/i18n.ts` — adds translation picker labels and search strings (EN/FI).

## Tests

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
cd src/clible-web && npm test --silent
```

Python: **345 passed**, coverage **94.36%** (gate ≥ 80%). Web: **46 passed**.

## Notes

`heb-leningrad` remains in the upstream catalog but is hidden from the public UI because `clible seed install heb-leningrad` fails with a malformed XML parse error (mismatched tag).

