# Phase 2 learning notes — User profile and settings

This is a **learning-oriented implementation guide** for Phase 2 of the iterative user auth plan:
moving client-side preferences from `localStorage` into the authenticated server-side domain.

## Phase 1 recap (what we already have)

- **Session auth**: `express-session` with a custom SQLite-backed store.
- **User DB**: `users.db` holds `users` and `sessions`.
- **Protected API**: `/api/clible`, `/api/ai/*` are guarded by `requireAuth`.
- **UI gate**: React app shows login/register first, then the main app.
- **Docker persistence**: `clible-web-data` mounts `/app/web/data` so `users.db` persists.

---

## Goals of Phase 2

### Product goals

- Settings (translation/theme/etc.) persist **across page reloads** and **across browsers**.
- Settings belong to the authenticated user, not to a single device.

### Engineering goals

- The server becomes the **source of truth** for settings.
- The frontend uses a small REST API and keeps only a thin cache in memory.

### Non-goals (keep scope focused)

- OAuth / email verification / password reset (Phase 3).
- Multi-device conflict resolution beyond **last write wins**.
- A full “profile page” UI unless you explicitly want it.

---

## Data model: `user_settings`

### Why a separate table

Settings are user-owned data with a different lifecycle than auth/session data.
Keeping them separate makes schema changes safer and avoids polluting `users`.

### Table shape (recommended v1)

Use **one row per user**:

- `user_id TEXT PRIMARY KEY`
- `translation_id TEXT NULL`
- `theme TEXT NOT NULL` (`'light' | 'dark' | 'system'`)
- `created_at TEXT NOT NULL DEFAULT (datetime('now'))`
- `updated_at TEXT NOT NULL DEFAULT (datetime('now'))`

Why “one row per user”?

- Simple reads: one `SELECT`.
- Simple writes: one `INSERT ... ON CONFLICT(user_id) DO UPDATE`.
- Easy to add columns later.

### Defaults strategy

There are two common approaches:

- **Approach A (recommended)**: create a settings row automatically when the user is created
  (or on first settings read), with defaults like:
  - `translation_id = NULL` (UI selects a default)
  - `theme = 'system'`
- **Approach B**: allow “no row” and compute defaults in the API response.

Approach A is simpler because the UI always receives concrete values after the first call.

---

## API design: `GET/PUT /api/user/settings`

### What we want from the API

- A stable contract the UI can call on startup and after changes.
- Validation on the server side (never trust the client).

### Endpoints

#### `GET /api/user/settings`

- Requires auth (`requireAuth`).
- Returns the current settings for the logged-in user.
- If no settings row exists: create it with defaults and return it (Approach A).

Example response:

```json
{
  "translationId": "kjv",
  "theme": "system"
}
```

#### `PUT /api/user/settings`

- Requires auth (`requireAuth`).
- Accepts **partial updates** (patch-like), e.g. only `translationId`.
- Validates allowed keys and allowed values.
- Writes to SQLite and returns the updated settings.

Example request:

```json
{
  "translationId": "web"
}
```

### Validation rules (recommended)

- `translationId`:
  - `null` or a string
  - optionally validate it exists in `translations.json` (strict) or allow any string (lenient)
- `theme`:
  - must be one of: `light`, `dark`, `system`

Prefer strict validation for `theme`. For `translationId`, strict is nicer UX, but requires the server
to know the translation catalog (either via clible data or static list).

---

## Backend implementation plan (Node/Express)

### Step 1: Extend the DB schema (`users.db`)

- Add `user_settings` table creation to `src/clible-web/auth/db.ts`.
- If you already have data in the volume, remember: schema changes may require a migration strategy
  (for Phase 2 you can still accept resetting the dev volume, but document it).

### Step 2: Add a settings router

Create something like:

- `src/clible-web/user/settings_routes.ts` (router only)
or
- `src/clible-web/user/routes.ts` with `GET/PUT /settings`

