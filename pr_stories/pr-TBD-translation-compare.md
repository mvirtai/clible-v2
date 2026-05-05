# PR: feat(web): translation compare, analytics word cloud, compare export, AI study API

## Summary

This PR adds a full **translation compare** flow in the web UI: users pick two installed translations, enter a reference, and see aligned verses with similarity scores from the existing `clible analytics compare` CLI path exposed via the `/api/clible` bridge. It introduces an optional **word cloud** view for analytics word frequency (alongside the existing horizontal bar chart), wires **export** for compare results through the same `ExportModal` and `analytics compare … --stdout-export` pipeline used elsewhere, and adds **POST /api/ai/study** plus Gemini prompts for future original-language study assistance when Hebrew/Greek texts are paired with a translation.

## Purpose

- Readers comparing two Bible translations had no first-class UI; they had to use the CLI or exports manually.
- Word frequency in Analytics was only available as a bar chart; a size-proportional “word map” makes relative frequency scannable at a glance.
- Compare results could not be downloaded in the same formats (Markdown, HTML, JSON, etc.) as verse, search, and analytics exports.
- A dedicated study-style endpoint prepares the app for deeper Hebrew/Greek ↔ translation commentary without overloading the generic insight or tone routes.

## Changes in This PR

### 1. Types and data (`src/clible-web/types/compare.ts`)

Typed `CompareResult`, `AlignedVerse`, and `CompareSummary` to match the JSON from `AnalyticService.compare_translations` so the React layer stays type-safe and the bridge response is validated in the service.

### 2. Bible service bridge (`src/clible-web/services/bibleService.ts`)

`getCompareResult` builds the same token sequence the CLI expects: `compare` + JSON-quoted reference + `--left` / `--right` translation ids, then `GET /api/clible?cmd=analytics&args=…`. The reference is passed through `JSON.stringify` so special characters in references are handled consistently with the export path in `App.tsx`. Error handling maps non-OK responses to user-readable messages.

### 3. Compare UI (`src/clible-web/components/CompareView.tsx`)

New view: reference field, two translation dropdowns, run button, summary cards (average similarity, exact matches, aligned rows, most similar verse, top shared words), and a table of aligned verses. **Export compare** uses the same button placement and styling as `AnalyticsView` (rounded pill, `Download` icon). The original-language “AI study” control remains a visible placeholder (disabled) until the client is wired to the new study endpoint.

### 4. App shell and navigation (`src/clible-web/App.tsx`)

Compare is a first-class `viewMode` with state for left/right translation ids, loading and error, and `handleCompare` calling `bibleService.getCompareResult`. **Export** calls `triggerExport('analytics', \`compare ${JSON.stringify(ref)} --left … --right …\`, title)` so the existing `bibleRepository.export` appends `--stdout-export <format>`. `handleExport` is adjusted so **tone analysis is not appended** when the analytics args start with `compare `, avoiding polluting compare exports with analytics tone text. `SearchPanel` gains a **Study** entry area (scripture / compare tab) so users can open compare from the same entry point as reading and search.

### 5. Analytics word cloud (`src/clible-web/components/WordCloud.tsx`, `AnalyticsView.tsx`)

`WordCloud` renders `nativeFrequency` with font size and weight scaled to min–max count; no new charting dependencies. `AnalyticsView` adds a **bar / cloud** toggle next to the Word Frequency heading with localized `title` attributes (`analyticsFreqViewBarTitle` / `analyticsFreqViewCloudTitle`).

### 6. Internationalization (`src/clible-web/utils/i18n.ts`)

New strings for compare (including `compareExport`), frequency view toggle titles, and any Study/compare labels added with `SearchPanel`. English and Finnish keys stay in lockstep.

### 7. AI study API (`src/clible-web/ai.config.ts`, `src/clible-web/server.ts`)

