# ADR-001: Offline-first with SQLite for verse data

**Status:** Accepted  
**Date:** 2025

---

## Context

A Bible study tool needs to be reliable in environments where internet access is intermittent or unavailable — on trains, in remote areas, in countries with restricted internet access, or simply for users who want fast, dependency-free operation.

The alternative approach — fetching verses from a live REST API (such as bible-api.com) on every request — has several drawbacks: it requires a network connection, introduces latency, creates a runtime dependency on a third-party service, and limits the ability to run the tool fully offline or air-gapped.

## Decision

Bible text is **seeded locally** via `clible seed install <translation>`. The seed command downloads an XML file from a public GitHub repository, parses it, and stores all verses in a local SQLite database. After seeding, no network connection is needed for any Bible lookup, search, or analytics operation.

SQLite was chosen as the storage format because:
- It is a single file — easy to back up, restore, and move
- The Python stdlib includes `sqlite3` — no additional runtime dependency
- It supports FTS5 (full-text search) natively, which covers the search use case without a separate search engine
- It is well-suited to the read-heavy, single-writer workload of this tool

## Consequences

**Positive:**
- Works fully offline after seeding
- Fast lookups — no network round-trip
- No runtime API dependency
- FTS5 enables full-text search within the same database

**Negative:**
- Users must run `clible seed install` before any verse commands work
- Adding a new translation requires a new seed; translations are not automatically updated
- Multi-instance write scenarios (e.g. multiple Cloud Run instances) require care — SQLite does not support concurrent writers well

**Mitigations:**
- The CLI gives a clear error message when no translation is installed
- GCS backup/restore (`clible backup gcs`) handles the multi-instance case by treating GCS as the source of truth for the SQLite file
- The web layer stores only user data in PostgreSQL; verse data stays in SQLite and is treated as read-only in production
