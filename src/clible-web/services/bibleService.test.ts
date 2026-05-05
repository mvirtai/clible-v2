import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';

import type { InstalledTranslation } from '../types/bible';
import { BibleService } from './bibleService';

const installed: InstalledTranslation[] = [
  { id: 'greeksblgnt', name: 'Greek SBLGNT', language: 'grc', format: 'usfx' },
  { id: 'heb-leningrad', name: 'Hebrew Leningrad', language: 'he', format: 'usfx' },
  { id: 'fin-1992', name: 'FIN 1992', language: 'fi', format: 'usfx' },
  { id: 'web', name: 'World English Bible', language: 'en', format: 'usfx' },
];

describe('BibleService.getOriginalStudyResult', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('throws when reference is missing', async () => {
    const service = new BibleService();
    await expect(service.getOriginalStudyResult('   ', 'greeksblgnt', ['fin-1992'], installed)).rejects.toThrow(
      'Reference is required.',
    );
  });

  it('throws when no target translations remain', async () => {
    const service = new BibleService();
    await expect(
      service.getOriginalStudyResult('John 3:16', 'greeksblgnt', ['greeksblgnt'], installed),
    ).rejects.toThrow('Select at least one translation to compare.');
  });

  it('builds payload and returns result for grc source', async () => {
    const service = new BibleService();
    const fetchMock = vi.fn();

    fetchMock
      // Original lookup
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            verses: [{ book_id: 'JHN', chapter: 3, verse: 16, text: 'ΟΥΤΩΣ ΓΑΡ ΗΓΑΠΗΣΕΝ' }],
          }),
          { status: 200 },
        ),
      )
      // Finnish lookup
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            verses: [{ book_id: 'JHN', chapter: 3, verse: 16, text: 'Sillä niin on Jumala rakastanut' }],
          }),
          { status: 200 },
        ),
      )
      // English lookup
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            verses: [{ book_id: 'JHN', chapter: 3, verse: 16, text: 'For God so loved' }],
          }),
          { status: 200 },
        ),
      )
      // AI endpoint
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ text: 'analysis body' }), { status: 200 }),
      );

    vi.stubGlobal('fetch', fetchMock as typeof fetch);

    const out = await service.getOriginalStudyResult(
      ' John 3:16 ',
      'greeksblgnt',
      ['fin-1992', 'web', 'web'],
      installed,
    );

    expect(out.reference).toBe('John 3:16');
    expect(out.sourceLanguage).toBe('grc');
    expect(out.analysis).toBe('analysis body');
    expect(out.translations.map((t) => t.id)).toEqual(['fin-1992', 'web']);

    const aiCall = fetchMock.mock.calls[3];
    expect(String(aiCall[0])).toBe('/api/ai/original-study');
    const body = JSON.parse(String((aiCall[1] as RequestInit).body));
    expect(body.sourceLanguage).toBe('grc');
    expect(body.translations).toHaveLength(2);
    expect(body.reference).toBe('John 3:16');
    expect(body.sourceText).toContain('ΟΥΤΩΣ');
  });

  it('uses he source language for hebrew originals', async () => {
    const service = new BibleService();
    const fetchMock = vi.fn();

    fetchMock
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            verses: [{ book_id: 'GEN', chapter: 1, verse: 1, text: 'בְּרֵאשִׁית בָּרָא' }],
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            verses: [{ book_id: 'GEN', chapter: 1, verse: 1, text: 'Alussa loi Jumala' }],
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(new Response(JSON.stringify({ text: 'ok' }), { status: 200 }));

    vi.stubGlobal('fetch', fetchMock as typeof fetch);

    await service.getOriginalStudyResult('Genesis 1:1', 'heb-leningrad', ['fin-1992'], installed);

    const aiCall = fetchMock.mock.calls[2];
    const body = JSON.parse(String((aiCall[1] as RequestInit).body));
    expect(body.sourceLanguage).toBe('he');
  });

  it('throws if original lookup has no source text', async () => {
    const service = new BibleService();
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce(new Response(JSON.stringify({ verses: [] }), { status: 200 }))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            verses: [{ book_id: 'JHN', chapter: 3, verse: 16, text: 'Sillä niin' }],
          }),
          { status: 200 },
        ),
      );

    vi.stubGlobal('fetch', fetchMock as typeof fetch);

    await expect(
      service.getOriginalStudyResult('John 3:16', 'greeksblgnt', ['fin-1992'], installed),
    ).rejects.toThrow('No original-language text found for this reference.');
  });

  it('surfaces API error details from original-study endpoint', async () => {
    const service = new BibleService();
    const fetchMock = vi.fn();

    fetchMock
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            verses: [{ book_id: 'JHN', chapter: 3, verse: 16, text: 'ΟΥΤΩΣ' }],
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            verses: [{ book_id: 'JHN', chapter: 3, verse: 16, text: 'For God so loved' }],
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ details: 'Rate limit exceeded' }), { status: 429 }),
      );

    vi.stubGlobal('fetch', fetchMock as typeof fetch);

    await expect(
      service.getOriginalStudyResult('John 3:16', 'greeksblgnt', ['web'], installed),
    ).rejects.toThrow('Rate limit exceeded');
  });
});

