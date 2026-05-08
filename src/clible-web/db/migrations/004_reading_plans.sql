-- Migration 004: reading plans + per-user progress.
--
-- reading_plan_templates: seeded catalog of plan templates (JSON entries).
-- user_reading_plans: per-user active/completed plan selection.
-- reading_progress: day completion markers for streak + progress.

CREATE TABLE IF NOT EXISTS reading_plan_templates (
    id            TEXT  PRIMARY KEY,
    name          TEXT  NOT NULL,
    description   TEXT,
    duration_days INT   NOT NULL,
    entries       JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS user_reading_plans (
    id         TEXT        PRIMARY KEY,
    user_id    TEXT        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id    TEXT        NOT NULL REFERENCES reading_plan_templates(id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status     TEXT        NOT NULL DEFAULT 'active'
);

-- Only one active plan per user at a time.
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_plan
  ON user_reading_plans(user_id)
  WHERE status = 'active';

CREATE TABLE IF NOT EXISTS reading_progress (
    id            TEXT        PRIMARY KEY,
    user_plan_id  TEXT        NOT NULL REFERENCES user_reading_plans(id) ON DELETE CASCADE,
    day_number    INT         NOT NULL,
    completed_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_plan_id, day_number)
);

CREATE INDEX IF NOT EXISTS idx_reading_progress_plan_day
  ON reading_progress(user_plan_id, day_number);