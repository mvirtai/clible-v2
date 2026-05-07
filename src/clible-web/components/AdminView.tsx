/**
 * AdminView provides a minimal admin dashboard for capability toggles.
 *
 * Purpose:
 * - Let admins grant/revoke beta AI access (users.ai_access)
 * - Let admins promote/demote other admins (users.is_admin)
 *
 * Security:
 * - The server enforces authorization via requireAdmin on /api/admin/*
 * - This UI is just an affordance; it must never be treated as the security boundary.
 */

import { useEffect, useMemo, useState } from "react";

import type { AdminUserRow } from "../types/admin";
import { adminRepository } from "../repositories/adminRepository";

type Props = {
  currentUserId: string;
};

function normalizeQuery(q: string): string {
  return q.trim().replace(/\s+/g, " ");
}

export function AdminView({ currentUserId }: Props) {
  const [query, setQuery] = useState("");
  const [users, setUsers] = useState<AdminUserRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savingUserId, setSavingUserId] = useState<string | null>(null);

  const effectiveQuery = useMemo(() => normalizeQuery(query), [query]);

  const load = async (q?: string) => {
    setLoading(true);
    setError(null);
    try {
      const rows = await adminRepository.listUsers({ query: q, limit: 50 });
      setUsers(rows);
    } catch (e: unknown) {
      setUsers([]);
      setError(e instanceof Error ? e.message : "Failed to load admin users.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load("");
  }, []);

  const patch = async (id: string, next: { aiAccess?: boolean; isAdmin?: boolean }) => {
    setSavingUserId(id);
    setError(null);
    try {
      const updated = await adminRepository.patchUser(id, next);
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to update user.");
    } finally {
      setSavingUserId(null);
    }
  };

  return (
    <section className="space-y-6">
      <div className="flex items-start justify-between gap-6">
        <div className="space-y-1">
          <h2 className="text-2xl font-semibold tracking-tight">Admin</h2>
          <p className="text-sm text-[#8E8E8E]">
            Manage beta access for Gemini-backed features and admin privileges.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by username…"
            className="w-64 border border-[var(--border)] bg-[var(--surface)] rounded-xl px-3 py-2 text-sm outline-none focus:border-[var(--text)]"
          />
          <button
            type="button"
            onClick={() => void load(effectiveQuery)}
            className="px-4 py-2 rounded-xl text-sm font-medium bg-[var(--text)] text-[var(--surface)] hover:opacity-90 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Loading…" : "Search"}
          </button>
        </div>
      </div>

      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      <div className="overflow-x-auto border border-[var(--border)] rounded-2xl bg-[var(--surface)]">
        <table className="min-w-full text-sm">
          <thead className="border-b border-[var(--border)] bg-[color:color-mix(in_srgb,var(--surface)_70%,transparent)]">
            <tr>
              <th className="text-left font-medium px-4 py-3">Username</th>
              <th className="text-left font-medium px-4 py-3">AI access</th>
              <th className="text-left font-medium px-4 py-3">Admin</th>
              <th className="text-right font-medium px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 && !loading && (
              <tr>
                <td className="px-4 py-4 text-[#8E8E8E]" colSpan={4}>
                  No users found.
                </td>
              </tr>
            )}

            {users.map((u) => {
              const isSelf = u.id === currentUserId;
              const saving = savingUserId === u.id;
              return (
                <tr key={u.id} className="border-b border-[var(--border)] last:border-b-0">
                  <td className="px-4 py-3 font-medium">
                    {u.username}
                    {isSelf && (
                      <span className="ml-2 text-xs text-[#8E8E8E] font-normal">(you)</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <label className="inline-flex items-center gap-2 select-none">
                      <input
                        type="checkbox"
                        checked={u.ai_access}
                        disabled={saving}
                        onChange={(e) => void patch(u.id, { aiAccess: e.target.checked })}
                      />
                      <span className="text-[#8E8E8E]">Enabled</span>
                    </label>
                  </td>
                  <td className="px-4 py-3">
                    <label className="inline-flex items-center gap-2 select-none">
                      <input
                        type="checkbox"
                        checked={u.is_admin}
                        disabled={saving || isSelf}
                        onChange={(e) => void patch(u.id, { isAdmin: e.target.checked })}
                      />
                      <span className="text-[#8E8E8E]">Enabled</span>
                    </label>
                    {isSelf && (
                      <div className="text-xs text-[#8E8E8E] mt-1">
                        Self-demotion disabled
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      type="button"
                      className="px-3 py-1.5 rounded-lg text-xs font-medium border border-[var(--border)] hover:bg-[#F5F5F5] disabled:opacity-50"
                      disabled={saving}
                      onClick={() => void patch(u.id, { aiAccess: !u.ai_access })}
                    >
                      {saving ? "Saving…" : u.ai_access ? "Disable AI" : "Enable AI"}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

