import { describe, expect, it } from 'vitest';

import type { InstalledTranslation } from '../types/bible';
import type { OriginalStudyVerse } from '../types/originalStudy';
import { buildOriginalStudyPayload, inferOriginalSourceLanguage } from './originalStudyPayload';

const installed: InstalledTranslation[] = [
  { id: 'greek', name: 'Greek', language: 'grc', format: 'usfx' },
  { id: 'hebrew', name: 'Hebrew', language: 'heb', format: 'usfx' },
  { id: 'fin-1992', name: 'FIN', language: 'fi', format: 'usfx' },
  { id: 'web', name: 'WEB', language: 'en', format: 'usfx' },
];

describe('inferOriginalSourceLanguage', () => {
  it('returns he for heb/hbo/he language values', () => {
    expect(inferOriginalSourceLanguage('hebrew', installed)).toBe('he');
    expect(
      inferOriginalSourceLanguage('hbo-id', [
        ...installed,
        { id: 'hbo-id', name: 'HBO', language: 'hbo', format: 'usfx' },
      ]),
    ).toBe('he');
  });

  it('falls back to grc when translation is unknown', () => {
    expect(inferOriginalSourceLanguage('unknown', installed)).toBe('grc');
  });
});

describe('buildOriginalStudyPayload', () => {
  const mapLookupToVerses = (data: Record<string, unknown>): OriginalStudyVerse[] =>
    ((data.verses as Array<Record<string, unknown>> | undefined) ?? []).map((v) => ({
      book_name: String(v.book_id ?? ''),
      chapter: Number(v.chapter ?? 0),
      verse: Number(v.verse ?? 0),
      text: String(v.text ?? ''),
    }));

  it('builds payload and translation list in target order', () => {
    const lookups: Array<Record<string, unknown>> = [
      { verses: [{ book_id: 'JHN', chapter: 3, verse: 16, text: 'ΟΥΤΩΣ' }] }, // original
      { verses: [{ book_id: 'JHN', chapter: 3, verse: 16, text: 'Sillä niin' }] }, // fin
      { verses: [{ book_id: 'JHN', chapter: 3, verse: 16, text: 'For God so loved' }] }, // web
    ];
    const originalVerses = mapLookupToVerses(lookups[0]);
    const out = buildOriginalStudyPayload({
      reference: 'John 3:16',
      sourceLanguage: 'grc',
      originalVerses,
      uniqueTargets: ['fin-1992', 'web'],
      lookups,
      installed,
      mapLookupToVerses,
    });

    expect(out.payload.reference).toBe('John 3:16');
    expect(out.payload.sourceText).toContain('ΟΥΤΩΣ');
    expect(out.payload.translations.map((t) => t.id)).toEqual(['fin-1992', 'web']);
    expect(out.translations.map((t) => t.id)).toEqual(['fin-1992', 'web']);
  });

  it('fills empty target text with em dash fallback', () => {
    const lookups: Array<Record<string, unknown>> = [
      { verses: [{ book_id: 'JHN', chapter: 3, verse: 16, text: 'ΟΥΤΩΣ' }] },
      { verses: [] },
    ];
    const originalVerses = mapLookupToVerses(lookups[0]);
    const out = buildOriginalStudyPayload({
      reference: 'John 3:16',
      sourceLanguage: 'grc',
      originalVerses,
      uniqueTargets: ['web'],
      lookups,
      installed,
      mapLookupToVerses,
    });

    expect(out.payload.translations[0].text).toBe('—');
  });

  it('throws when source text is missing', () => {
    expect(() =>
      buildOriginalStudyPayload({
        reference: 'John 3:16',
        sourceLanguage: 'grc',
        originalVerses: [{ book_name: 'JHN', chapter: 3, verse: 16, text: '   ' }],
        uniqueTargets: ['web'],
        lookups: [{ verses: [] }, { verses: [] }],
        installed,
        mapLookupToVerses,
      }),
    ).toThrow('No original-language text found for this reference.');
  });
});

