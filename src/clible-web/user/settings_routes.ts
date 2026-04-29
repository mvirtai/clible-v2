import { Router } from 'express';
import { pool } from '../db/pool.js';
import { requireAuth } from '../auth/middleware.js';

type Theme = 'light' | 'dark' | 'system';

type UserSettings = {
  translationId: string | null;
  theme: Theme;
};

type SettingsPatch = {
  translationId?: string | null;
  theme?: Theme;
};

function isTheme(value: unknown): value is Theme {
  return value === 'light' || value === 'dark' || value === 'system';
}

function toSettingsRow(row: unknown): UserSettings | null {
  if (row == null || typeof row !== 'object') return null;
  const r = row as { translation_id?: unknown; theme?: unknown };
  return {
    translationId: typeof r.translation_id === 'string' ? r.translation_id : null,
    theme: isTheme(r.theme) ? r.theme : 'system',
  };
}

async function getOrCreateSettings(userId: string): Promise<UserSettings> {
  const { rows } = await pool.query(
    'SELECT translation_id, theme FROM user_settings WHERE user_id = $1',
    [userId],
  );
  const existing = toSettingsRow(rows[0]);
  if (existing) return existing;

  await pool.query(
    "INSERT INTO user_settings (user_id, translation_id, theme) VALUES ($1, NULL, 'system')",
    [userId],
  );
  return { translationId: null, theme: 'system' };
}

export const settingsRouter = Router();
settingsRouter.use(requireAuth);

// GET /api/user/settings
settingsRouter.get('/', async (req, res) => {
  const settings = await getOrCreateSettings(req.session.userId!);
  res.json(settings);
});

// PUT /api/user/settings
settingsRouter.put('/', async (req, res) => {
  const body: unknown = req.body;
  if (body == null || typeof body !== 'object') {
    return res.status(400).json({ error: 'Invalid JSON body.' });
  }

  const patch = body as SettingsPatch;

  if (patch.theme !== undefined && !isTheme(patch.theme)) {
    return res.status(400).json({ error: "Invalid 'theme'. Expected: light | dark | system." });
  }
  if (
    patch.translationId !== undefined &&
    patch.translationId !== null &&
    typeof patch.translationId !== 'string'
  ) {
    return res.status(400).json({ error: "Invalid 'translationId'. Expected string or null." });
  }

  const current = await getOrCreateSettings(req.session.userId!);
  const next: UserSettings = {
    translationId:
      patch.translationId !== undefined ? patch.translationId : current.translationId,
    theme: patch.theme ?? current.theme,
  };

  await pool.query(
    `INSERT INTO user_settings (user_id, translation_id, theme, updated_at)
     VALUES ($1, $2, $3, NOW())
     ON CONFLICT (user_id) DO UPDATE SET
       translation_id = EXCLUDED.translation_id,
       theme          = EXCLUDED.theme,
       updated_at     = NOW()`,
    [req.session.userId, next.translationId, next.theme],
  );

  res.json(next);
});
