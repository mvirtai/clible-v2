export interface OriginalStudyVerse {
    book_name: string;
    chapter: number;
    verse: number;
    text: string;
  }
  
  export interface OriginalStudyTranslation {
    id: string;
    name: string;
    verses: OriginalStudyVerse[];
  }
  
  export interface OriginalStudyResult {
    reference: string;
    originalId: string;
    sourceLanguage: "grc" | "he";
    originalVerses: OriginalStudyVerse[];
    translations: OriginalStudyTranslation[];
    analysis: string;
  }