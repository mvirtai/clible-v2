# PR: Multi-verse lookup (verse range support)

**Branch/theme:** `able-multi-verse-search`

## Goal

Support **verse ranges** in the verse command so one reference can return multiple verses.

- **Current:** `clible verse "John 3:16"` → single verse.
- **After:** `clible verse "John 3:16-18"` → verses 16, 17, 18 in order.

Same translation and book; only the verse range changes. No new dependencies; reuse existing repos and CLI structure.

---

## Scope

### In scope

- Parse reference with optional range: `Book chapter:start-end` (e.g. `John 3:16-18`).
- **Single verse** `John 3:16` still works (no range = one verse).
- **Verse range** `John 3:16-18` returns a list of verses (16, 17, 18) from the same book/chapter/translation.
- Service layer: new method or extended contract that returns `list[dict]` for a range, single-item list for one verse (so CLI can always iterate).
- CLI: display multiple verses (e.g. one panel per verse, or one panel with verses numbered).
- Tests: verse service (single verse, range, invalid range); CLI output when range is used.

### Out of scope (later)

- Multiple separate references in one command (e.g. `"John 3:16" "Romans 8:28"`).
- Full-text search across verses (different feature).
- Cross-chapter ranges (e.g. John 3:16–4:2) — can be a follow-up.

---

## Implementation outline

1. **Reference parsing**
  Extend (or replace) `_parse_reference` so it returns either:
  - `(book_name, chapter, verse_start, verse_end)` with `verse_end >= verse_start`, or  
  - keep single-verse as `(book_name, chapter, verse, verse)` (start == end).  
   Regex already has `(\d+)(?:-(\d+))?`; capture the optional end verse.
2. **VerseRepo**
  Already has `get_verses(translation_id, book_id, chapter)` returning all verses in a chapter. Options:
  - **A)** Service gets full chapter and slices to `verse_start..verse_end` in Python.  
  - **B)** Add `get_verses_in_range(translation_id, book_id, chapter, start_verse, end_verse)` in VerseRepo and use it.  
   Prefer **B** for clarity and one place for range logic; **A** is fine if you want to avoid repo changes first.
3. **VerseService**
  - Either add `get_verses(reference, translation_id) -> list[dict]` (range or single → list), or  
  - Keep `get_verse` for single and add `get_verse_range(reference, translation_id) -> list[dict]`.  
   Recommendation: single method `get_verses(reference, translation_id) -> list[dict]` so CLI always gets a list (length 1 or more).
4. **CLI**
  Call `get_verses`; if empty, error; else loop and display each verse (e.g. `Panel` per verse or a single panel with "16 ... 17 ... 18" and text).
5. **Tests**
  - `test_verse_service.py`: single verse still works; range "John 3:16-18" returns 3 items in order; invalid range (e.g. 18-16) or missing verses handled.  
  - `test_verse_repo.py`: if you add range method, test it.  
  - CLI test: `clible verse "John 3:16-18"` prints multiple verses (snapshot or assert verse count / content).

---

## Files to touch (expected)


| Area        | File(s)                                                                        |
| ----------- | ------------------------------------------------------------------------------ |
| Parsing     | `src/clible/services/verse_service.py` (_parse_reference, get_verses)          |
| Repo (opt.) | `src/clible/db/repositories/verse_repo.py` (get_verses_in_range if chosen)     |
| CLI         | `src/clible/commands/verse.py` (use get_verses, render list)                   |
| Tests       | `tests/test_services/test_verse_service.py`, `tests/test_cli/` (verse command) |


---

## Acceptance criteria

- `clible verse "John 3:16"` still shows one verse.
- `clible verse "John 3:16-18"` shows three verses (16, 17, 18) in order.
- Invalid reference or invalid range (e.g. end < start) gives clear error, no traceback.
- All new/updated paths covered by tests (service + CLI).
- Lint and format clean; commit message e.g. `feat: support verse ranges in verse command`.

---

## Notes

- Keep reference parsing in the service layer; no need to expose regex to CLI.
- If a verse in the range is missing in DB (e.g. 17 not seeded), decide: fail entire request vs. return only available verses. Simpler: fail if any verse in range is missing (consistent with “verse not found” for single verse).

