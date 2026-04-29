# feat(web): translation management in web UI (available + install)

This PR adds a full web flow for browsing available translations and installing them directly from the UI, without requiring direct CLI access from end users.

## Summary

- Added JSON output mode for `clible seed available` so the web backend can consume catalog data reliably.
- Added authenticated web API endpoints for translation catalog listing and translation installation.
- Extended the web repository layer with methods for available translations and install requests.
- Updated translation modal UX to:
  - show available catalog translations,
  - install translations directly,
  - show install loading/success/error states,
  - allow selecting only installed translations.
- Added/updated CLI tests for `seed available --json`.

## Files modified

- `src/clible/commands/seed.py` — add `--json` support for `seed available`.
- `tests/test_cli/test_seed_commands.py` — tests for `seed available --json`.
- `src/clible-web/server.ts` — add `/api/translations/available` and `/api/translations/install` endpoints.
- `src/clible-web/repositories/bibleRepository.ts` — add `listAvailableTranslations()` and `installTranslation()`.
- `src/clible-web/types/bible.ts` — add `AvailableTranslation` type.
- `src/clible-web/App.tsx` — wire available/install flow and install state handling.
- `src/clible-web/components/TranslationModal.tsx` — render available catalog and install controls.

## Why

Previously, users had to install translations via CLI on the server/container, which is not practical for normal web usage. This change moves translation management into the web workflow while keeping auth and backend validation intact.

## Test plan

```bash
uv run pytest -q tests/test_cli/test_seed_commands.py
cd src/clible-web && npm run lint
```

- `uv run pytest -q tests/test_cli/test_seed_commands.py` — passes
- `npm run lint` (`tsc --noEmit`) — passes

## Notes

- Endpoints are auth-protected with existing session middleware (`requireAuth`).
- Install endpoint validates `translationId` format and returns user-friendly error details from CLI failures.
