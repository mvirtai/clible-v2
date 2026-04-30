# feat(docker): persist web data, fix session cookie, and harden Docker setup

Builds on the Phase 1 user authentication PR. Fixes a critical session cookie bug that prevented
protected API routes from working over HTTP, and adds proper Docker data persistence for the
user database and sessions.

## Summary

- **Session cookie bug fixed**: `package.json` `start` script hardcoded `NODE_ENV=production`,
  causing `cookie.secure: true` always. Express-session skips setting the cookie on non-HTTPS
  connections, so the browser never received a session ID. Removed the hardcode; `NODE_ENV` now
  comes from the container environment (`ENV NODE_ENV=production` in Dockerfile, overridable via
  `-e NODE_ENV=development` in the debug task).
- **Dockerfile CMD simplified**: Removed the `export NODE_ENV=production` override in `CMD` that
  blocked the debug task's `-e NODE_ENV=development` from reaching `server.ts`.
- **Data persistence**: Added `mkdir -p data` and `VOLUME ["/app/web/data"]` to the Dockerfile so
  `users.db` and sessions survive container restarts.
- **Taskfile**: Both `web-docker-run` and `web-docker-debug` now mount `-v clible-web-data:/app/web/data`
  and pass through `SESSION_SECRET`.
- **Node.js 20 → 22**: Updated `setup_20.x` to `setup_22.x` to silence EBADENGINE warnings from
  `@vitejs/plugin-react`.
- **OCI labels**: Added `org.opencontainers.image.title/description/source` labels.
- **HEALTHCHECK**: Added `curl -f http://localhost:3000/` check (30s interval, 5s timeout, 15s start period).
- **React useEffect guards**: Translations and history effects now guard with `if (!user) return`
  and depend on `[user]` so protected API calls are never made before authentication is confirmed.
- **Dockerfile comments**: Converted Finnish comments to English per project convention.

## Files modified

- `src/clible-web/Dockerfile` — Node 22, OCI labels, HEALTHCHECK, data dir, VOLUME, simplified CMD.
- `src/clible-web/package.json` — removed hardcoded `NODE_ENV=production` from `start` script.
- `Taskfile.yml` — `clible-web-data` volume and `SESSION_SECRET` passthrough in both docker tasks.
- `src/clible-web/App.tsx` — `useEffect` guards for translations and history; `LogOut` button in header.

## Test plan

Manual:
1. `task web-docker-debug` — server starts, `NODE_ENV=development` is in effect.
2. Register a new user → login succeeds, main app renders.
3. Open translation selector → no "Authentication required." error.
4. Stop and restart container — user and session data persist via `clible-web-data` volume.
5. `task web-docker-run` — `NODE_ENV=production` from Dockerfile ENV; app works over HTTP on localhost.
