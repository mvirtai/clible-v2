<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/78955bc0-b17d-47fa-adca-b4816c2b6882

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Set the `GEMINI_API_KEY` in `.env.local` (or your shell env) to your Gemini API key
3. Run the app:
   `npm run dev`

## Docker

Build from the **repository root** so the image installs the `clible` CLI from this checkout (not only the version baked into the base image):

```bash
docker build -f src/clible-web/Dockerfile -t clible-web-ci .
```

Or: `task web-docker-build` / `task web-docker-run` (same build).

The image sets `CLIBLE_DATA_DIR=/home/clible/.clible-data` so the SQLite DB is writable (the install-time default under `site-packages` is read-only). Persist data across runs:

```bash
docker run --rm -p 3000:3000 -v clible-data:/home/clible/.clible-data clible-web-ci
```

Seed a translation inside the container (e.g. `docker exec ... clible seed install web`) before using verse search.

### Translations in the web UI

The globe menu lists only **installed** translations (`clible seed list`), loaded via the API bridge (`clible seed list --json`). There is no default selection until you pick one. Install translations with `clible seed install <id>` (or `docker exec` into the container), then refresh the page.

- **Security**: `GEMINI_API_KEY` must be provided at **runtime** only. It is never bundled into the browser client.
- **Run with AI enabled**:

```bash
docker run --rm -p 3000:3000 -e GEMINI_API_KEY="YOUR_KEY" <your-image>
```

- **Run without AI** (default): omit `GEMINI_API_KEY`. The app will still work, but AI features return a friendly error.

#### If you see `API key not valid` (400)

The server is receiving *some* key, but Google rejects it. Check:

1. **Use a current key** from [Google AI Studio](https://aistudio.google.com/apikey) (or Cloud Console with **Generative Language API** enabled for that key).
2. **`.env` format**: use `GEMINI_API_KEY=AIza...` on one line, no spaces around `=`. Avoid pasting the placeholder `MY_GEMINI_API_KEY`.
3. **Cloud API key restrictions**: if the key is restricted to **HTTP referrers** or **IP addresses**, server-side calls from Docker will fail. For local testing, use **None** or restrict by API only (allow Generative Language API).
