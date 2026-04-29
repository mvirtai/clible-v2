-- Migration 001: core user data tables
--
-- sessions uses the schema expected by connect-pg-simple:
--   sid  VARCHAR PRIMARY KEY
--   sess JSON    (full session payload, not just userId)
--   expire TIMESTAMP(6)
-- The library manages this table automatically; do not rename columns.

CREATE TABLE IF NOT EXISTS users (
    id            TEXT        PRIMARY KEY,
    username      TEXT        UNIQUE NOT NULL,
    password_hash TEXT        NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
    sid    VARCHAR      NOT NULL PRIMARY KEY,
    sess   JSON         NOT NULL,
    expire TIMESTAMP(6) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_expire ON sessions (expire);

CREATE TABLE IF NOT EXISTS user_settings (
    user_id        TEXT        PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    translation_id TEXT,
    theme          TEXT        NOT NULL DEFAULT 'system',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
