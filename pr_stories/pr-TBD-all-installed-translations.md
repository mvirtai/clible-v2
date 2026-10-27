# PR: feat: display verses across installed translations and languages

## Summary

This PR adds `clible verse "John 3:16" --all` for terminal comparison of a verse or verse range across every translation already seeded in the local SQLite database. `--language CODE` narrows that view to a locally installed language, including when used without `--all`. The implementation keeps translation selection in `VerseService`, preserves the existing single-translation command behavior, and makes the new options discoverable in CLI and documentation help.

## Purpose

- Reading the same reference across installed languages required a shell loop and manual translation IDs.
- `verse` accepted one translation with `-t` but had no concise way to inspect all locally available texts or language-specific subsets.
- Users need an offline comparison workflow that does not download the entire translation catalog.

## Changes in This PR

### 1. Service-level installed translation lookup (`src/clible/services/verse_service.py`)

`VerseService.get_verses_for_all_translations` returns each matching installed translation together with the requested verse data. Its optional language-code filter is case-insensitive, and it keeps translations with no matching verse so the CLI can distinguish a missing reference from a translation that was not considered.

### 2. CLI rendering and option validation (`src/clible/commands/verse.py`)

The `--all` flag renders a heading and Rich panel for each locally installed translation. `--language CODE` uses the same multi-translation display path but limits it to an installed language, even without `--all`. Both are deliberately limited to verse and verse-range references, and they reject `-t`, JSON, and export options because their existing output formats describe exactly one translation.

### 3. Help, documentation, and tests (`src/clible/ui/help_texts.py`, `docs-site/cli/verse.md`, `tests/`)

The CLI help and public verse documentation describe the new options and clarify that they only use already seeded data. The translation catalog and a migration correct Dios Habla Hoy's language code to `es` for both future and existing seeds. Service, command, and migration tests cover ordered multi-translation lookup, case-insensitive language filtering, rendering distinct text for each translation, updating existing metadata, and rejecting an incompatible translation override.

## Files added

- `pr_stories/pr-TBD-all-installed-translations.md` — PR narrative and validation record.

## Files modified

- `src/clible/services/verse_service.py` — add installed-translation verse lookup.
- `src/clible/commands/verse.py` — add and render `--all` and `--language`.
- `src/clible/data/translations.json` — correct Dios Habla Hoy's language code to `es`.
- `src/clible/db/migrations/007_fix_spanishdhh_language.sql` — repair the stored language code in existing databases.
- `src/clible/ui/help_texts.py` — document CLI usage and option limits.
- `docs-site/cli/verse.md` — document the installed-translation workflow.
- `tests/test_services/test_verse_service.py` — cover service selection and missing data.
- `tests/test_cli/test_verse_commands.py` — cover rendering and option validation.

## Tests

```bash
uv run task check
```

350 pytest tests completed with 94.42% coverage (gate >= 80%); Ruff lint and format checks passed.

## Usage

```bash
# Display John 3:16 from every translation already seeded locally.
clible verse "John 3:16" --all

# Display John 3:16 from every locally seeded Spanish translation.
clible verse "John 3:16" --language es

# Continue selecting exactly one translation when needed.
clible verse "John 3:16" -t web
```

## Notes

`--all` and `--language` do not seed or download additional Bible texts. Whole chapters and books remain on the existing paginated single-translation path to keep output bounded. The language-code migration updates existing Dios Habla Hoy installs automatically when the upgraded CLI opens the database.
