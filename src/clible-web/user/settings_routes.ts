import { Router } from 'express';
import { pool } from '../db/pool.js';
import { requireAuth } from '../auth/middleware.js';

type Theme = 'light' | 'dark' | 'system';
type UILanguage = 'en' | 'fi';

type UserSettings = {
  translationId: string | null;
  theme: Theme;
  uiLanguage: UILanguage;
};

type SettingsPatch = {
  translationId?: string | null;
  theme?: Theme;
  uiLanguage?: UILanguage;
};

function isTheme(value: unknown): value is Theme {
  return value === 'light' || value === 'dark' || value === 'system';
}

function isUILanguage(value: unknown): value is UILanguage {
  return value === 'en' || value === 'fi';
}

function toSettingsRow(row: unknown): UserSettings | null {
  if (row == null || typeof row !== 'object') return null;
  const r = row as { translation_id?: unknown; theme?: unknown; ui_language?: unknown };
  const uiLang: UILanguage =
    typeof r.ui_language === 'string' && isUILanguage(r.ui_language) ? r.ui_language : 'en';
  return {
    translationId: typeof r.translation_id === 'string' ? r.translation_id : null,
    theme: isTheme(r.theme) ? r.theme : 'system',
    uiLanguage: uiLang,
  };
}

async function getOrCreateSettings(userId: string): Promise<UserSettings> {
  const { rows } = await pool.query(
    'SELECT translation_id, theme, ui_language FROM user_settings WHERE user_id = $1',
    [userId],
  );
  const existing = toSettingsRow(rows[0]);
  if (existing) return existing;

  await pool.query(
    "INSERT INTO user_settings (user_id, translation_id, theme) VALUES ($1, NULL, 'system')",
    [userId],
  );
  return { translationId: null, theme: 'system', uiLanguage: 'en' };
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
  if (patch.uiLanguage !== undefined && !isUILanguage(patch.uiLanguage)) {
    return res.status(400).json({ error: "Invalid 'uiLanguage'. Expected: en | fi." });
  }

  const current = await getOrCreateSettings(req.session.userId!);
  const next: UserSettings = {
    translationId:
      patch.translationId !== undefined ? patch.translationId : current.translationId,
    theme: patch.theme ?? current.theme,
    uiLanguage: patch.uiLanguage ?? current.uiLanguage,
  };

  await pool.query(
    `INSERT INTO user_settings (user_id, translation_id, theme, ui_language, updated_at)
     VALUES ($1, $2, $3, $4, NOW())
     ON CONFLICT (user_id) DO UPDATE SET
       translation_id = EXCLUDED.translation_id,
       theme          = EXCLUDED.theme,
       ui_language    = EXCLUDED.ui_language,
       updated_at     = NOW()`,
    [req.session.userId, next.translationId, next.theme, next.uiLanguage],
  );

  res.json(next);
});
