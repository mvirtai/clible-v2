# feat: FTS5 web search MVP (CLI JSON + UI mapping + bridge docs)

This PR makes **full-text search in clible-web** work end-to-end: the Express bridge always receives valid JSON from `clible search --json`, the React client maps the CLI payload to list rows, and the Taskfile no longer has duplicate Docker task keys. It builds on the existing `/api/clible` bridge and FTS5-backed `VerseRepo.search_text`.

---

## Suggested commit sequence (you push)

Use a **topic branch** (example: `feat/fts5-web-search-mvp`). Commit **one logical change per commit**; order below keeps dependencies clear (CLI before web).

**1. CLI: empty search results must still print JSON**

```bash
git add src/clible/commands/search.py tests/test_cli/test_search_commands.py
git commit -m "fix(cli): emit JSON for search --json when there are no matches" -m "The web bridge parses stdout as JSON. Empty FTS results previously printed Rich text only, which caused Invalid JSON output from Clible CLI."
```

**2. Web: map search payload + types + label**

```bash
git add src/clible-web/repositories/bibleRepository.ts src/clible-web/types/bible.ts src/clible-web/App.tsx src/clible-web/vite-env.d.ts src/clible-web/tsconfig.json
git commit -m "feat(web): map FTS5 search JSON to SearchResultRow[]" -m "Normalize clible search --json (type search, verses array) to reference+text rows; add SearchResultRow; FTS5 label; Vite env types for import.meta.env.DEV."
```

**3. Bridge: optional dev logging**

```bash
git add src/clible-web/server.ts
git commit -m "chore(web): add dev-only logs for /api/clible CLI bridge"
```

**4. Docs: flow diagram**

```bash
git add docs/SEARCH_FLOW.md
git commit -m "docs: document web FTS5 search path to SQLite and back"
```

**5. Taskfile: Docker tasks**

```bash
git add Taskfile.yml
git commit -m "fix(task): dedupe web-docker tasks and add web-docker-run-base"
```

**6. Optional misc** (only if these changes belong in this PR)

```bash
# Whitespace in INTEGRATION.md, if still tracked:
git add src/clible-web/INTEGRATION.md
git commit -m "docs(web): minor INTEGRATION formatting"

# If you keep ignoring local INTEGRATION.md under clible-web:
git add src/clible-web/.gitignore
git commit -m "chore(web): gitignore local INTEGRATION.md override"
```

Then: `git push -u origin HEAD` and open the PR.

**If everything is already one commit:** either push as-is (single commit is acceptable for this scope) or split with `git reset --soft main` and re-commit in the order above, or use `git rebase -i` to reorder/squash.

---

## Summary

- **CLI:** When `clible search … --json` finds no verses, stdout is still a single JSON object (`verses: []`, statistics) from `export_verses_bundle`, not Rich-only output.
- **Web:** `BibleRepository.search` validates `type === "search"`, maps `verses` to `{ reference, text }`, surfaces API error bodies; dev-only browser logs when `import.meta.env.DEV`.
- **Server:** Non-production logs for argv, stdout/stderr sizes, parsed JSON keys, and parse failures (first 200 chars of stdout).
- **Docs:** `docs/SEARCH_FLOW.md` — sequence diagram and layer-by-layer explanation.
- **Task:** `web-docker-run-base` holds shared `docker run` logic; `web-docker-run` and `web-docker-debug` delegate without duplicate YAML keys.

---

## Files added

- `docs/SEARCH_FLOW.md` — Browser → Express → CLI → VerseService → `verses_fts` → JSON round-trip.
- `src/clible-web/vite-env.d.ts` — Vite client types for `import.meta.env`.

---

## Files modified

- `src/clible/commands/search.py` — JSON path for zero matches when `--json`.
- `tests/test_cli/test_search_commands.py` — `test_search_json_no_matches_emits_valid_json`.
- `src/clible-web/repositories/bibleRepository.ts` — `mapSearchJsonToRows`, error parsing, dev logs.
- `src/clible-web/types/bible.ts` — `SearchResultRow`.
- `src/clible-web/App.tsx` — FTS5 Search label (was FST5 typo).
- `src/clible-web/server.ts` — bridge debug logs.
- `src/clible-web/tsconfig.json` — `include` for `*.d.ts`.
- `Taskfile.yml` — `web-docker-run-base`, single `web-docker-run` / `web-docker-debug`.
- `src/clible-web/INTEGRATION.md` — optional minor spacing (if committed).
- `src/clible-web/.gitignore` — optional `INTEGRATION.md` (if committed).

---

## Tests

```bash
uv run pytest -v tests/test_cli/test_search_commands.py
uv run pytest -v
```

**Manual:** `cd src/clible-web && npm ci && npm run build` (and `npm run dev` + FTS5 search against an installed translation).

Update test counts when you run the suite before merge.

---

## Usage

```bash
# CLI sanity check
clible search grace -t web --json

# Web (dev)
cd src/clible-web && npm run dev
# Select translation, FTS5 Search, enter a word
```

Docker: `task web-docker-run` or `task web-docker-debug` (see `Taskfile.yml`).

---

## Follow-ups (not this PR)

- Performance: caching, pagination, or limiting large result sets in the UI.
- FTS tokenization / Finnish morphology if product needs it.
- Remove or gate bridge/browser logs further for production noise.
- Revisit `src/clible-web/.gitignore` + tracked `INTEGRATION.md` if the ignore rule was only for local drafts.
