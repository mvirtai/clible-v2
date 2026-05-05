import type { AnalyticsMode } from '../components/AnalyticsView';
import type { SearchResponse } from '../types/search';
import type { SavedSearchRow, SearchQueryOptions } from '../types/searchQuery';

export function deriveSavedSearchScope(
  searchScope: string,
  scopeValue: string | null,
): SearchQueryOptions['scope'] {
  if (searchScope === 'testament' && scopeValue === 'NT') return 'nt';
  if (searchScope === 'testament' && scopeValue === 'OT') return 'ot';
  if (searchScope === 'book') return 'book';
  return 'bible';
}

export function buildSearchExportArgs(
  searchResponse: SearchResponse,
  translationId: string,
): string {
  let args = `"${searchResponse.query}" -t ${translationId}`;
  if (searchResponse.scope) args += ` --scope ${searchResponse.scope}`;
  if (searchResponse.scopeRef) args += ` -r "${searchResponse.scopeRef}"`;
  if (searchResponse.searchMode) {
    const mode =
      searchResponse.searchMode === 'boolean' ? 'words' : searchResponse.searchMode;
    args += ` --mode ${mode}`;
  }
  if (searchResponse.searchOperator) {
    args += ` --operator ${searchResponse.searchOperator.toLowerCase()}`;
  }
  return args;
}

export function buildAnalyticsExportArgs(
  analyticsMode: AnalyticsMode,
  reference: string,
  translationId: string,
): string {
  if (analyticsMode === 'reference') {
    return `reference "${reference}" -t ${translationId}`;
  }
  if (analyticsMode === 'chapter') {
    const parts = reference.split(' ');
    const book = parts.slice(0, -1).join(' ');
    const chapter = parts[parts.length - 1].split(':')[0];
    return `chapter "${book}" ${chapter} -t ${translationId}`;
  }
  const book = reference.split(' ')[0];
  return `book "${book}" -t ${translationId}`;
}

export function buildCompareExportArgs(
  reference: string,
  leftTranslationId: string,
  rightTranslationId: string,
): string {
  return `compare ${JSON.stringify(reference)} --left ${leftTranslationId} --right ${rightTranslationId}`;
}

export function buildOriginalStudyExportArgs(
  reference: string,
  originalId: string,
): string {
  return `"${reference}" -t ${originalId}`;
}

export function buildSavedSearchOptions(
  saved: SavedSearchRow,
  fallbackTranslationId: string,
): SearchQueryOptions {
  return {
    terms: [saved.query_text.trim()],
    mode: 'phrase',
    operator: 'and',
    scope: deriveSavedSearchScope(saved.search_scope, saved.scope_value),
    book: saved.search_scope === 'book' ? saved.scope_value : null,
    translationId: saved.translation_id ?? fallbackTranslationId,
  };
}

