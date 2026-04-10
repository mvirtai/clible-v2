# feat(web): robust web interface export support

This PR implements a full-stack export feature for the web application, bridging the powerful Clible CLI export capabilities to the browser. It enables users to download verses, search results, and analytics in various formats directly from the web UI.

## Summary

### CLI Enhancements
- Added `--stdout-export [csv|html|json|md|txt|xml]` flag to `verse`, `search`, and `analytics` commands.
- Implemented high-performance stdout streaming for formatted content, allowing the web bridge to consume export data without filesystem writes.

### API Bridge (`server.ts`)
- Updated the Express bridge to handle raw formatted output.
- Implemented automatic `Content-Type` header resolution based on the requested format.
- Optimized the command builder to avoid JSON parsing overhead when performing exports.

### Frontend Integration
- **New Component**: `ExportModal.tsx` — A premium, motion-enhanced dialog for format selection with descriptive icons (Lucide) and animations (Motion).
- **New Utility**: `utils/download.ts` — A robust browser-side file download trigger.
- **Service Layer**: Extended `BibleRepository` with a streaming `export` method.
- **UI Connectivity**:
  - Integrated export triggers into `ReaderView`, `SearchView`, and `AnalyticsView`.
  - Added visual Polish to the Search Results header to accommodate the new export action.

### Design & UX Refinements
- **Theme Consistency**: Refactored `SearchStatsPanel` to use CSS theme variables, ensuring perfect visibility in both Light and Dark modes.
- **Markdown Fixes**: Resolved visibility issues for bold text and horizontal rules within inverted AI insight cards.

## Files Added
- `src/clible-web/components/ExportModal.tsx` — Formatted selection dialog.
- `src/clible-web/utils/download.ts` — Browser download utility.

## Files Modified
- `src/clible/commands/verse.py` — Added `--stdout-export`.
- `src/clible/commands/search.py` — Added `--stdout-export`.
- `src/clible/commands/analytics.py` — Added `--stdout-export` to all subcommands.
- `src/clible-web/server.ts` — Bridge support for raw output.
- `src/clible-web/repositories/bibleRepository.ts` — Added export API method.
- `src/clible-web/App.tsx` — Main application logic for export orchestration.
- `src/clible-web/components/ReaderView.tsx` — Export button connection.
- `src/clible-web/components/SearchView.tsx` — Added export button.
- `src/clible-web/components/AnalyticsView.tsx` — Added export button.
- `src/clible-web/components/SearchStatsPanel.tsx` — Theme variable refactor.
- `src/clible-web/utils/markdownComponents.tsx` — Bold text visibility fixes.

## Tests
Verified CLI functionality and ensured that standard JSON-based bridge calls remain unaffected.
```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -v  # 243 tests passing
```

## Preview
| Feature | Description |
| --- | --- |
| **Export Modal** | Card-based selection with premium icons |
| **Analytics Export** | Direct download of text-based linguistic reports |
| **Search Export** | Full result set download in Markdown/CSV |
