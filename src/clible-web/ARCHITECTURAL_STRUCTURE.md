# Architectural Structure

Deep technical documentation of Clible Web's system design, data structures, and implementation patterns.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Module Organization](#module-organization)
3. [Data Flow & State Management](#data-flow--state-management)
4. [Type System Design](#type-system-design)
5. [API Bridge Layer](#api-bridge-layer)
6. [Authentication & Authorization](#authentication--authorization)
7. [Component Architecture](#component-architecture)
8. [Service Layer Pattern](#service-layer-pattern)
9. [Database Schema](#database-schema)
10. [Performance Considerations](#performance-considerations)
11. [Error Handling Strategy](#error-handling-strategy)
12. [Security Architecture](#security-architecture)
13. [Build & Runtime Configuration](#build--runtime-configuration)

---

## System Architecture

### Layered Architecture with Clear Separation of Concerns

```
┌─────────────────────────────────────────────────────────────────┐
│                         Presentation Layer                        │
│                                                                    │
│  App.tsx (Root Container)                                         │
│    ├── ViewMode Management (reader | analytics | search)         │
│    ├── Global State (result, query, loading, error)              │
│    └── Route Coordination                                         │
│                                                                    │
│  ├── ReaderView.tsx                                               │
│  │   └── Verse display + AI insights                             │
│  ├── AnalyticsView.tsx                                            │
│  │   └── Statistics visualization (D3/Recharts)                  │
│  ├── SearchView.tsx                                               │
│  │   └── FTS5 results presentation                               │
│  └── Components/ (SettingsPanel, TranslationModal, ExportModal) │
│                                                                    │
├─────────────────────────────────────────────────────────────────┤
│                      Business Logic Layer                         │
│                                                                    │
│  services/bibleService.ts                                        │
│    ├── getVerse() → calls repository                            │
│    ├── getNativeAnalytics() → argument construction + repo call  │
│    ├── getAiInsight() → Gemini API integration                  │
│    └── getAiTone() → Gemini API integration                     │
│                                                                    │
│  user/SettingsContext.tsx                                        │
│    └── Per-user preference management                            │
│                                                                    │
├─────────────────────────────────────────────────────────────────┤
│                     Data Access Layer (Repository)                │
│                                                                    │
│  repositories/bibleRepository.ts                                 │
│    ├── listInstalledTranslations()                               │
│    ├── getVerse(reference, translation)                          │
│    ├── search(query, translation, limit)                         │
│    └── export(cmd, args, format)                                 │
│                                                                    │
├─────────────────────────────────────────────────────────────────┤
│                      Protocol Layer (HTTP/API)                    │
│                                                                    │
│  Express Server (server.ts)                                       │
│    ├── /api/clible → Clible CLI bridge                          │
│    ├── /api/ai/insight → Gemini proxy                           │
│    ├── /api/ai/tone → Gemini proxy                              │
│    ├── /api/auth/* → Auth handling                              │
│    └── /api/user/settings → Preferences                         │
│                                                                    │
├─────────────────────────────────────────────────────────────────┤
│                      Engine Layer (Python CLI)                    │
│                                                                    │
│  clible (Python)                                                  │
│    ├── verse → SQLite query                                      │
│    ├── search → FTS5 index query                                │
│    ├── analytics → Text metrics + word frequency                │
│    └── seed → Translation management                            │
│                                                                    │
│  SQLite Database                                                  │
│    ├── Bible texts (per translation)                             │
│    ├── FTS5 search index                                         │
│    └── User data (sessions, settings)                            │
│                                                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack Rationale

| Layer | Technology | Why |
|-------|-----------|-----|
| **Presentation** | React 19 + Vite | Fast HMR, excellent tree-shaking, component composition |
| **Styling** | Tailwind + @tailwindcss/vite | Utility-first, minimal CSS output, type-safe theming |
| **State** | useState + Context | Sufficient for this domain, no Redux overhead |
| **Charts** | D3 + Recharts | D3 for flexibility, Recharts for quick charts |
| **Build** | Vite | Instant HMR, optimized prod builds, ESM-native |
| **Backend** | Express | Lightweight, well-understood, minimal overhead for bridge pattern |
| **CLI Bridge** | child_process.spawn | Clean isolation, no IPC overhead, JSON handoff |
| **Database** | SQLite | Self-contained, zero-config, ACID compliance |
| **Session Store** | Custom SQLite Store | Persistent sessions, simple implementation, no external deps |
| **Auth** | bcryptjs + JWT sessions | Standard bcrypt work factor (12), secure httpOnly cookies |

---

## Module Organization

### Directory Structure Philosophy

```
src/clible-web/
├── types/                    # Shared type definitions
│   ├── bible.ts             # Core domain types
│   └── search.ts            # Search response shape
│
├── repositories/            # Data access, HTTP abstraction
│   └── bibleRepository.ts   # All external API calls
│
├── services/                # Business logic, orchestration
│   └── bibleService.ts      # Analytics, AI, verse logic
│
├── components/              # React UI components (pure)
│   ├── ReaderView.tsx       # Verse display
│   ├── AnalyticsView.tsx    # Stats + charts
│   ├── SearchView.tsx       # Search results
│   ├── ExportModal.tsx      # Export dialog
│   ├── TranslationModal.tsx # Translation selector
│   ├── SettingsPanel.tsx    # User settings
│   └── SearchStatsPanel.tsx # Search metadata
│
├── views/                   # Page-level components
│   └── LoginView.tsx        # Authentication UI
│
├── utils/                   # Utilities
│   ├── bookNames.ts         # Bible book name utilities
│   ├── download.ts          # File download helper
│   └── markdownComponents.tsx # Markdown rendering
│
├── auth/                    # Authentication layer
│   ├── db.ts                # SQLite session store
│   ├── middleware.ts        # requireAuth guard
│   └── routes.ts            # /api/auth/* endpoints
│
├── user/                    # User/settings layer
│   ├── SettingsContext.tsx  # Context provider
│   └── settings_routes.ts   # /api/user/settings endpoints
│
├── data/                    # Static data
│   └── bible_structure.json # Book/chapter metadata
│
├── App.tsx                  # Root component, state orchestration
├── main.tsx                 # Vite entry point
├── server.ts                # Express server
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
└── ai.config.ts             # Gemini prompt engineering
```

### Dependency Graph

```
App.tsx
├── useAuth() → AuthContext.tsx (JWT header)
├── useSettings() → SettingsContext.tsx (per-user settings)
├── bibleRepository → HTTP layer
├── bibleService → Business logic
├── Components/
│   ├── ReaderView
│   └── AnalyticsView
│       └── bibleService.getNativeAnalytics()
└── Views/
    └── LoginView → authRouter (/api/auth/*)

bibleRepository.ts
└── fetch /api/clible (Express bridge)

bibleService.ts
├── bibleRepository.getVerse()
├── bibleRepository.search()
├── fetch /api/ai/insight (Gemini)
├── fetch /api/ai/tone (Gemini)
└── Argument construction (CLI format)

server.ts (Express)
├── requireAuth middleware → usersDb
├── /api/clible → child_process.spawn('clible', argv)
├── /api/ai/insight → GoogleGenAI.models.generateContent()
├── /api/ai/tone → GoogleGenAI.models.generateContent()
├── /api/auth/* → bcrypt password handling
└── /api/user/settings → usersDb.prepare()

authRouter.ts
├── POST /register → bcrypt.hash() → usersDb.insert()
├── POST /login → bcrypt.compare() → session.userId
└── POST /logout → session.destroy()

SQLiteStore (express-session)
└── usersDb (better-sqlite3)
    ├── users table
    ├── sessions table
    ├── user_settings table
    └── session_queries table
```

---

## Data Flow & State Management

### React State Management Strategy

Modern React (19+) with minimal dependencies:

```typescript
// App.tsx - Root component state
const [query, setQuery] = useState('');
const [result, setResult] = useState<BibleResponse | null>(null);
const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [viewMode, setViewMode] = useState<'reader' | 'analytics' | 'search'>('reader');
const [analyticsMode, setAnalyticsMode] = useState<'reference' | 'chapter' | 'book'>('reference');
const [nativeStats, setNativeStats] = useState<TextStats | null>(null);
const [nativeFrequency, setNativeFrequency] = useState<WordFrequency[]>([]);
```

**Rationale:**
- Simple, predictable state updates
- No reducer boilerplate
- Type-safe with TypeScript inference
- Effects are explicit with useEffect dependencies

### Context Providers

```typescript
// AuthContext.tsx - Global auth state
interface AuthContextType {
  user: { id: string; username: string } | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
}

// SettingsContext.tsx - Per-user preferences
interface SettingsContextType {
  settings: { translation_id: string; theme: 'light' | 'dark' | 'system' };
  updateSettings: (settings: Partial<typeof settings>) => Promise<void>;
  loading: boolean;
  error: string | null;
}
```

### Async Operation Pattern

All async operations follow this pattern:

```typescript
const handleSearch = async (query: string) => {
  setLoading(true);
  setError(null);
  try {
    const data = await bibleRepository.getVerse(query, selectedTranslation);
    setResult(data);
    setViewMode('reader');
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

Guarantees:
- Loading state always cleared (catch + finally)
- Errors always displayed
- Type-safe error handling

---

## Type System Design

### Domain Types (`types/bible.ts`)

```typescript
export interface Verse {
  book_name: string;
  chapter: number;
  verse: number;
  text: string;
}

export interface BibleResponse {
  reference: string;           // "John 3:16"
  verses: Verse[];             // Array of verse objects
  text: string;                // Raw concatenated text
  translation_name: string;    // "Web"
}

export interface TextStats {
  wordCount: number;
  charCount: number;
  avgWordLength: string;       // Fixed to 1 decimal
  uniqueWords: number;
}

export interface WordFrequency {
  name: string;                // Word
  value: number;               // Frequency count
}

export interface InstalledTranslation {
  id: string;                  // e.g., "esv", "kjv", "web"
  name: string;                // Display name
  language: string;            // ISO language code
  format: string;              // Bible format/standard
}
```

### Search Types (`types/search.ts`)

```typescript
export interface SearchResultRow {
  book_name: string;
  chapter: number;
  verse: number;
  text: string;
}

export interface SearchStatistics {
  total_matches: number;
  search_time_ms: number;
  scope: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResultRow[];
  statistics: SearchStatistics;
  translation_name: string;
}
```

### Type Safety Benefits

- **Compile-time verification** — Typos caught before runtime
- **IDE autocomplete** — All fields available during development
- **Self-documenting** — Types serve as inline docs
- **Backward compatibility** — Type evolution is explicit
- **JSON parsing safety** — No `any` type for clible responses

---

## API Bridge Layer

### Route Sanitization

```typescript
function parseClibleArgTokens(sanitized: string): string[] {
  return (
    sanitized
      .match(/(?:[^\s"]+|"[^"]*")+/g)  // Tokenize respecting quotes
      ?.map((s) => s.replace(/^"(.*)"$/, "$1"))  // Unquote
      .filter(Boolean) ?? []
  );
}

function buildClibleArgv(cmd: string, tokens: string[]): string[] {
  const argv = [cmd, ...tokens];
  
  // Auto-append --json for JSON endpoints
  if (cmd === 'verse' || cmd === 'search' || cmd === 'analytics') {
    if (!tokens.some((t) => t.includes('--stdout-export'))) {
      argv.push('--json');
    }
  }
  
  return argv;
}
```

**Security mechanisms:**
1. **Explicit command allowlist** — Only `verse`, `search`, `analytics`, `seed`
2. **Regex tokenization** — Respectful of quoted arguments
3. **Subprocess isolation** — `spawn()` not shell `exec()`
4. **Character blacklist** — No `;&|`\`$<>`

### Request/Response Cycle

```typescript
app.get('/api/clible', requireAuth, async (req, res) => {
  const { cmd, args } = req.query;
  
  // 1. Validate
  if (!allowedCommands.includes(cmd)) {
    return res.status(403).json({ error: 'Not allowed' });
  }
  
  // 2. Sanitize
  const sanitized = (args as string).replace(/[;&|`$<>`]/g, '');
  const tokens = parseClibleArgTokens(sanitized);
  const argv = buildClibleArgv(cmd, tokens);
  
  // 3. Execute (with timeout guard via Promise.race if needed)
  const { stdout, stderr } = await runClible(argv);
  
  // 4. Parse (with error recovery)
  try {
    const parsed = JSON.parse(stdout);
    res.json(parsed);
  } catch {
    res.status(500).json({ 
      error: 'Invalid JSON from CLI',
      rawOutput: stdout.slice(0, 500)
    });
  }
});
```

### Error Classification

```typescript
function clibleFailureMessage(
  err: Error & { code?: number; stdout?: string; stderr?: string }
): string {
  const combined = `${err.stderr ?? ''}\n${err.stdout ?? ''}`.trim();
  if (combined) return stripAnsi(combined);  // Strip ANSI color codes
  return stripAnsi(err.message);
}

// In error handler:
if (code === 1 && msg.includes('Verse(s) not found')) {
  // Specific user error → 404
  return res.status(404).json({
    error: msg,
    hint: 'Install a translation first'
  });
} else if (code === 127) {
  // clible not in PATH
  return res.status(500).json({
    error: 'CLI not available',
    hint: "Make sure 'clible' is installed"
  });
}
```

---

## Authentication & Authorization

### Session Management Architecture

```typescript
// Custom SQLite session store (express-session compatible)
class SQLiteStore extends session.Store {
  get(sid: string, cb: Callback) {
    const row = usersDb
      .prepare('SELECT data, expires FROM sessions WHERE sid = ?')
      .get(sid);
    
    if (!row || row.expires < Date.now()) {
      return cb(null, null);  // Session expired or missing
    }
    
    try {
      cb(null, JSON.parse(row.data));
    } catch {
      cb(null, null);  // Corrupted session data
    }
  }
  
  set(sid: string, sessionData: any, cb?: Callback) {
    // Compute expiration from session.cookie or default to 24h
    const expires = sessionData.cookie?.expires
      ? new Date(sessionData.cookie.expires).getTime()
      : Date.now() + 24 * 60 * 60 * 1000;
    
    usersDb
      .prepare('INSERT OR REPLACE INTO sessions (sid, data, expires) VALUES (?, ?, ?)')
      .run(sid, JSON.stringify(sessionData), expires);
    
    cb?.();
  }
  
  destroy(sid: string, cb?: Callback) {
    usersDb.prepare('DELETE FROM sessions WHERE sid = ?').run(sid);
    cb?.();
  }
}
```

### Authentication Flow

```
Browser                    Express                       SQLite
───────                    ───────                       ──────

POST /api/auth/register
{username, password}   ─→  validate length
                           bcrypt.hash(pw, 12)
                                              ─→  INSERT users
                                              ←─  user ID
                       ←─  Set-Cookie: connect.sid
                           (session starts)

Subsequent requests
all include cookie     ─→  SQLiteStore.get(sid)
                                              ─→  SELECT from sessions
                                              ←─  session data
                           requireAuth middleware checks
                       ←─  401 if invalid
                           200 if OK
```

### Password Hashing

```typescript
// Registration
const hash = await bcrypt.hash(password, 12);
// Work factor 12 = ~500ms on laptop, balances security/speed

// Login
const match = await bcrypt.compare(password, storedHash);
// Constant-time comparison prevents timing attacks
```

**Note:** Work factor 12 is chosen for:
- ~500ms on modern CPU (prevents brute force)
- Acceptable for login UX
- Not so high it causes timeout on slow boxes

---

## Component Architecture

### Controlled Component Pattern

All user inputs use React's controlled component pattern:

```typescript
function SearchBar() {
  const [query, setQuery] = useState('');
  
  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      onKeyPress={(e) => {
        if (e.key === 'Enter') {
          handleSearch(query);
        }
      }}
    />
  );
}
```

Benefits:
- Single source of truth (React state)
- Validation on change
- Undo/redo capability if needed

### Pure Function Components

All components are pure (no side effects in render):

```typescript
// ✅ Good - pure component
function ReaderView({ result, loading }: Props) {
  return (
    <div>
      {loading && <Spinner />}
      {result && <h2>{result.reference}</h2>}
    </div>
  );
}

// ❌ Bad - has side effect in render
function BadComponent() {
  fetch('/api/...').then(...);  // Don't do this!
  return <div>...</div>;
}
```

### Modal Component Pattern

Modals use a focused state machine:

```typescript
function ExportModal({ isOpen, result, onClose }: Props) {
  const [format, setFormat] = useState<ExportFormat>('csv');
  const [exporting, setExporting] = useState(false);
  
  const handleExport = async () => {
    setExporting(true);
    try {
      // Only one action in progress at a time
      await bibleService.export(...);
    } finally {
      setExporting(false);
      onClose();
    }
  };
  
  if (!isOpen) return null;  // Component unmounts when not visible
  
  return (
    <motion.div aria-modal="true">
      {/* Modal UI */}
      <button onClick={handleExport} disabled={exporting}>
        {exporting ? 'Exporting...' : 'Export'}
      </button>
    </motion.div>
  );
}
```

---

## Service Layer Pattern

### Business Logic Encapsulation

All application logic lives in `services/bibleService.ts`:

```typescript
export class BibleService {
  // Verse operations
  async getVerse(
    reference: string,
    translation: string
  ): Promise<BibleResponse> {
    return bibleRepository.getVerse(reference, translation);
  }
  
  // Analytics with dynamic argument construction
  async getNativeAnalytics(
    type: 'reference' | 'chapter' | 'book',
    value: string,
    translation: string,
    top: number = 10
  ): Promise<{ stats: TextStats; frequency: WordFrequency[] }> {
    let args = '';
    
    switch (type) {
      case 'reference':
        args = `reference "${value}" --translation ${translation} --top ${top}`;
        break;
      case 'chapter':
        const [book, chapter] = parseBookChapter(value);
        args = `chapter "${book}" ${chapter} --translation ${translation} --top ${top}`;
        break;
      case 'book':
        args = `book "${value}" --translation ${translation} --top ${top}`;
        break;
    }
    
    const response = await fetch(
      `/api/clible?cmd=analytics&args=${encodeURIComponent(args)}`
    );
    return parseAnalyticsResponse(await response.json());
  }
  
  // AI integration
  async getAiInsight(result: BibleResponse): Promise<string> {
    const response = await fetch('/api/ai/insight', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: result.text })
    });
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    return data.text ?? '';
  }
}

const bibleService = new BibleService();
```

**Design benefits:**
- Single responsibility (per method)
- Easy to test (mock repository layer)
- Reusable across components
- Argument construction logic isolated

---

## Database Schema

### Users Database (`data/users.db`)

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,                    -- UUID
    username TEXT UNIQUE NOT NULL,          -- Case-sensitive
    password_hash TEXT NOT NULL,            -- bcrypt(12)
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE sessions (
    sid TEXT PRIMARY KEY,                   -- Session ID
    data TEXT NOT NULL,                     -- JSON-stringified session object
    expires INTEGER NOT NULL                -- Unix timestamp ms
);
-- Background cleanup could DELETE WHERE expires < datetime('now')

CREATE TABLE user_settings (
    user_id TEXT PRIMARY KEY,               -- FK → users.id
    translation_id TEXT,                    -- Selected translation ID
    theme TEXT NOT NULL DEFAULT 'system',   -- 'light' | 'dark' | 'system'
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE session_queries (
    session_id TEXT NOT NULL,               -- FK → sessions.sid
    query_id TEXT NOT NULL,
    PRIMARY KEY (session_id, query_id)
    -- Reserved for future query history feature
);
```

### Bible Database (From Clible CLI)

Managed by Clible CLI, not by this app:

```sql
-- Per-translation database
CREATE VIRTUAL TABLE <translation>_fts USING fts5(
    book_name,
    chapter,
    verse,
    text
);

-- Regular table for fast ref lookups
CREATE TABLE <translation>_verses (
    id INTEGER PRIMARY KEY,
    book_name TEXT,
    chapter INTEGER,
    verse INTEGER,
    text TEXT
);

CREATE INDEX idx_book_chapter_verse 
    ON <translation>_verses(book_name, chapter, verse);
```

---

## Performance Considerations

### Client-Side Optimization

```typescript
// 1. Input debouncing (not implemented yet, but recommended)
import { useCallback, useRef } from 'react';

const debouncedSearch = useCallback(
  debounce((query: string) => {
    handleSearch(query);
  }, 300),
  []
);

// 2. Memoization for expensive components
const AnalyticsView = React.memo(function AnalyticsView(props) {
  // Chart rendering is expensive
  return <Rechart {...props} />;
}, (prev, next) => {
  // Custom comparison
  return prev.stats === next.stats && prev.frequency === next.frequency;
});

// 3. Code splitting (Vite auto-handles)
// Large components can be lazy-loaded:
const ReaderView = React.lazy(() => import('./ReaderView'));
```

### Server-Side Optimization

```typescript
// 1. Child process reuse (currently spawns per request)
// Could be optimized with a pool if needed:
// const child = new CliChildProcess();
// child.command('verse', args);

// 2. Response caching (not implemented)
// Cache frequent queries:
// app.get('/api/clible', cache('5 minutes'), requireAuth, (req, res) => {

// 3. CLI invocation overhead
// clible subprocess spawn: ~50-100ms
// JSON parsing: <5ms
// SQLite lookup: 1-10ms depending on query
// Total: 60-120ms per request (acceptable)
```

### Network Optimization

```typescript
// 1. Response compression
app.use(compression());  // Gzip JSON responses

// 2. Request batching (could combine multiple analytics calls)
// Currently: separate fetch for each scope
// Future: batch endpoint combining ref + chapter + book

// 3. Caching strategy
// Browser: no caching (Bible data doesn't change often, but we fetch fresh)
// Server: could add Redis for popular verses
```

---

## Error Handling Strategy

### Error Hierarchy

```typescript
// 1. Validation errors (user input)
if (!reference.match(/^[A-Za-z ]+ \d+:\d+$/)) {
  throw new Error('Invalid verse format');
}

// 2. Network errors
try {
  const response = await fetch('/api/...');
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Network request failed');
  }
} catch (err) {
  throw new Error(`API request failed: ${err.message}`);
}

// 3. Logic errors
if (!selectedTranslation) {
  throw new Error('No translation selected. Install one first.');
}

// 4. CLI errors (from child_process)
const { stdout, stderr } = await runClible(argv).catch(err => {
  if (err.code === 127) {
    throw new Error('clible CLI not found');
  }
  if (stderr && stderr.includes('not found')) {
    throw new Error('Verse not found. Check translation is installed.');
  }
  throw err;
});
```

### Error Display Pattern

```typescript
const [error, setError] = useState<string | null>(null);

const handleSearch = async (query: string) => {
  setError(null);  // Clear previous errors
  try {
    // Do async work
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setError(message);  // Display to user
  }
};

// In component:
{error && (
  <Alert variant="destructive">
    <AlertCircle className="h-4 w-4" />
    <AlertTitle>Error</AlertTitle>
    <AlertDescription>{error}</AlertDescription>
  </Alert>
)}
```

---

## Security Architecture

### Defense in Depth

```
Layer 1: Input Sanitization
├── Character blacklist: [;&|`$<>]
├── Regex tokenization: respect quoted args
└── Type validation: cmd in allowlist

Layer 2: Process Isolation
├── spawn() not exec() → no shell injection
├── Closed stdio → output captured safely
└── Exit code checking → error detection

Layer 3: Authentication
├── Session token required: requireAuth middleware
├── HttpOnly cookies: cannot be stolen by XSS
├── Secure flag: HTTPS only in production
└── 24h expiration: session tokens rotate

Layer 4: Authorization
├── Only authenticated users access /api/clible
├── Only session owner accesses their settings
└── No cross-user data leakage

Layer 5: Secrets Management
├── GEMINI_API_KEY: env var only, never in code
├── SESSION_SECRET: env var only
└── DB passwords: not needed (local SQLite)
```

### Threat Model

```
Threat                         Mitigation
────────────────────────────────────────────────────────
UI-based code injection         React escapes HTML by default
                                 Third-party libs (markdown) explicitly set dangerouslySetInnerHTML

Command injection               Commands validated against allowlist
                                 Arguments tokenized and escaped
                                 spawn() used, not exec()

Session hijacking              HttpOnly cookies (no JS access)
                                 Secure flag (HTTPS only)
                                 24h expiration

API key exposure               Environment variable (not in code)
                                 Used server-side only
                                 Not logged in debug output

CSRF attacks                   Session cookies autoinclude
                                (SameSite could be added)

XSS attacks                    React default escaping
                                CSP headers (not yet implemented)
                                Content-Security-Policy header

Database tampering             SQLite file permissions
                                (not world-writable)

Rate limiting                  Not yet implemented
                                Could add: express-rate-limit
```

### Recommended Hardening (TODO)

```typescript
// 1. Content Security Policy
app.use((req, res, next) => {
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'"
  );
  next();
});

// 2. Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
});
app.use('/api/', limiter);

// 3. Input validation schemas
const verseSchema = z.string().regex(/^[A-Za-z ]+ \d+:\d+$/);

// 4. SQL injection protection (already using prepared statements)
// 5. CORS configuration
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:3000'
}));
```

---

## Build & Runtime Configuration

### Vite Configuration

```typescript
export default defineConfig(({ mode }) => {
  const root = path.resolve(__dirname);
  return {
    root,
    plugins: [
      react(),      // JSX + Fast Refresh
      tailwindcss() // Tailwind integration
    ],
    build: {
      outDir: 'dist',
      emptyOutDir: true,
      target: 'esnext'  // Modern JavaScript
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),  // import '@/types'
      },
    },
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:3000',       // Proxy to Express
          changeOrigin: true,
          ws: true  // WebSocket support (unused currently)
        },
      },
      hmr: process.env.DISABLE_HMR !== 'true',  // Hot Module Reload
    },
  };
});
```

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "strict": true,
    "noEmit": true
  }
}
```

