# Web Integration Guide

This document explains how **Clible Web** connects the React frontend with the Clible CLI backend, and how data flows through the system.

---

## 📚 The Simple Explanation (ELI5)

Imagine Clible Web as a **translator between you and a library**:

- **You** (the user) speak English and use a web browser
- **The library** (Clible CLI) speaks a technical language and lives on a computer
- **The translator** (Express Bridge) sits between you and the library, converting your requests into library language, then translating the library's answers back to English

Here's how it works:

1. **You type** "John 3:16" in the search box
2. **Your browser** sends this to the translator (Express server)
3. **The translator** converts it to: `clible verse "John 3:16" --json`
4. **The library** (Clible CLI) looks it up and returns the result in JSON format
5. **The translator** shows you the result in your browser

This happens instantly because the translator and library are in the **same Docker container** — no waiting for slow internet!

---

## 🏗️ System Architecture

### The Unified Container Design

```
┌─────────────────────── Docker Container ────────────────────────┐
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Browser (Your Computer)                                │   │
│  │  • React/Vite Frontend (Port 5173 in dev)              │   │
│  │  • TypeScript UI Code                                   │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │ HTTP                                       │
│  ┌──────────────────▼──────────────────────────────────────┐   │
│  │  Express Server (Port 3000)                             │   │
│  │  • API Bridge Layer                                      │   │
│  │  • Session Management & Authentication                 │   │
│  │  • Gemini AI Proxy                                       │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │ spawn child_process                       │
│  ┌──────────────────▼──────────────────────────────────────┐   │
│  │  Clible CLI (Python)                                    │   │
│  │  • Bible Text Engine                                     │   │
│  │  • SQLite FTS5 Search Index                              │   │
│  │  • Text Analytics (word counts, frequency, etc.)        │   │
│  │  • Translation Management                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Why This Design?

1. **Fast**: Everything in one container = zero network latency for Bible lookups
2. **Secure**: Sensitive operations (Bible texts, user passwords) never leave your machine
3. **Simple**: Install translations once, they're available everywhere
4. **Offline**: Once you've downloaded a translation, you don't need internet to search

---

## 🔄 Data Flow Diagram

```
User Action                Frontend (React)              Backend (Express)         Engine (Clible CLI)
─────────────────────────────────────────────────────────────────────────────────────────────────

1. Type "John 3:16"  ──────────────────────────────────────────────────────────────────────────
2. Click Search      ──→  App.tsx state change
                         ↓
                     Search validation
                     ↓
3. ◄────────────────  bibleRepository.getVerse()
                         ↓
                     HTTP GET /api/clible?cmd=verse&args="John+3:16"+...
                     ↓
4. ◄────────────────────────────────────────────────────→  sanitize args
                     ┌─────────────────────────────────────────────────────────────────
                     │ child_process.spawn("clible", ["verse", "John 3:16", "--json"])
                     │
                     │ Clible CLI executes:
                     │ • Looks up verse in SQLite database
                     │ • Returns: {"reference": "John 3:16", "text": "..."}
                     │
                     └─────────────────────────────────────────────────────────────────
                         ↓
5. ◄────────────────  JSON response
                     ↓
                     Parse JSON
                     ↓
6. ◄────────────────  HTTP response (200 OK)
                         ↓
                     Update: setResult()
                     ↓
7. ◄───────────────── Render: ReaderView component
                         ↓
                     User sees verse on screen ──────── 👤
```

---

## 🌉 The Express API Bridge (`server.ts`)

The Express server is the **central nervous system** of Clible Web. Here's what it does:

### 1. Spawns CLI Commands

When you request a verse, the server runs the `clible` command exactly as if you typed it in a terminal:

```javascript
// Frontend request
GET /api/clible?cmd=verse&args="John 3:16" -t web

// Express converts to
spawn('clible', ['verse', 'John 3:16', '-t', 'web', '--json'])

// Clible responds with JSON
{ "reference": "John 3:16", "verses": [...], "text": "..." }

