import { describe, expect, it } from 'vitest';

import type { SearchResponse } from '../types/search';
import {
  buildAnalyticsExportArgs,
  buildCompareExportArgs,
  buildOriginalStudyExportArgs,
  buildSavedSearchOptions,
  buildSearchExportArgs,
  deriveSavedSearchScope,
} from './appViewHelpers';

describe('appViewHelpers', () => {
  it('derives saved search scopes correctly', () => {
    expect(deriveSavedSearchScope('testament', 'NT')).toBe('nt');
    expect(deriveSavedSearchScope('testament', 'OT')).toBe('ot');
    expect(deriveSavedSearchScope('book', 'JHN')).toBe('book');
    expect(deriveSavedSearchScope('bible', null)).toBe('bible');
  });

  it('builds search export args with optional fields', () => {
    const searchResponse: SearchResponse = {
      rows: [],
      statistics: { totalOccurrences: 0, uniqueVerses: 0, booksWithMatches: 0, topBooks: [] },
      query: 'grace',
      title: 'Search: grace',
      translationId: 'fin-1992',
      scope: 'book',
      scopeRef: 'JHN',
      searchMode: 'boolean',
      searchOperator: 'AND',
    };
    const args = buildSearchExportArgs(searchResponse, 'fin-1992');
    expect(args).toContain('"grace" -t fin-1992');
    expect(args).toContain('--scope book');
    expect(args).toContain('-r "JHN"');
    expect(args).toContain('--mode words');
    expect(args).toContain('--operator and');
  });

  it('builds analytics args for all modes', () => {
    expect(buildAnalyticsExportArgs('reference', 'John 3:16', 'web')).toBe(
      'reference "John 3:16" -t web',
    );
    expect(buildAnalyticsExportArgs('chapter', 'John 3:16', 'web')).toBe(
      'chapter "John" 3 -t web',
    );
    expect(buildAnalyticsExportArgs('book', 'John 3:16', 'web')).toBe(
      'book "John" -t web',
    );
  });

  it('builds compare and original study export args', () => {
    expect(buildCompareExportArgs('John 3:16', 'fin-1992', 'web')).toContain(
      'compare "John 3:16" --left fin-1992 --right web',
    );
    expect(buildOriginalStudyExportArgs('John 3:16', 'greeksblgnt')).toBe(
      '"John 3:16" -t greeksblgnt',
    );
  });

  it('builds saved-search options with fallback translation id', () => {
    const options = buildSavedSearchOptions(
      {
        id: '1',
        name: 'my search',
        query_text: ' grace ',
        search_scope: 'book',
        scope_value: 'JHN',
        translation_id: null,
      },
      'fin-1992',
    );
    expect(options).toEqual({
      terms: ['grace'],
      mode: 'phrase',
      operator: 'and',
      scope: 'book',
      book: 'JHN',
      translationId: 'fin-1992',
    });
  });
});

