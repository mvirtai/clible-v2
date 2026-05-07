/**
 * Authorization helpers for the web server.
 *
 * This module is the server-side enforcement point for sensitive capabilities:
 * - Admin-only routes (/api/admin/*)
 * - Gemini-backed AI routes (/api/ai/*)
 *
 * The frontend may hide UI affordances, but these checks are the real boundary.
 */

import type { NextFunction, Request, Response } from "express";
import { pool } from "../db/pool.js";

export type UserAccessRow = {
  id: string;
  username: string;
  ai_access: boolean;
  is_admin: boolean;
};

export async function getUserAccessById(userId: string): Promise<UserAccessRow | null> {
  const { rows } = await pool.query<UserAccessRow>(
    "SELECT id, username, ai_access, is_admin FROM users WHERE id = $1",
    [userId],
  );
  return rows[0] ?? null;
}

function respondNotAuthenticated(res: Response): void {
  res.status(401).json({ error: "Not authenticated." });
}

function respondForbidden(res: Response, hint?: string): void {
  res.status(403).json({ error: "Forbidden.", ...(hint ? { hint } : {}) });
}

/**
 * Require that the current session belongs to an admin user.
 *
 * Returns:
 * - 401 if the request has no authenticated session
 * - 403 if the user exists but is not an admin
 */
export async function requireAdmin(req: Request, res: Response, next: NextFunction) {
  const userId = req.session?.userId;
  if (!userId) {
    respondNotAuthenticated(res);
    return;
  }

  const user = await getUserAccessById(userId);
  if (!user) {
    respondNotAuthenticated(res);
    return;
  }

  if (!user.is_admin) {
    respondForbidden(res);
    return;
  }

  next();
}

/**
 * Require that the current session user is allowed to call Gemini-backed endpoints.
 *
 * Returns:
 * - 401 if the request has no authenticated session
 * - 403 if the user exists but does not have AI access enabled
 */
export async function requireAiAccess(req: Request, res: Response, next: NextFunction) {
  const userId = req.session?.userId;
  if (!userId) {
    respondNotAuthenticated(res);
    return;
  }

  const user = await getUserAccessById(userId);
  if (!user) {
    respondNotAuthenticated(res);
    return;
  }

  if (!user.ai_access) {
    respondForbidden(res, "Request beta access to enable AI features.");
    return;
  }

  next();
}