// Express forwards to frontend
```

### 2. Manages Authentication

Before running **any** clible command, the server checks:
- Is this user logged in? (Session cookie)
- If not → Block the request with 401 Unauthorized

```javascript
app.get('/api/clible', requireAuth, async (req, res) => {
  // Only authenticated users get here
  // ...
})
```

### 3. Proxies Gemini AI Calls

AI features (tone analysis, study insights) use Google's Gemini API. The server:
- Receives text from the frontend
- Sends it to Gemini with your API key (**never exposed to the browser**)
- Returns the result to you

```
Browser → "Analyze this verse" → Express + GEMINI_API_KEY → Google Servers
          ← Analysis result ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

### 4. Supported Commands

| Endpoint | Command | Purpose |
|----------|---------|---------|
| `/api/clible?cmd=verse` | `clible verse` | Fetch one verse or range |
| `/api/clible?cmd=search` | `clible search` | Full-text search |
| `/api/clible?cmd=analytics` | `clible analytics` | Word counts, frequency, stats |
| `/api/clible?cmd=seed` | `clible seed list` | List installed translations |

---

## 📦 Frontend Architecture Layers

Your React app is organized into clear layers, each with a specific job:

```
App.tsx (State & Coordination)
   ↑
   │ uses
   ↓
components/  (UI Display)
   ↑
   │ calls
   ↓
services/  (Business Logic)
   ↑
   │ calls
   ↓
repositories/  (HTTP Abstraction)
   ↑
   │ HTTP GET/POST
   ↓
/api/  (Express Backend)
```

### Layer 1: Types (`types/`)

Defines the **shape of data** so TypeScript can verify everything matches:

```typescript
// types/bible.ts
interface BibleResponse {
  reference: string;      // "John 3:16"
  verses: Verse[];        // Array of verse objects
  text: string;           // Full text as one string
  translation_name: string; // "Web"
}

interface TextStats {
  wordCount: number;
  charCount: number;
  avgWordLength: string;
  uniqueWords: number;
}
```

### Layer 2: Repository (`repositories/bibleRepository.ts`)

**Pure HTTP calls** — translates user requests into API calls:

```typescript
async getVerse(reference: string, translation: string): Promise<BibleResponse> {
  const args = `"${reference}" -t ${translation}`;
  const response = await fetch(`/api/clible?cmd=verse&args=${encodeURIComponent(args)}`);
  return response.json();
}
```

This layer handles:
- Building correct query strings
- Error handling
- JSON parsing

### Layer 3: Service (`services/bibleService.ts`)

**Business logic** — makes decisions about how to use the data:

```typescript
// Example: Building analytics arguments
async getNativeAnalytics(
  type: 'reference' | 'chapter' | 'book',
  value: string,
  translation: string
) {
  let args = '';
  
  if (type === 'reference') {
    args = `reference "${value}" --translation ${translation}`;
  } else if (type === 'chapter') {
    // Extract book name from something like "John 3"
    const parts = value.split(' ');
    const book = parts.slice(0, -1).join(' ');
    const chapter = parts[parts.length - 1];
    args = `chapter "${book}" ${chapter} --translation ${translation}`;
  }
  
  // Fetch and parse analytics...
}
```

This layer handles:
- Converting "John 3" to `chapter "John" 3` (correct CLI format)
- AI insight prompts
- Combining multiple API calls

### Layer 4: Components (`components/` & `views/`)

**Pure UI** — only render data, don't fetch:

```typescript
// ReaderView.tsx - just shows verse text
function ReaderView({ result }) {
  return (
    <div className="verse">
      <h2>{result.reference}</h2>
      <p>{result.text}</p>
    </div>
  );
}

// Never calls API directly, only receives props
```

### Layer 5: App.tsx

**Orchestration** — ties everything together:

```typescript
const [result, setResult] = useState<BibleResponse | null>(null);

async function handleSearch(query: string) {
  try {
    const result = await bibleRepository.getVerse(query, selectedTranslation);
    setResult(result); // Update state
    setViewMode('reader'); // Switch view
  } catch (e) {
    setError(e.message);
  }
}
```

