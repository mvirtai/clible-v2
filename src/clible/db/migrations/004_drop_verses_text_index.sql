-- Migration 004: Drop redundant B-tree index on verses.text
-- Full-text search uses FTS5 (verses_fts); idx_verses_search did not help FTS queries
-- and added storage overhead on INSERT/UPDATE.

DROP INDEX IF EXISTS idx_verses_search;
