# feat(auth): Phase 1 user authentication for clible-web

Adds a complete server-side user authentication system to clible-web. Users can register,
log in, and log out. All Bible query endpoints are now protected and require an active session.
Session state persists across container restarts via a dedicated Docker volume.

## Summary

- **SQLite user store** (`auth/db.ts`): `users`, `sessions`, and `session_queries` tables created
  on startup with `better-sqlite3`.
- **Session management** (`server.ts`): custom `SQLiteStore` class extends `express-session.Store`;
  sessions stored in `users.db` alongside user records.
- **Auth routes** (`auth/routes.ts`): `POST /api/auth/register`, `POST /api/auth/login`,
  `POST /api/auth/logout`, `GET /api/auth/me` — passwords hashed with `bcryptjs` (cost 12),
  IDs generated with `crypto.randomUUID`.
- **Route protection** (`auth/middleware.ts`): `requireAuth` middleware guards `/api/clible`,
  `/api/ai/insight`, and `/api/ai/tone`.
- **React auth context** (`AuthContext.tsx`): `AuthProvider` checks `/api/auth/me` on mount,
  exposes `user`, `loading`, `login`, and `logout` to the component tree.
- **Login view** (`views/LoginView.tsx`): single form handles both register and login modes.
- **App integration** (`App.tsx`): gates the main UI behind authentication; `useEffect` hooks
  guard API calls with `if (!user) return` to prevent pre-auth requests; logout button in header.
- **Session cookie fix**: removed hardcoded `NODE_ENV=production` from the `start` script;
  `cookie.secure` now correctly reflects the runtime environment, fixing session cookies over HTTP.
- **Docker persistence**: `VOLUME ["/app/web/data"]` declared in Dockerfile; both docker Taskfile
  tasks mount `-v clible-web-data:/app/web/data` so `users.db` survives container restarts.
- **Docker hardening**: Node.js 20 → 22, OCI image labels, `HEALTHCHECK`, simplified `CMD`.

## Files added

- `src/clible-web/auth/db.ts` — SQLite connection and schema init for users and sessions.
- `src/clible-web/auth/middleware.ts` — `requireAuth` Express middleware.
- `src/clible-web/auth/routes.ts` — authentication API routes and `express-session` type extension.
- `src/clible-web/AuthContext.tsx` — React context for global auth state.
- `src/clible-web/views/LoginView.tsx` — login/register form component.
- `pr_stories/pr-TBD-web-docker-data-persistence-and-session-fix.md` — PR story for sub-PR #48.

## Files modified

- `src/clible-web/server.ts` — added `SQLiteStore`, `express-session` middleware, `authRouter`, and `requireAuth` on protected routes.
- `src/clible-web/App.tsx` — auth context integration, `useEffect` guards, `LogOut` button.
- `src/clible-web/main.tsx` — wrapped `<App>` with `<AuthProvider>`.
- `src/clible-web/Dockerfile` — Node 22, OCI labels, `HEALTHCHECK`, `VOLUME`, data dir, simplified `CMD`.
- `src/clible-web/package.json` — added `bcryptjs`, `better-sqlite3`, `express-session` and their types; removed hardcoded `NODE_ENV=production` from `start` script.
- `Taskfile.yml` — added `clible-web-data` volume mount and `SESSION_SECRET` passthrough to docker tasks.

## Test plan

```bash
# Build and run in debug mode (NODE_ENV=development, cookie.secure=false)
task web-docker-debug

# 1. Open http://localhost:3000 — login form appears
# 2. Register a new user — redirects to main app
# 3. Open translation selector — no "Authentication required." error
# 4. Verse queries and AI features work (requireAuth passes)
# 5. Sign out — login form reappears
# 6. Stop and restart container — same credentials still work (users.db persisted)
# 7. Log back in — session restored, translations load correctly
```
