-- Migration 005: Scopes and Saved Results
-- Adds support for grouping saved work into contexts (scopes)

CREATE TABLE scopes (
    id TEXT PRIMARY KEY,           -- UUID
    name TEXT NOT NULL UNIQUE,      -- Name of the scope (e.g. 'default', 'study-paul')
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE saved_searches (
    id TEXT PRIMARY KEY,           -- UUID
    scope_id TEXT NOT NULL,        -- FK to scopes
    name TEXT NOT NULL,            -- User-defined name
    query_text TEXT NOT NULL,      -- The word searched for
    search_scope TEXT NOT NULL,    -- bible, testament, book, chapter, verse
    scope_value TEXT,              -- e.g. "John", "OT", "John 3:16"
    translation_id TEXT,           -- Optional preferred translation ID
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scope_id) REFERENCES scopes(id) ON DELETE CASCADE,
    FOREIGN KEY (translation_id) REFERENCES translations(id) ON DELETE SET NULL
);

CREATE TABLE saved_analyses (
    id TEXT PRIMARY KEY,           -- UUID
    scope_id TEXT NOT NULL,        -- FK to scopes
    name TEXT NOT NULL,            -- User-defined name
    reference TEXT NOT NULL,       -- Bible reference (e.g. John 3:16)
    analysis_type TEXT NOT NULL,   -- top_words, concordance, etc.
    translation_id TEXT,           -- Optional preferred translation ID
    params_json TEXT,              -- JSON string for extra params like top_n
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scope_id) REFERENCES scopes(id) ON DELETE CASCADE,
    FOREIGN KEY (translation_id) REFERENCES translations(id) ON DELETE SET NULL
);

-- Indices for fast listing per scope
CREATE INDEX idx_saved_searches_scope ON saved_searches(scope_id);
CREATE INDEX idx_saved_analyses_scope ON saved_analyses(scope_id);
