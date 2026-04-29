/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface Verse {
  book_name: string;
  chapter: number;
  verse: number;
  text: string;
}

export interface BibleResponse {
  reference: string;
  verses: Verse[];
  text: string;
  translation_name: string;
}

/** One row from `clible seed list --json`. */
export interface InstalledTranslation {
  id: string;
  name: string;
  language: string;
  format: string;
}

/** One row from `/api/translations/available`. */
export interface AvailableTranslation extends InstalledTranslation {
  size_mb?: number | null;
}

export interface TextStats {
  wordCount: number;
  charCount: number;
  avgWordLength: string;
  uniqueWords: number;
}

export interface WordFrequency {
  name: string;
  value: number;
}

