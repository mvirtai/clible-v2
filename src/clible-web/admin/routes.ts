/**
 * Admin API endpoints.
 *
 * These routes are intentionally small and narrowly scoped:
 * - Query users by username substring
 * - Toggle capability flags (AI access, admin access)
 *
 * Security boundary: server.ts mounts this router behind requireAdmin,
 * so every handler here assumes the caller is already an authenticated admin.
 */

import { Router } from "express";
import { pool } from "../db/pool.js";

type AdminUserRow = {
  id: string;
  username: string;
  ai_access: boolean;
  is_admin: boolean;
};

function toLimit(value: unknown): number {
  const n = typeof value === "string" ? parseInt(value, 10) : NaN;
  if (!Number.isFinite(n)) return 20;
  return Math.max(1, Math.min(100, n));
}

export const adminRouter = Router();

// GET /api/admin/users?query=...&limit=...
adminRouter.get("/users", async (req, res) => {
  const query = typeof req.query.query === "string" ? req.query.query.trim() : "";
  const limit = toLimit(req.query.limit);

  const whereClause = query ? "WHERE username ILIKE $1" : "";
  const params = query ? [`%${query}%`, limit] : [limit];

  const { rows } = await pool.query<AdminUserRow>(
    `SELECT id, username, ai_access, is_admin
     FROM users
     ${whereClause}
     ORDER BY created_at DESC
     LIMIT $${params.length}`,
    params,
  );

  res.json(rows);
});

type UserPatchBody = {
  aiAccess?: boolean;
  isAdmin?: boolean;
};

function isBoolean(v: unknown): v is boolean {
  return v === true || v === false;
}

// PATCH /api/admin/users/:id { aiAccess?: boolean, isAdmin?: boolean }
adminRouter.patch("/users/:id", async (req, res) => {
  const id = typeof req.params.id === "string" ? req.params.id.trim() : "";
  if (!id) {
    return res.status(400).json({ error: "Missing user id." });
  }

  const body: unknown = req.body;
  if (body == null || typeof body !== "object") {
    return res.status(400).json({ error: "Invalid JSON body." });
  }

  const patch = body as UserPatchBody;
  const wantsAi = patch.aiAccess;
  const wantsAdmin = patch.isAdmin;
  if (wantsAi === undefined && wantsAdmin === undefined) {
    return res.status(400).json({ error: "No changes requested." });
  }
  if (wantsAi !== undefined && !isBoolean(wantsAi)) {
    return res.status(400).json({ error: "Invalid 'aiAccess'. Expected boolean." });
  }
  if (wantsAdmin !== undefined && !isBoolean(wantsAdmin)) {
    return res.status(400).json({ error: "Invalid 'isAdmin'. Expected boolean." });
  }

  const sets: string[] = [];
  const values: unknown[] = [];
  if (wantsAi !== undefined) {
    sets.push(`ai_access = $${values.length + 1}`);
    values.push(wantsAi);
  }
  if (wantsAdmin !== undefined) {
    sets.push(`is_admin = $${values.length + 1}`);
    values.push(wantsAdmin);
  }
  values.push(id);

  const { rows } = await pool.query<AdminUserRow>(
    `UPDATE users
     SET ${sets.join(", ")}
     WHERE id = $${values.length}
     RETURNING id, username, ai_access, is_admin`,
    values,
  );

  const updated = rows[0];
  if (!updated) {
    return res.status(404).json({ error: "User not found." });
  }

  res.json(updated);
});

