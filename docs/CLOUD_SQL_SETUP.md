# PostgreSQL Setup

clible-web stores user accounts, sessions, and settings in a PostgreSQL database.
This document covers the recommended setup (Neon, free) and an alternative GCP-native
option (Cloud SQL, paid).

---

## Why not SQLite?

SQLite is a single-file embedded database. It works well for the offline-first CLI,
but is a poor fit for a stateless web service:

- **Cloud Run containers are ephemeral.** Any file written inside the container is lost
  when the revision restarts, scales to zero, or scales to multiple instances.
- **Multiple instances cannot share a file.** Cloud Run can run several containers in
  parallel; each would have its own copy of `users.db`, so login sessions would break
  across instances.
- **SQLite serialises writers.** Even in WAL mode, concurrent writes queue up. Spawning
  a new Python process per HTTP request (the CLI bridge) already triggers
  `database is locked` errors under light load.

PostgreSQL is a separate server process. The application connects to it over TCP or a
Unix socket and the database manages concurrency correctly.

---

## Architecture

```
Cloud Run container
└── Express (server.ts)
    ├── pg Pool (src/clible-web/db/pool.ts)
    │     │
    │     └── TLS/TCP ──► Neon (PostgreSQL 16, serverless)
    │                      ├── users
    │                      ├── sessions   (managed by connect-pg-simple)
    │                      └── user_settings
    │
    └── spawn("clible") ──► clible.db (SQLite, baked into image, read-only)
```

The Bible text database (`clible.db`) remains in SQLite — it is seeded once and never
written to at runtime.

---

## Option A: Neon (free, recommended)

[Neon](https://neon.tech) is a serverless PostgreSQL provider with a generous free tier
(0.5 GB storage, scales to zero when idle — no charges when not in use).

### Setup

1. Sign up at [neon.tech](https://neon.tech) and create a project (PostgreSQL 16,
   nearest region).
2. Copy the connection string from the dashboard:
   ```
   postgresql://user:password@ep-xxx.eu-central-1.aws.neon.tech/neondb?sslmode=require
   ```
3. Add it to `.env.production`:
   ```
   DATABASE_URL=postgresql://user:password@ep-xxx...neon.tech/neondb?sslmode=require
   ```
4. Deploy:
   ```bash
   set -a && source .env.production && set +a
   task gcp-web-deploy
   ```

No IAM setup, no sidecar containers, no VPC connectors. The pool uses `DATABASE_URL`
when set and enables SSL automatically for non-socket connections in production.

---

## Option B: Cloud SQL (GCP-native, ~€9/month minimum)

Cloud SQL is GCP's managed PostgreSQL service. It costs money even at the smallest tier;
use it if you want everything inside GCP and are willing to pay.

### Setup

Run `scripts/setup-cloud-sql.sh` after sourcing `.env.production`:

```bash
set -a && source .env.production && set +a
bash scripts/setup-cloud-sql.sh
```

The script creates a PostgreSQL 16 instance (`clible-pg`, ENTERPRISE edition,
`db-f1-micro` tier), creates the database and user, and grants the Cloud Run service
account the `cloudsql.client` IAM role.

After the script completes, note the **instance connection name**
(`PROJECT:REGION:INSTANCE`) it prints. Add these to `.env.production`:

```
CLOUD_SQL_CONNECTION_NAME=clible-v2dev:europe-north1:clible-pg
PGDATABASE=clible
PGUSER=clible-pg-user
PGPASSWORD=your-password
```

Then update the deploy commands in `Taskfile.yml` to pass
`--add-cloudsql-instances="${CLOUD_SQL_CONNECTION_NAME}"` and the corresponding env
vars instead of `DATABASE_URL`.

---

## Environment variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | Full connection string — **takes priority over all other vars**. Use this for Neon and local development. |
| `CLOUD_SQL_CONNECTION_NAME` | `PROJECT:REGION:INSTANCE` — activates Unix socket mode for Cloud SQL. |
| `PGHOST` | Hostname for plain TCP connections (fallback when neither of the above is set). |
| `PGDATABASE` | Database name (default: `clible`). |
| `PGUSER` / `CLIBLE_POSTGRES_USER` | Database username. |
| `PGPASSWORD` / `CLIBLE_POSTGRES_PASSWORD` | Database password. |

`pool.ts` resolves credentials in this order:

1. `DATABASE_URL` → used as-is (Neon, Supabase, local Docker)
2. `CLOUD_SQL_CONNECTION_NAME` → Unix socket at `/cloudsql/<name>` + `PG*` vars
3. `PGHOST` + `PG*` vars → plain TCP

---

## Migrations

Migrations run automatically when the server starts (`runMigrations()` is called before
`app.listen()`). Migration SQL files live in `src/clible-web/db/migrations/` and are
named `NNN_description.sql`. Applied migrations are tracked in the `_migrations` table.

To run migrations manually:

```bash
# Source your env first, then:
task db-migrate
```

---

## Local development

Run a local Postgres instance with Docker:

```bash
docker run --rm \
  -e POSTGRES_USER=clible \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=clible \
  -p 5432:5432 \
  postgres:16-alpine
```

Add to your local `.env`:

```
DATABASE_URL=postgresql://clible:secret@localhost:5432/clible
```

Migrations run automatically on the first `npm run dev`.

Alternatively, use a free Neon project for local development too — create a separate
Neon branch for dev and point `DATABASE_URL` at it.
