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

type ReadingPlanGenerator = {
  type: 'sequentialChapters';
  scope: 'bible' | 'ot' | 'nt';
};

type ReadingPlanFile = {
  id: string;
  name: string;
  description?: string;
  durationDays: number;
  entries?: ReadingPlanEntry[];
  generator?: ReadingPlanGenerator;
};

const DATA_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'data', 'reading_plans');

function isReadingPlanFile(value: unknown): value is ReadingPlanFile {
  if (value == null || typeof value !== 'object') return false;
  const v = value as Record<string, unknown>;
  if (typeof v.id !== 'string' || typeof v.name !== 'string') return false;
  if (typeof v.durationDays !== 'number' || !Number.isFinite(v.durationDays)) return false;
  const hasEntries = Array.isArray(v.entries);
  const hasGenerator = v.generator != null && typeof v.generator === 'object';
  return hasEntries || hasGenerator;
}

async function loadBibleStructure(): Promise<Array<{ id: string; testament: 'OT' | 'NT'; chapters: number }>> {
  const jsonPath = join(DATA_DIR, '..', 'bible_structure.json');
  const raw = await readFile(jsonPath, 'utf8');
  const parsed = JSON.parse(raw) as unknown;
  if (parsed == null || typeof parsed !== 'object') {
    throw new Error('Invalid bible_structure.json');
  }
  const books = (parsed as any).books;
  if (!Array.isArray(books)) {
    throw new Error('Invalid bible_structure.json: missing books');
  }
  return books.map((b: any) => ({
    id: String(b.id),
    testament: b.testament === 'NT' ? 'NT' : 'OT',
    chapters: Number(b.chapters),
  }));
}

function buildSequentialChapterPlan(args: {
  durationDays: number;
  books: Array<{ id: string; chapters: number }>;
}): ReadingPlanEntry[] {
  const chapters: Array<[string, number]> = [];
  for (const book of args.books) {
    for (let ch = 1; ch <= book.chapters; ch += 1) {
      chapters.push([book.id, ch]);
    }
  }

  const total = chapters.length;
  const days = args.durationDays;
  if (days <= 0) throw new Error('durationDays must be > 0');
  if (total < days) throw new Error('Not enough chapters for durationDays');

  const base = Math.floor(total / days);
  const remainder = total % days;

  const daySizes: number[] = [];
  for (let i = 0; i < days; i += 1) {
    daySizes.push(i < remainder ? base + 1 : base);
  }

  const entries: ReadingPlanEntry[] = [];
  let idx = 0;
  for (let day = 1; day <= days; day += 1) {
    const size = daySizes[day - 1]!;
    const slice = chapters.slice(idx, idx + size);
    idx += size;

    const passages: ReadingPlanPassage[] = [];
    let [curBook, curStart] = slice[0]!;
    let curEnd = curStart;
    for (const [bookId, chapter] of slice.slice(1)) {
      if (bookId === curBook && chapter === curEnd + 1) {
        curEnd = chapter;
        continue;
      }
      passages.push({ bookId: curBook, chapterStart: curStart, chapterEnd: curEnd });
      curBook = bookId;
      curStart = chapter;
      curEnd = chapter;
    }
    passages.push({ bookId: curBook, chapterStart: curStart, chapterEnd: curEnd });

    entries.push({ dayNumber: day, passages });
  }

  if (entries.length !== days) {
    throw new Error('Generated plan did not match durationDays');
  }
  return entries;
}

export async function seedReadingPlanTemplates(): Promise<void> {
  const files = (await readdir(DATA_DIR)).filter((f) => f.endsWith('.json')).sort();
  if (files.length === 0) {
    console.warn('[seed] no reading plan templates found');
    return;
  }

  const bibleBooks = await loadBibleStructure();

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
      const entries: ReadingPlanEntry[] = (() => {
        if (Array.isArray(parsed.entries)) {
          if (parsed.entries.length !== parsed.durationDays) {
            throw new Error(
              `durationDays (${parsed.durationDays}) does not match entries length (${parsed.entries.length}) in ${file}`,
            );
          }
          return parsed.entries as ReadingPlanEntry[];
        }

        const gen = parsed.generator as ReadingPlanGenerator | undefined;
        if (!gen || gen.type !== 'sequentialChapters') {
          throw new Error(`Missing entries and unsupported generator in ${file}`);
        }

        const scopeBooks =
          gen.scope === 'ot'
            ? bibleBooks.filter((b) => b.testament === 'OT')
            : gen.scope === 'nt'
              ? bibleBooks.filter((b) => b.testament === 'NT')
              : bibleBooks;

        return buildSequentialChapterPlan({
          durationDays: parsed.durationDays,
          books: scopeBooks.map((b) => ({ id: b.id, chapters: b.chapters })),
        });
      })();

      await client.query(
        `INSERT INTO reading_plan_templates (id, name, description, duration_days, entries)
         VALUES ($1, $2, $3, $4, $5::jsonb)
         ON CONFLICT (id) DO UPDATE SET
           name          = EXCLUDED.name,
           description   = EXCLUDED.description,
           duration_days = EXCLUDED.duration_days,
           entries       = EXCLUDED.entries`,
        [parsed.id, parsed.name, parsed.description ?? null, parsed.durationDays, JSON.stringify(entries)],
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

