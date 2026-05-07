# ADR-004: PostgreSQL for user data in the web layer

**Status:** Accepted  
**Date:** 2026

---

## Context

The CLI tool stores all Bible data in a single SQLite file. When the web UI was added, it needed to store user accounts, sessions, and settings. Putting user data in the same SQLite file as verse data creates two problems:

1. **Concurrent writes**: Cloud Run can run multiple container instances. SQLite supports only one writer at a time, so concurrent session writes from different instances would either lock or corrupt the database.

2. **Separation of concerns**: Verse data is read-only after seeding and owned by the CLI layer. User data is mutable and owned by the web layer. Mixing them in one file would blur this boundary and complicate backup/restore logic.

## Decision

User-related data — accounts, sessions, settings — is stored in a **PostgreSQL database** (Neon in production, local Postgres in development). Session storage uses `connect-pg-simple`, which stores Express sessions in a `session` table.

The SQLite file remains the source of truth for Bible text and is treated as **read-only** in the web layer. The web layer never writes to SQLite — it only spawns `clible` CLI commands that read from it.

This creates a clean split:

| Store      | Owns                              | Managed by  |
|------------|-----------------------------------|-------------|
| SQLite     | Translations, books, verses       | CLI layer   |
| PostgreSQL | Users, sessions, settings         | Web layer   |

## Consequences

**Positive:**

- Multiple Cloud Run instances can safely handle concurrent requests — PostgreSQL supports concurrent writes
- User data and Bible data can be backed up, migrated, and scaled independently
- The CLI layer remains completely unaware of user management

**Negative:**

- The web app now requires a PostgreSQL connection string (`DATABASE_URL`) to start
- Local development needs a running Postgres instance (or a Neon free-tier connection)
- Two database systems to reason about and keep in sync during development

**Trade-off accepted:** The operational complexity of a second database is justified by the need for concurrent session writes and the clean separation between user data and Bible data.

**Setup:** See `docs/CLOUD_SQL_SETUP.md` for provisioning options (Neon, Cloud SQL). The web layer's migrations live in `src/clible-web/db/migrations/`.
