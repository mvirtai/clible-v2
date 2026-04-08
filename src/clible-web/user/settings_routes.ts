import { Router } from "express";
import { usersDb } from "../auth/db";
import { requireAuth } from "../auth/middleware";

type Theme = "light" | "dark" | "system";

type UserSettings = {
  translationId: string | null;
  theme: Theme;
};

type SettingsPatch = {
  translationId?: string | null;
  theme?: Theme;
};

function isTheme(value: unknown): value is Theme {
  return value === "light" || value === "dark" || value === "system";
}

function toSettingsRow(row: unknown): UserSettings | null {
  if (row == null || typeof row !== "object") return null;
  const r = row as { translation_id?: unknown; theme?: unknown };

  const translationId =
    typeof r.translation_id === "string" ? r.translation_id : null;
  const theme = isTheme(r.theme) ? r.theme : "system";

  return { translationId, theme };
}

const selectSettingsStmt = usersDb.prepare(
  "SELECT translation_id, theme FROM user_settings WHERE user_id = ?"
);
const insertDefaultsStmt = usersDb.prepare(
  "INSERT INTO user_settings (user_id, translation_id, theme) VALUES (?, NULL, 'system')"
);
const upsertSettingsStmt = usersDb.prepare(`
  INSERT INTO user_settings (user_id, translation_id, theme, updated_at)
  VALUES (?, ?, ?, datetime('now'))
  ON CONFLICT(user_id) DO UPDATE SET
    translation_id = excluded.translation_id,
    theme = excluded.theme,
    updated_at = datetime('now')
`);

function getOrCreateSettings(userId: string): UserSettings {
  const existing = toSettingsRow(selectSettingsStmt.get(userId));
  if (existing) return existing;

  insertDefaultsStmt.run(userId);
  return { translationId: null, theme: "system" };
}

export const settingsRouter = Router();
settingsRouter.use(requireAuth);

// GET /api/user/settings
settingsRouter.get("/", (req, res) => {
  const userId = req.session.userId;
  const settings = getOrCreateSettings(userId);
  res.json(settings);
});

// PUT /api/user/settings
settingsRouter.put("/", (req, res) => {
  const userId = req.session.userId;
  const body: unknown = req.body;
  if (body == null || typeof body !== "object") {
    return res.status(400).json({ error: "Invalid JSON body." });
  }

  const patch = body as SettingsPatch;

  if (patch.theme !== undefined && !isTheme(patch.theme)) {
    return res
      .status(400)
      .json({ error: "Invalid 'theme'. Expected: light | dark | system." });
  }

  if (
    patch.translationId !== undefined &&
    patch.translationId !== null &&
    typeof patch.translationId !== "string"
  ) {
    return res
      .status(400)
      .json({ error: "Invalid 'translationId'. Expected string or null." });
  }

  const current = getOrCreateSettings(userId);
  const next: UserSettings = {
    translationId:
      patch.translationId !== undefined
        ? patch.translationId
        : current.translationId,
    theme: patch.theme ?? current.theme,
  };

  upsertSettingsStmt.run(userId, next.translationId, next.theme);
  res.json(next);
});