---

## 🔐 Authentication & Sessions

### How Login Works

```
1. User clicks "Register" → Submits username + password
   ↓
2. Express hashes password with bcrypt (slow, secure hash)
   ↓
3. Stores user record in SQLite: users table
   ↓
4. Creates session cookie (secure, httpOnly)
   ↓
5. Browser automatically includes cookie in future requests
   ↓
6. Express verifies cookie before allowing /api/* access
```

### Session Storage

Sessions are stored in SQLite (not memory), so:
- Sessions persist across server restarts
- Multiple instances can share sessions (with same database)
- Sessions auto-expire after 24 hours

```sql
-- Every login creates/updates this:
INSERT OR REPLACE INTO sessions (sid, data, expires)
VALUES ('session-id-123', '{"userId": "..."}', 1713000000)
```

### Per-User Settings

Once logged in, users can save preferences:

```sql
-- User's translation preference, theme, etc.
UPDATE user_settings 
SET translation_id = 'esv', theme = 'dark'
WHERE user_id = 'uuid-123'
```

---

## 🤖 AI Integration

### Gemini API (Server-Side Only)

AI features are **never exposed to the browser**:

1. **Frontend** sends plain text to Express
2. **Express** adds your `GEMINI_API_KEY` (server-only env variable)
3. **Gemini API** returns analysis
4. **Express** sends result back to frontend

```typescript
// server.ts - AI endpoint
app.post('/api/ai/insight', requireAuth, async (req, res) => {
  const { text } = req.body; // From user
  
  // API key stays on server, never sent to browser
  const aiClient = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  
  const response = await aiClient.models.generateContent({
    model: 'gemini-2.0-flash',
    contents: buildInsightUserPrompt(text),
    config: { systemInstruction: insightSystemInstruction }
  });
  
  res.json({ text: response.text });
});
```

### Two Gemini Models

- **`gemini-2.0-flash`** — For insights (exegesis, commentary, context)
- **`gemini-2.0-flash`** — For tone analysis (emotional tone, style, emphasis)

---

## 📊 Text Analytics Pipeline

### Three Scopes of Analysis

When you click "Analytics" after viewing a verse:

```
User selects scope:  REFERENCE         CHAPTER           BOOK
                          ↓                 ↓                ↓
bibleService builds: reference "..."   chapter "..." N   book "..."
                          ↓                 ↓                ↓
Express runs:       clible analytics reference ... --json
                          ↓
Clible CLI returns:  {
                       "token_count": 22,
                       "unique_token_count": 18,
                       "character_count": 123,
                       "word_frequency": [
                         {"name": "Jesus", "value": 1},
                         {"name": "love", "value": 2}
                       ]
                     }
                          ↓
Frontend renders:    Chart + Statistics
```

### What Gets Analyzed

| Scope | Includes | Example |
|-------|----------|---------|
| **Reference** | Only the verses you fetched | `"John 3:16"` = 33 words |
| **Chapter** | Entire chapter containing your verse | `"John 3"` = 1,000+ words |
| **Book** | Entire Bible book | `"John"` = 19,000+ words |

This lets you see:
- Which words are emphasized in THIS verse?
- How does this verse compare to its chapter context?
- What's the pattern across the entire book?

---

## 🚀 Data Export Pipeline

### Supported Formats

```
App state (result, analytics, etc.)
     ↓
ExportModal.tsx (user picks format)
     ↓
bibleService.export()
     ↓
Express: /api/clible?cmd=analytics&args=...&--stdout-export csv
     ↓
Clible CLI formats output
     ↓
Express returns raw file content (Content-Type: text/csv)
     ↓
Browser downloads file ──→ 📥 user_analytics.csv
```

---

## 🔧 Development Workflow

### Running Locally

