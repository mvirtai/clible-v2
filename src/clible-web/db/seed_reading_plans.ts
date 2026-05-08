import { readdir, readFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { pool } from './pool.js';

type ReadingPlanPassage = {
  bookId: string;
  chapterStart: number;
  chapterEnd: number;
};

type ReadingPlanEntry = {
  dayNumber: number;
  passages: ReadingPlanPassage[];
};

type ReadingPlanFile = {
  id: string;
  name: string;
  description?: string;
  durationDays: number;
  entries: ReadingPlanEntry[];
};

const DATA_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'data', 'reading_plans');

function isReadingPlanFile(value: unknown): value is ReadingPlanFile {
  if (value == null || typeof value !== 'object') return false;
  const v = value as Record<string, unknown>;
  if (typeof v.id !== 'string' || typeof v.name !== 'string') return false;
  if (typeof v.durationDays !== 'number' || !Number.isFinite(v.durationDays)) return false;
  if (!Array.isArray(v.entries)) return false;
  return true;
}

export async function seedReadingPlanTemplates(): Promise<void> {
  const files = (await readdir(DATA_DIR)).filter((f) => f.endsWith('.json')).sort();
  if (files.length === 0) {
    console.warn('[seed] no reading plan templates found');
    return;
  }

  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    for (const file of files) {
      const raw = await readFile(join(DATA_DIR, file), 'utf8');
      const parsed = JSON.parse(raw) as unknown;
      if (!isReadingPlanFile(parsed)) {
        throw new Error(`Invalid reading plan template: ${file}`);
      }

      // Basic sanity checks to prevent broken plans from being seeded.
      if (parsed.durationDays <= 0) {
        throw new Error(`Invalid durationDays in reading plan template: ${file}`);
      }
      if (parsed.entries.length !== parsed.durationDays) {
        throw new Error(
          `durationDays (${parsed.durationDays}) does not match entries length (${parsed.entries.length}) in ${file}`,
        );
      }

      await client.query(
        `INSERT INTO reading_plan_templates (id, name, description, duration_days, entries)
         VALUES ($1, $2, $3, $4, $5::jsonb)
         ON CONFLICT (id) DO UPDATE SET
           name          = EXCLUDED.name,
           description   = EXCLUDED.description,
           duration_days = EXCLUDED.duration_days,
           entries       = EXCLUDED.entries`,
        [parsed.id, parsed.name, parsed.description ?? null, parsed.durationDays, JSON.stringify(parsed.entries)],
      );
    }
    await client.query('COMMIT');
    console.log(`[seed] reading plan templates upserted (${files.length})`);
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

