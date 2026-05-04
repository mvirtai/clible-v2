import { Pool, type PoolConfig } from 'pg';

function buildConfig(): PoolConfig {
  // DATABASE_URL takes priority (local dev, CI, any non-GCP hosting).
  if (process.env.DATABASE_URL) {
    return { connectionString: process.env.DATABASE_URL };
  }

  // Cloud Run + Cloud SQL: the built-in Auth Proxy exposes a Unix socket at
  // /cloudsql/<connection-name>. No password travels over the wire; IAM controls
  // access. The `host` field in pg accepts socket paths directly.
  const socketPath = process.env.CLOUD_SQL_CONNECTION_NAME
    ? `/cloudsql/${process.env.CLOUD_SQL_CONNECTION_NAME}`
    : undefined;

  const password = process.env.PGPASSWORD ?? process.env.CLIBLE_POSTGRES_PASSWORD ?? '';

  return {
    host: socketPath ?? process.env.PGHOST ?? 'localhost',
    port: socketPath ? undefined : parseInt(process.env.PGPORT ?? '5432'),
    database: process.env.PGDATABASE ?? 'clible',
    user: process.env.PGUSER ?? process.env.CLIBLE_POSTGRES_USER,
    password,
    // Only enforce SSL for plain TCP connections outside Cloud Run.
    ssl:
      !socketPath && process.env.NODE_ENV === 'production'
        ? { rejectUnauthorized: false }
        : undefined,
    max: 10,
    idleTimeoutMillis: 30_000,
    connectionTimeoutMillis: 5_000,
  };
}

export const pool = new Pool(buildConfig());

// Surface connection errors early rather than on the first request.
pool.on('error', (err) => {
  console.error('[db] idle client error:', err.message);
});
