import { describe, expect, it, vi, afterEach } from 'vitest';

import { BibleRepository } from './bibleRepository';

describe('BibleRepository.getVerse', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('formats verse range reference from returned verses', async () => {
    const repo = new BibleRepository();
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            type: 'verse_lookup',
            title: 'Verses: Luke 10:10-15',
            translation_id: 'fin-1992',
            verses: [
              { book_id: 'LUK', chapter: 10, verse: 10, text: 'a' },
              { book_id: 'LUK', chapter: 10, verse: 11, text: 'b' },
              { book_id: 'LUK', chapter: 10, verse: 15, text: 'c' },
            ],
          }),
          { status: 200 },
        ),
      ) as unknown as typeof fetch,
    );

    const out = await repo.getVerse('Luke 10:10-15', 'fin-1992');
    expect(out.reference).toBe('LUK 10:10-15');
  });

  it('formats cross-chapter range reference', async () => {
    const repo = new BibleRepository();
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            type: 'verse_lookup',
            title: 'Verses: Luke 10:45-11:2',
            translation_id: 'web',
            verses: [
              { book_id: 'LUK', chapter: 10, verse: 45, text: 'a' },
              { book_id: 'LUK', chapter: 11, verse: 2, text: 'b' },
            ],
          }),
          { status: 200 },
        ),
      ) as unknown as typeof fetch,
    );

    const out = await repo.getVerse('Luke 10:45-11:2', 'web');
    expect(out.reference).toBe('LUK 10:45-11:2');
  });
});

