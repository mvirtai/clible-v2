# feat(web): migrate user auth database from SQLite to PostgreSQL

Replaces the embedded `better-sqlite3` user database in the Express backend with a
shared PostgreSQL instance (Neon). This is a prerequisite for running the web app
on Cloud Run, where every container restart would previously wipe session and
user data stored in the ephemeral local filesystem.

## Summary

- **New `src/clible-web/db/` module** — `pg.Pool` singleton (`pool.ts`), file-based
  migration runner (`migrate.ts`), and initial schema migration
  (`001_users_sessions_settings.sql`) with `users`, `session`, and `user_settings`
  tables.
- **`auth/routes.ts`** — all queries converted from synchronous `better-sqlite3`
  to `async/await` `pool.query()` with PostgreSQL `$1`/`$2` placeholders.
- **`user/settings_routes.ts`** — same async conversion; `INSERT OR REPLACE`
  rewritten as `INSERT … ON CONFLICT … DO UPDATE SET` (standard SQL upsert).
- **`server.ts`** — replaced custom `SQLiteStore` with `connect-pg-simple` backed
  by the shared pool; `runMigrations()` is awaited before `app.listen()`.
- **`auth/db.ts`** — stripped to a thin re-export of `pool` for backwards
  compatibility; `better-sqlite3` bootstrap removed entirely.
- **`Dockerfile`** — removed `VOLUME ["/app/web/data"]`; SQLite user-data volume
  no longer needed.
- **`Taskfile.yml`** — added `db-migrate` task; `deploy-cloud-run` / `gcp-web-deploy`
  updated to pass `DATABASE_URL` (Neon connection string) instead of Cloud SQL flags.
- **`scripts/setup-cloud-sql.sh`** — kept as an alternative provisioning script for
  Cloud SQL (uses `--edition=ENTERPRISE` to allow `db-f1-micro`).
- **`docs/CLOUD_SQL_SETUP.md`** — new public guide: Neon (recommended, free) and
  Cloud SQL setup, `DATABASE_URL` format, local Docker usage.
- **`src/clible-web/README.md`** — Docker Quick Start updated: removed SQLite volume,
  added `DATABASE_URL` requirement and reference to setup guide.
- **`docs/PROJECT_OVERVIEW.md`** — web DB layer and sessions added to Done table;
  file map updated; Planned section cleared.
- **`.github/workflows/neon-workflow.yml`** — Neon preview branch workflow cleaned up:
  removed template noise, fixed step ID reference, activated migration step so each
  PR gets a fresh isolated schema on a dedicated Neon branch.

## Files added

| File | Purpose |
|---|---|
| `src/clible-web/db/pool.ts` | `pg.Pool` singleton configured from `DATABASE_URL` |
| `src/clible-web/db/migrate.ts` | Runs numbered `.sql` files in `db/migrations/` |
| `src/clible-web/db/migrations/001_users_sessions_settings.sql` | Initial schema: `users`, `session`, `user_settings` |
| `docs/CLOUD_SQL_SETUP.md` | Public PostgreSQL setup guide (Neon + Cloud SQL) |
| `scripts/setup-cloud-sql.sh` | Optional Cloud SQL provisioning script |
| `.github/workflows/neon-workflow.yml` | PR preview branch workflow for Neon |

## Files modified

| File | Change |
|---|---|
| `src/clible-web/auth/db.ts` | Removed `better-sqlite3` bootstrap; re-exports `pool` |
| `src/clible-web/auth/routes.ts` | Sync → async `pool.query()`; `?` → `$1/$2` |
| `src/clible-web/user/settings_routes.ts` | Sync → async; SQLite upsert → PostgreSQL `ON CONFLICT` |
| `src/clible-web/server.ts` | `SQLiteStore` → `connect-pg-simple`; `runMigrations()` on startup |
| `src/clible-web/package.json` | `+pg +connect-pg-simple −better-sqlite3` |
| `src/clible-web/Dockerfile` | Removed `VOLUME ["/app/web/data"]` |
| `Taskfile.yml` | `db-migrate` task; deploy commands use `DATABASE_URL` |
| `src/clible-web/README.md` | Docker Quick Start + Security Notes updated |
| `docs/PROJECT_OVERVIEW.md` | Done table and file map updated |
| `.gitignore` | Added `.agents/`, `.claude/`, `skills-lock.json` |

## Tests

The web backend has no automated test suite yet (Express/TypeScript). The Python
CLI tests are unaffected:

```bash
uv run pytest -v
```

Manual smoke-test after deployment:

```bash
# Register a user
curl -X POST https://<SERVICE_URL>/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"test","password":"test1234"}'

# Log in
curl -X POST https://<SERVICE_URL>/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"test","password":"test1234"}'
```

## Usage

```bash
# Local development with Docker
docker run --rm -p 3000:3000 \
  -e DATABASE_URL="postgresql://user:pass@host/db?sslmode=require" \
  clible-web

# Deploy to Cloud Run (reads DATABASE_URL from .env.production)
task gcp-web-deploy
```

See `docs/CLOUD_SQL_SETUP.md` for how to provision the database.
