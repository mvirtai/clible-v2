import bibleStructure from '../data/bible_structure.json';
import bookNamesData from '../data/book_names.json';

export type UILanguage = 'en' | 'fi';

type BookMeta = {
  en: string;
  fi: string;
  aliases_fi: string[];
  abbr_fi?: string;
  /** If set, used for heading abbreviations instead of `abbr_fi` (e.g. Acts: `ap` → `Ap.`). */
  citation_abbr_fi?: string;
};

const BOOK_LOCALE = bookNamesData as Record<string, BookMeta>;

/** Finnish citation abbreviation for headings (e.g. `joh` → `Joh.`). Prefers `citation_abbr_fi` when set. */
export function bookCitationAbbrevFi(id: string): string {
  const meta = BOOK_LOCALE[id];
  const slug = (meta?.citation_abbr_fi ?? meta?.abbr_fi)?.trim();
  if (!slug) {
    return id;
  }
  const parts = slug.split(/\s+/);
  if (parts.length === 1) {
    const w = parts[0];
    if (/^[a-z]{2,}$/i.test(w) && !/^\d+$/.test(w)) {
      const base = w.replace(/\.$/, '').toLowerCase();
      return `${base.charAt(0).toUpperCase()}${base.slice(1)}.`;
    }
    return w;
  }
  const out = [...parts];
  const last = out[out.length - 1];
  if (/^[a-z]{1,}$/i.test(last) && last.length >= 2) {
    const base = last.replace(/\.$/, '').toLowerCase();
    out[out.length - 1] = `${base.charAt(0).toUpperCase()}${base.slice(1)}.`;
  }
  return out.join(' ');
}

/** Book id prefix in bridge references: three letters (`GEN`) or digit + two letters (`1CO`). */
const REF_BOOK_PREFIX =
  /^((?:\d[A-Z]{2}|[A-Z]{3}))\s+(\d+:\S.*)$/;

/**
 * Presentation-only reference label. Keeps canonical `BOOK chapter:verse` for EN;
 * FI: full localized book name plus citation in parentheses (e.g.
 * `Apostolien teot (Ap. 1:1)`).
 */
export function formatReferenceForDisplay(reference: string, lang: UILanguage): string {
  if (lang !== 'fi') {
    return reference;
  }
  const trimmed = reference.trim();
  const m = trimmed.match(REF_BOOK_PREFIX);
  if (!m) {
    return reference;
  }
  const [, bookId, rest] = m;
  const fullName = bookNameLocalized(bookId, 'fi');
  const cite = `${bookCitationAbbrevFi(bookId)} ${rest}`;
  return `${fullName} (${cite})`;
}

/** Returns Finnish citation abbreviation, or the canonical book id for EN / missing abbr. */
export function bookAbbrevOrId(id: string, lang: UILanguage): string {
  if (lang !== 'fi') {
    return id;
  }
  const ab = BOOK_LOCALE[id]?.abbr_fi;
  return ab && ab.length > 0 ? ab : id;
}

/** Lookup map: book ID (e.g. "ROM") → full English name (e.g. "Romans"). */
export const BOOK_NAMES: Readonly<Record<string, string>> = Object.fromEntries(
  (bibleStructure.books as Array<{ id: string; name: string }>).map((b) => [
    b.id,
    b.name,
  ])
);

/** Returns the English full book name for a given ID, falling back to the raw ID. */
export function bookName(id: string): string {
  return BOOK_NAMES[id] ?? id;
}

/** Returns the display name for a book ID in the requested UI language. */
export function bookNameLocalized(id: string, lang: UILanguage): string {
  if (lang !== 'fi') {
    return bookName(id);
  }
  const meta = BOOK_LOCALE[id];
  if (meta?.fi) {
    return meta.fi;
  }
  return bookName(id);
}
