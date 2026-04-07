import bibleStructure from '../data/bible_structure.json';

/** Lookup map: book ID (e.g. "ROM") → full name (e.g. "Romans"). */
export const BOOK_NAMES: Readonly<Record<string, string>> = Object.fromEntries(
  (bibleStructure.books as Array<{ id: string; name: string }>).map((b) => [
    b.id,
    b.name,
  ])
);

/** Returns the full book name for a given ID, falling back to the raw ID. */
export function bookName(id: string): string {
  return BOOK_NAMES[id] ?? id;
}
