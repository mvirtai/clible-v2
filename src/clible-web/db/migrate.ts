import { readdir, readFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { pool } from './pool.js';

// __dirname is not available in ESM; derive it from import.meta.url.
const MIGRATIONS_DIR = join(dirname(fileURLToPath(import.meta.url)), 'migrations');

export async function runMigrations(): Promise<void> {
  const client = await pool.connect();
  try {
    // The migrations tracker table bootstraps itself — it only needs to exist
    // before we start checking individual migration files.
    await client.query(`
      CREATE TABLE IF NOT EXISTS _migrations (
        name  TEXT        PRIMARY KEY,
        applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `);

    const files = (await readdir(MIGRATIONS_DIR))
      .filter((f) => f.endsWith('.sql'))
      .sort(); // alphabetical order guarantees 001 < 002 < 003 ...

    for (const file of files) {
      const { rowCount } = await client.query(
        'SELECT 1 FROM _migrations WHERE name = $1',
        [file],
      );
      if (rowCount && rowCount > 0) {
        continue; // already applied
      }

      const sql = await readFile(join(MIGRATIONS_DIR, file), 'utf8');

      // Each migration runs inside a transaction so a partial failure leaves
      // the database in a consistent state.
      await client.query('BEGIN');
      try {
        await client.query(sql);
        await client.query('INSERT INTO _migrations (name) VALUES ($1)', [file]);
        await client.query('COMMIT');
        console.log(`[migrate] applied ${file}`);
      } catch (err) {
        await client.query('ROLLBACK');
        throw new Error(`Migration ${file} failed: ${(err as Error).message}`);
      }
    }
  } finally {
    client.release();
  }
}
