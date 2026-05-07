-- Migration 003: user capability flags for admin-controlled access.
--
-- Purpose:
-- - ai_access: allows calling Gemini-backed endpoints (/api/ai/*)
-- - is_admin: allows using admin-only endpoints (/api/admin/*)
--
-- Defaults are false so existing and newly registered users do not gain access implicitly.

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS ai_access BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;

