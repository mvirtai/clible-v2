-- Migration 002: UI language preference for web app (EN/FI)

ALTER TABLE user_settings
  ADD COLUMN IF NOT EXISTS ui_language TEXT NOT NULL DEFAULT 'en';
