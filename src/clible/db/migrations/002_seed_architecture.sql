-- Migration 002: Seed Architecture
-- Creates tables for offline Bible data (books, translations, verses)

-- Books table (static reference data for 66 Bible books)
CREATE TABLE books (
    id TEXT PRIMARY KEY,           -- Book abbreviation (GEN, JHN, REV, etc.)
    name TEXT NOT NULL,            -- Full book name (Genesis, John, Revelation)
    testament TEXT NOT NULL,       -- OT or NT
    position INTEGER NOT NULL,     -- Canonical order (1-66)
    chapters INTEGER NOT NULL      -- Number of chapters in book
);

-- Translations table (installed Bible translations)
CREATE TABLE translations (
    id TEXT PRIMARY KEY,           -- Translation abbreviation (web, kjv, fin-biblia)
    name TEXT NOT NULL,            -- Full translation name (World English Bible)
    language TEXT NOT NULL,        -- Language code (en, fi, etc.)
    format TEXT NOT NULL,          -- XML format (USFX, OSIS, Zefania)
    source_url TEXT,               -- GitHub raw URL for XML file
    installed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Verses table (actual Bible text)
CREATE TABLE verses (
    id TEXT PRIMARY KEY,           -- UUID for each verse
    translation_id TEXT NOT NULL,  -- Which translation (web, kjv, etc.)
    book_id TEXT NOT NULL,         -- Which book (GEN, JHN, etc.)
    chapter INTEGER NOT NULL,      -- Chapter number
    verse INTEGER NOT NULL,        -- Verse number
    text TEXT NOT NULL,            -- The actual verse text
    FOREIGN KEY (translation_id) REFERENCES translations(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id),
    UNIQUE(translation_id, book_id, chapter, verse)
);

-- Indexes for fast verse lookups
CREATE INDEX idx_verses_lookup 
    ON verses(translation_id, book_id, chapter, verse);

-- Index for full-text search on verse content
CREATE INDEX idx_verses_search 
    ON verses(text);
