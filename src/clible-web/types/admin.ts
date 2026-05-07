/**
 * Admin domain types for the web UI.
 *
 * Purpose: keep /api/admin payload shapes explicit and easy to reuse across
 * the admin panel components and repository.
 */

export type AdminUserRow = {
  id: string;
  username: string;
  ai_access: boolean;
  is_admin: boolean;
};

export type AdminUserPatch = {
  aiAccess?: boolean;
  isAdmin?: boolean;
};

