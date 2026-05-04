/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type SearchMode = 'phrase' | 'words' | 'wildcard';
export type SearchOperator = 'and' | 'or' | 'not';
export type SearchScope = 'bible' | 'ot' | 'nt' | 'book';

export interface SearchQueryOptions {
  terms: string[];
  mode: SearchMode;
  operator: SearchOperator;
  scope: SearchScope;
  book: string | null;
  translationId: string;
}

export interface SearchHistoryEntry {
  id: string;
  query_text: string;
  search_scope: string;
  scope_value: string | null;
  translation_id: string | null;
  mode: string;
  result_count: number;
  searched_at: string;
}

export interface SavedSearchRow {
  id: string;
  scope_id?: string;
  name: string;
  query_text: string;
  search_scope: string;
  scope_value: string | null;
  translation_id: string | null;
}