**Note:** `strict: true` enables:
- `noImplicitAny`
- `strictNullChecks`
- `strictFunctionTypes`
- etc.

Ensures type safety throughout.

### Environment Variables

```bash
# .env
GEMINI_API_KEY=AIza...              # Optional, AI disabled if missing
NODE_ENV=development                # development / production
SESSION_SECRET=your-secret-here     # Change in production
CLIBLE_DATA_DIR=/path/to/data       # Optional override

# Docker only:
VITE_API_URL=http://localhost:3000  # Frontend API endpoint
```

### Build Process

```bash
# Development
npm run dev:api        # Express on port 3000
npm run dev:web        # Vite on port 5173

# Production build
npm run build          # → dist/ directory
npm run start          # Express serves dist/ + API

# Production runtime
docker build -f Dockerfile -t clible-web .
docker run -e GEMINI_API_KEY=... clible-web
```

---

## Future Architectural Improvements

### Scalability

```
Current: Single container, local SQLite
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Future: Separated services

Frontend (Static hosting)
  ├─ CDN
  └─ S3

API Gateway / Load Balancer
  ├─ Express replicas (horizontal scale)
  ├─ Cache layer (Redis)
  └─ Rate limiter

CLI Service Cluster
  ├─ gRPC or HTTP wrapper
  └─ Managed database (PostgreSQL with FTS)

External Services
  └─ Gemini API (already external)
```