```bash
# Terminal 1: Start Express backend
npm run dev:api

# Terminal 2: Start Vite frontend
npm run dev:web
```

Then:
- Frontend at `http://localhost:5173` (proxies `/api` to `http://localhost:3000`)
- Backend at `http://localhost:3000`

### Making a Change

1. **Edit React component** → Vite auto-reloads in browser
2. **Edit Express server** → Restart `npm run dev:api`
3. **Edit types** → TypeScript auto-checks everything
4. **Add new API endpoint** → Update `repositories/` + `services/` + `components/`

### Testing the Bridge

In your browser's developer console:

```javascript
// Test if API bridge works
fetch('/api/clible?cmd=verse&args="John%203:16"')
  .then(r => r.json())
  .then(d => console.log(d))
```

---

## 🐳 Docker Deployment

### Build Process

```bash
docker build -f src/clible-web/Dockerfile -t clible-web .
```

The Dockerfile:
1. Starts with `clible-v2dev` image (has Clible CLI pre-installed)
2. Adds Node.js
3. Installs npm dependencies
4. Builds React app with Vite (`npm run build`)
5. Runs Express on port 3000 (`npm run start`)

### Environment Variables at Runtime

```bash
docker run \
  -e GEMINI_API_KEY="AIza..." \
  -e SESSION_SECRET="your-secret" \
  -v clible-data:/home/clible/.clible-data \
  -p 3000:3000 \
  clible-web
```

---

## 📋 API Reference

### `/api/clible` — Bible Engine Bridge

**Query Parameters:**
- `cmd` — Command name: `verse`, `search`, `analytics`, `seed`
- `args` — Space-separated arguments (URL-encoded)

**Examples:**

```
GET /api/clible?cmd=verse&args="John+3:16"++-t+web
GET /api/clible?cmd=search&args="love"++-t+web+-n+50
GET /api/clible?cmd=analytics&args=reference+"John+3:16"+-t+web
```

**Response:**
```json
{
  "reference": "John 3:16",
  "verses": [...],
  "text": "For God so loved the world...",
  "translation_name": "Web"
}
```

### `/api/ai/insight` — Study Insights

**POST** with JSON body:
```json
{
  "text": "For God so loved the world that he gave his only son..."
}
```

**Response:**
```json
{
  "text": "This verse emphasizes God's unconditional love and the significance of Christ's sacrifice..."
}
```

### `/api/ai/tone` — Tone Analysis

Similar to `/api/ai/insight`, returns emotional tone and style analysis.

### `/api/auth/register` — Create Account

**POST** with:
```json
{
  "username": "user123",
  "password": "securepassword"
}
```

### `/api/user/settings` — User Preferences

**GET** — Retrieve current settings
**POST** — Update settings
```json
{
  "translation_id": "esv",
  "theme": "dark"
}
```

---

## 🔍 Debugging Tips

### Enable Bridge Logging

```bash
NODE_ENV=development npm run dev:api
```

In console, look for:
```
[clible-web] bridge: argv clible verse "John 3:16" --json
[clible-web] bridge: stdout chars 543 stderr chars 0
[clible-web] bridge: JSON ok, top-level keys reference,verses,text,translation_name
```

### Check Session Data

```javascript
// In browser console
fetch('/api/user/settings')
  .then(r => r.json())
  .then(d => console.log('Settings:', d))
```

### Test CLI Directly

```bash
# If running locally
clible verse "John 3:16" --json

# If in Docker
docker exec <CONTAINER_ID> clible verse "John 3:16" --json
```

---

## Future Enhancements

- **Bulk Export** — Export multiple verses/ranges at once
- **Verse Linking** — Cross-references within Bible text
- **Commentary Integration** — Fetch external scholarly commentary
- **Cloud Sync** — Back up user settings and history
- **Advanced Search Filters** — Search by word count, readability level, etc.

---

**See also:** [README.md](README.md) for user guide, [ARCHITECTURAL_STRUCTURE.md](ARCHITECTURAL_STRUCTURE.md) for deep technical details.
