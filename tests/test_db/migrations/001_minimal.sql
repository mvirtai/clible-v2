-- Minimal migration for testing the migration runner.
-- Creates a dummy table so we can verify the migration ran.
CREATE TABLE IF NOT EXISTS _test_dummy (id INTEGER);
