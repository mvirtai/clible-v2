import type { NextFocusItem } from "../utils/nextFocus";

export interface OriginalStudyVerse {
    book_name: string;
    chapter: number;
    verse: number;
    text: string;
  }

  export type StudyScope = "verse" | "chapter" | "book";
  
  export interface OriginalStudyTranslation {
    id: string;
    name: string;
    verses: OriginalStudyVerse[];
  }
  
  export interface OriginalStudyResult {
    reference: string;
    scope: StudyScope;
    originalId: string;
    sourceLanguage: "grc" | "he";
    originalVerses: OriginalStudyVerse[];
    translations: OriginalStudyTranslation[];
    analysis: string;
    nextFocus?: NextFocusItem[];
  }