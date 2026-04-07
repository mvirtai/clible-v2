// Types for the FTS5 search feature.

export interface SearchStatistics {
  totalOccurrences: number;
  uniqueVerses: number;
  booksWithMatches: number;
  /** Each entry is [bookId, occurrenceCount], ordered by count descending. */
  topBooks: Array<[string, number]>;
}

export interface SearchResultRow {
  reference: string;
  text: string;
}

export interface SearchResponse {
  rows: SearchResultRow[];
  statistics: SearchStatistics;
  query: string;
  title: string;
  translationId: string | null;
  scope: string | null;
  scopeRef: string | null;
}