`GEMINI_MODEL_STUDY` defaults to the same flash model as insight/tone. `studySystemInstruction` and `buildStudyUserPrompt` define a structured Markdown response comparing source Hebrew or Greek text with a translation excerpt. `POST /api/ai/study` accepts `reference`, `sourceText`, `translationText`, and `sourceLanguage` (Hebrew vs Greek heuristic), reuses `requireAuth` and the existing AI rate limiter, and returns `{ text }` like the other AI routes. The Compare UI does not call this endpoint yet; it is ready for a follow-up that picks verses when one side is an original-language edition.

## Files added

- `src/clible-web/types/compare.ts` — TypeScript types for compare JSON.
- `src/clible-web/components/CompareView.tsx` — Translation compare screen and export button.
- `src/clible-web/components/WordCloud.tsx` — Frequency-weighted word display for Analytics.

## Files modified

- `src/clible-web/App.tsx` — Compare mode, export wiring, `handleExport` compare guard, SearchPanel integration.
- `src/clible-web/components/SearchPanel.tsx` — Study entry tabs / compare entry.
- `src/clible-web/components/AnalyticsView.tsx` — Bar/cloud toggle, localized toggle titles.
- `src/clible-web/services/bibleService.ts` — `getCompareResult` bridge.
- `src/clible-web/utils/i18n.ts` — New message keys (compare, export, frequency toggles).
- `src/clible-web/ai.config.ts` — Study model, prompts.
- `src/clible-web/server.ts` — `POST /api/ai/study`.

## Tests

```bash
uv run pytest -v
uv run ruff check .
uv run ruff format --check .
cd src/clible-web && npm run lint
```

Python suite: **315** tests, coverage gate satisfied. Web: `tsc --noEmit` passes. No new automated UI tests in this PR (manual QA: compare two translations, toggle word cloud, export compare as MD).

## Usage

```bash
# Local web (with .env / DATABASE_URL / GEMINI_* as needed)
cd src/clible-web && npm run dev
```

In the UI: open **Compare** from the study entry flow, choose two translations, enter a reference (e.g. `John 3:16`), run compare. In **Analytics**, use the chart/cloud icons next to Word Frequency. With compare results visible, click **Export compare** / **Vie vertailu** and pick a format in the modal.

Study API (for integrations or future UI):

```bash
curl -s -X POST http://localhost:3000/api/ai/study \
  -H "Content-Type: application/json" \
  -H "Cookie: …" \
  -d '{"reference":"John 3:16","sourceLanguage":"grc","sourceText":"…","translationText":"…"}'
```

## Notes

- **Compare export** reuses `cmd=analytics` because the CLI subcommand lives under `analytics compare`; this matches how `bibleRepository.export` already works.
- **AI study** is server-complete but not yet invoked from `CompareView`; enabling it requires product decisions (which verse row to send, loading states, errors).
- Optional **split for reviewers**: one commit for compare UI + bridge, one for word cloud + i18n toggles, one for study API—this branch uses a **single feature commit** plus a **docs commit** for the PR story to keep history linear and always buildable.

## Related documentation

- `src/clible/commands/analytics.py` — `analytics compare` CLI (reference for args).
- `docs/api/openapi.yml` — consider registering `/api/ai/study` in a follow-up if the API is published.

---

## Git commit strategy (executed locally)

| Step | Command / intent |
|------|------------------|
| 1 | Stage all web feature files under `src/clible-web/` and commit as one **feat(web)** (feature is coupled in `App.tsx`). |
| 2 | `git add -f pr_stories/pr-TBD-translation-compare.md` and **docs** commit (folder is gitignored but tracked files are allowed with `-f`). |

## After merge — for the PR author (not run by automation)

```bash
git fetch origin
git switch feat/add-translation-compare   # or your branch name
git push -u origin feat/add-translation-compare
```

Create the PR on GitHub (CLI example):

```bash
gh pr create --base main --head feat/add-translation-compare \
  --title "feat(web): translation compare, word cloud, compare export, AI study API" \
  --body-file pr_stories/pr-TBD-translation-compare.md
```

Then review CI (`web-ci`, `ci`), merge when green.
