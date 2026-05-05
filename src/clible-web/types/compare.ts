/**
 * Structure from `clible analytics compare … --json` (AnalyticService.compare_translations).
 */

export interface AlignedVerse {
  book_id: string;
  chapter: number;
  verse: number;
  text_a: string | null;
  text_b: string | null;
  similarity: number;
  exact_match?: boolean;
}

export interface CompareSummary {
  total_verses: number;
  fully_aligned_verses: number;
  exact_matches: number;
  exact_match_ratio: number;
  average_similarity: number;
  most_similar_verse: { reference: string; similarity: number } | null;
  top_shared_words: [string, number][];
}

export interface CompareResult {
  reference: string;
  translation_a?: string;
  translation_b?: string;
  aligned_verses: AlignedVerse[];
  summary: CompareSummary;
}
