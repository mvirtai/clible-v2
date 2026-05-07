# Changelog

The current development direction is captured in the [roadmap](/roadmap). This page summarises shipped milestones at a higher level than individual git commits.

For full commit history, see [the GitHub commits page](https://github.com/vivaldev/clible-v2/commits/main).

## Shipped

- **CLI engine** — verse lookup, FTS5 search, analytics, export, seed install/list/remove, GCS backup.
- **Web app** — React 19 + Vite frontend with an Express bridge that spawns the CLI for every Bible operation.
- **Authentication** — registration, login, sessions backed by PostgreSQL via `connect-pg-simple`.
- **AI features** — Gemini-powered insight, tone, study, and original-language analysis. Rate-limited per user.
- **Admin API** — capability toggles (AI access, admin flag), user search.
- **Deployment** — single Docker image, Cloud Run via Workload Identity Federation, GitHub Actions CI.
- **Test coverage** — Python CLI above 91%; web layer covered by Vitest.
- **Documentation** — VitePress site (this one).

## In progress

See the [roadmap](/roadmap) for near-term priorities (performance monitoring, structured logging) and the longer feature list.
