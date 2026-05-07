/**
 * AdminRepository is the single place that touches /api/admin/* from the browser.
 *
 * Purpose: keep the admin UI thin and consistent with existing repository patterns
 * (fetch happens here; components only coordinate state and render).
 */

import type { AdminUserPatch, AdminUserRow } from "../types/admin";

function readErrorMessage(payload: unknown, fallback: string): string {
  if (payload && typeof payload === "object") {
    const p = payload as { error?: unknown; details?: unknown; hint?: unknown };
    if (typeof p.hint === "string" && p.hint.trim()) return p.hint;
    if (typeof p.details === "string" && p.details.trim()) return p.details;
    if (typeof p.error === "string" && p.error.trim()) return p.error;
  }
  return fallback;
}

export class AdminRepository {
  async listUsers(params?: { query?: string; limit?: number }): Promise<AdminUserRow[]> {
    const query = params?.query?.trim() ?? "";
    const limit =
      typeof params?.limit === "number" && Number.isFinite(params.limit)
        ? params.limit
        : 20;

    const search = new URLSearchParams();
    if (query) search.set("query", query);
    if (limit) search.set("limit", String(limit));

    const response = await fetch(`/api/admin/users?${search.toString()}`);
    const payload = (await response.json().catch(() => null)) as unknown;
    if (!response.ok) {
      throw new Error(readErrorMessage(payload, "Failed to load users."));
    }
    if (!Array.isArray(payload)) {
      throw new Error("Invalid admin users response.");
    }
    return payload as AdminUserRow[];
  }

  async patchUser(id: string, patch: AdminUserPatch): Promise<AdminUserRow> {
    const response = await fetch(`/api/admin/users/${encodeURIComponent(id)}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patch),
    });

    const payload = (await response.json().catch(() => null)) as unknown;
    if (!response.ok) {
      throw new Error(readErrorMessage(payload, "Failed to update user."));
    }
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
      throw new Error("Invalid admin patch response.");
    }
    return payload as AdminUserRow;
  }
}

export const adminRepository = new AdminRepository();

