-- Migration 006: Search history
-- Automatically records every search query for quick re-execution

CREATE TABLE search_history (
    id TEXT PRIMARY KEY,
    query_text TEXT NOT NULL,
    search_scope TEXT NOT NULL DEFAULT 'bible',
    scope_value TEXT,
    translation_id TEXT,
    mode TEXT NOT NULL DEFAULT 'phrase',
    result_count INTEGER NOT NULL DEFAULT 0,
    searched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (translation_id) REFERENCES translations(id) ON DELETE SET NULL
);

CREATE INDEX idx_search_history_time ON search_history(searched_at DESC);