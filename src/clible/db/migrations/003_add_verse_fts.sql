-- Migration 003: Add FTS5 full-text search index for verses
-- Enables fast text search and concordance queries

-- Create FTS5 virtual table linked to verses table
CREATE VIRTUAL TABLE IF NOT EXISTS verses_fts USING fts5(
    text,
    content='verses',
    content_rowid='rowid'
);

-- Populate FTS index with existing verses
INSERT INTO verses_fts(verses_fts) VALUES ('rebuild');

-- Trigger: sync new verse insertions to FTS index
CREATE TRIGGER IF NOT EXISTS verses_ai AFTER INSERT ON verses BEGIN
    INSERT INTO verses_fts(rowid, text) VALUES (new.rowid, new.text);
END;

-- Trigger: sync verse deletions to FTS index
CREATE TRIGGER IF NOT EXISTS verses_ad AFTER DELETE ON verses BEGIN
    INSERT INTO verses_fts(verses_fts, rowid, text) VALUES('delete', old.rowid, old.text);
END;

-- Trigger: sync verse updates to FTS index (delete old + insert new)
CREATE TRIGGER IF NOT EXISTS verses_au AFTER UPDATE ON verses BEGIN
    INSERT INTO verses_fts(verses_fts, rowid, text) VALUES('delete', old.rowid, old.text);
    INSERT INTO verses_fts(rowid, text) VALUES (new.rowid, new.text);
END;
