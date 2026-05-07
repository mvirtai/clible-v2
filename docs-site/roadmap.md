# clible v2 — Roadmap

Current status and direction for the project. For implementation detail, see the [project overview](/architecture/project-overview).

---

## Current status

The core product is complete and deployed.

| Area | Status |
|------|--------|
| CLI (verse, search, analytics, seed, backup, export) | Done |
| Web UI (React/Vite + Express bridge) | Done |
| Authentication and user settings (PostgreSQL) | Done |
| AI features (Gemini insight + tone analysis) | Done |
| Docker packaging and Cloud Run deployment | Done |
| CI pipeline (GitHub Actions: lint, test, build, push) | Done |
| Test coverage (Python CLI, >91%) | Done |
| Documentation consolidation | Done |

---

## Near-term priorities

### H2 — Performance monitoring

Add response time middleware to the Express API. Add `clible analytics performance` command showing DB size, query times, and FTS table stats. Automate SQLite VACUUM. Add LRU cache for frequently fetched verses in the service layer.

### H4 — Error handling and logging

Structured logging (JSON) via `structlog`. Consistent, user-friendly error messages in CLI and web. Retry logic for seed downloads.

---

## Feature roadmap

### Medium priority

| Feature | What |
|---------|------|
| Advanced search (M1) | Boolean operators (AND/OR/NOT/NEAR), book/testament filters, saved searches |
| Reading plans (M3) | Pre-loaded plans (annual, 90-day, thematic), progress tracking, notes per verse |
| Export formats (M2) | PDF export, shareable web links |
| Mobile-first UI (M5) | PWA support, touch controls, dark mode improvements |

### Lower priority

- Translation comparison views (side-by-side, diff) in the web UI
- Internationalization (i18n) for UI strings

---

## Bold ideas

These would differentiate the project significantly if pursued.

| Idea | Notes |
|------|-------|
| AI study assistant (W1) | Free-form conversation, RAG over FTS + Gemini, contextual explanations |
| Community features (W2) | Shared notes, study groups, prayer wall, evangelism toolkit |
| Accessibility excellence (W7) | WCAG AAA, screen reader, dyslexia-friendly fonts, voice input |
| Offline P2P sync (W6) | Bluetooth/local-network sync for restricted environments |

---

## Development priorities by job-search relevance

1. **H2 (performance)** and **H4 (error handling)** — production-readiness signals
2. **One Wild feature** — W1 (AI assistant) or W7 (accessibility) for differentiation
3. **M3 (reading plans)** and **M1 (advanced search)** — core user value

Already done: H1 (testing >91%), H3 (documentation), H3 (docs), CI/CD, Docker, deployment.

---

## Historical notes

The original phase-based development plan (tickets 0–6) is preserved at [`docs/archive/PLAN.md`](https://github.com/vivaldev/clible-v2/blob/main/docs/archive/PLAN.md) for reference.