Then mount it in `server.ts`:

- `app.use("/api/user", requireAuth, userRouter)` (or apply `requireAuth` per route)

Why a separate router?

- Keeps `server.ts` readable.
- Makes it easy to unit test route handlers.

### Step 3: SQL operations (keep them boring)

Suggested SQL patterns:

- Read:
  - `SELECT translation_id, theme FROM user_settings WHERE user_id = ?`
- Upsert:
  - `INSERT INTO user_settings (user_id, translation_id, theme, updated_at) VALUES (?, ?, ?, datetime('now'))`
  - `ON CONFLICT(user_id) DO UPDATE SET translation_id = excluded.translation_id, theme = excluded.theme, updated_at = datetime('now')`

### Step 4: Use the session user id

All settings reads/writes should use:

- `req.session.userId` as the `user_id` key.

Do not accept `userId` in the request body (prevent horizontal privilege escalation).

---

## Frontend integration plan (React)

### Replace `localStorage` with the settings API

In Phase 1, the app used `localStorage` for:

- `clible_translation_id`
- potentially theme or other preferences later

Phase 2 direction:

- On app boot (after auth is known), fetch settings:
  - `GET /api/user/settings`
- When user changes translation/theme:
  - immediately update UI state (optimistic UI) **and**
  - `PUT /api/user/settings` in the background

### Where to store settings state

Two simple options:

- **Option A (recommended)**: extend `AuthContext` into a broader `UserContext` that includes:
  - `user`
  - `settings`
  - `updateSettings(...)`
- **Option B**: keep `AuthContext` focused on auth only and add a separate `SettingsContext`.

Option B is usually cleaner as the app grows (auth vs preferences are different concerns).

### Handling load order (important)

The app must not call settings endpoints before auth is confirmed.

Pattern:

- `AuthProvider` resolves `user` via `/api/auth/me`.
- Only after `user` is non-null should settings load run.

---

## Testing plan (what to test and why)

Even if Phase 1 didn’t add tests yet, Phase 2 is a good point to start.

### Backend (recommended)

- **GET creates defaults**:
  - no row in `user_settings` → GET returns defaults and inserts a row
- **PUT validates**:
  - invalid `theme` → 400
- **PUT persists**:
  - update `translationId` → subsequent GET returns it
- **Auth required**:
  - unauth GET/PUT → 401

Implementation approach:

- spin up an Express app in tests with an in-memory DB (or a temp sqlite file)
- or unit test the DB functions separately from the router

### Frontend (optional for Phase 2)

- If you add a settings context, test:
  - “loads settings after login”
  - “updates settings and calls PUT”

---

## Common pitfalls (things you should recognize quickly)

### 1) Session cookie not set on HTTP

If `cookie.secure` is true but you are running over plain HTTP, the browser will not store the cookie.
Symptoms:

- `/api/auth/login` returns 200
- next request to protected routes returns 401

Fixes:

- do not hardcode `NODE_ENV=production` in dev
- consider `app.set('trust proxy', 1)` only when behind a real TLS proxy

### 2) “localStorage vs server” double source of truth

During migration, you may temporarily have both:

- a local value in `localStorage`
- a server value in `user_settings`

Rule of thumb:

- server wins once settings are fetched successfully
- only use local fallback before the first successful GET (if you must)

### 3) Partial updates and overwriting fields

If `PUT` accepts partial data, be careful not to overwrite other columns with `NULL`.
One safe approach:

- read current settings
- apply a patch
- write the merged result

Or keep the API simple:

- require both `translationId` and `theme` in PUT (no partials).

---

## Suggested definition of done for Phase 2

- `user_settings` exists and is populated with defaults per user.
- `GET /api/user/settings` returns settings for the current session user.
- `PUT /api/user/settings` updates settings for the current session user.
- UI uses server settings for translation (and optionally theme).
- Restarting the container does not lose settings (`clible-web-data` volume).