### Enhanced Type Safety

```typescript
// 1. Zod schemas for runtime validation
const BibleResponseSchema = z.object({
  reference: z.string(),
  verses: z.array(z.object({
    book_name: z.string(),
    chapter: z.number(),
    verse: z.number(),
    text: z.string()
  })),
  text: z.string(),
  translation_name: z.string()
});

// 2. Type guards
function isBibleResponse(data: unknown): data is BibleResponse {
  return BibleResponseSchema.safeParse(data).success;
}

// 3. Branded types to prevent mix-ups
type TranslationId = string & { readonly __brand: 'TranslationId' };
type BookName = string & { readonly __brand: 'BookName' };

function createTranslationId(id: string): TranslationId {
  return id as TranslationId;
}
```

### Testing Strategy

```typescript
// Unit tests (jest)
describe('bibleService', () => {
  it('constructs chapter analytics args correctly', () => {
    const args = bibleService.buildAnalyticsArgs('chapter', 'John 3');
    expect(args).toBe('chapter "John" 3 --translation web');
  });
});

// Integration tests
describe('API bridge', () => {
  it('returns verse on valid request', async () => {
    const response = await request(app)
      .get('/api/clible?cmd=verse&args="John+3:16"')
      .set('Cookie', sessionCookie)
      .expect(200);
    expect(response.body.reference).toBe('John 3:16');
  });
});

// E2E tests (Cypress/Playwrig)
describe('User flow', () => {
  it('searches and exports verse', () => {
    cy.visit('http://localhost:5173');
    cy.get('[data-test=search-input]').type('John 3:16');
    cy.get('[data-test=search-button]').click();
    cy.get('[data-test=verse-text]').should('be.visible');
    cy.get('[data-test=export-button]').click();
  });
});
```

---

## References

- [Express.js Docs](https://expressjs.com)
- [React 19 Docs](https://react.dev)
- [Vite Docs](https://vitejs.dev)
- [TypeScript Handbook](https://typescriptlang.org/docs/)
- [SQLite FTS5](https://www.sqlite.org/fts5.html)
- [better-sqlite3](https://github.com/WiseLibs/better-sqlite3)
- [Google Generative AI](https://ai.google.dev/tutorials)

---

**See also:** [README.md](README.md) for user guide, [WEB_INTEGRATION.md](WEB_INTEGRATION.md) for data flow explainers.
