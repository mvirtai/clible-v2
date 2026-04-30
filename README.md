# clible

A Bible study web application with full-text search, text analytics, and AI-powered insights. Built as an offline-first tool: Bible translations are seeded from open XML sources into a local SQLite database, so all verse lookups and searches run without any API calls at query time.

The project has two interfaces: a **web app** (the primary user interface) and a **CLI tool** (the engine behind the web app, also usable directly).

---

## Features

### Web app

- **Verse lookup** — search by reference (`John 3:16`, `Genesis 1:1-3`, `1 Corinthians 13:4`)
- **Full-text search** — FTS5-powered search across the whole Bible or scoped to a book, chapter, testament, or verse range; includes occurrence statistics and top-book breakdown
- **Text analytics** — word frequency, lexical diversity, bigrams, trigrams, and concordance for any reference, chapter, or whole book; compare two translations side-by-side with word-level diffs
- **AI insights** — Gemini-powered study notes and tone analysis for any passage (rate-limited; requires API key)
- **Translation management** — install translations from the catalog through the UI
- **User accounts** — registration, login, and per-user settings (preferred translation, theme)
- **Export** — download search results or analytics as Markdown, HTML, JSON, CSV, or XML

### CLI tool

The same engine is available as a standalone CLI for power users and scripting:

```bash
clible verse "John 3:16"
clible search "grace" --scope book --reference Romans
clible analytics chapter John 3
clible analytics compare "Psalm 23" --left web --right kjv
```

---

## Translations

Translations are installed from public-domain XML repositories ([seven1m/open-bibles](https://github.com/seven1m/open-bibles), [Beblia/Holy-Bible-XML-Format](https://github.com/Beblia/Holy-Bible-XML-Format)). Run `clible seed available` to see the full catalog.

Included examples:

| ID | Translation | Language | Format |
|----|-------------|----------|--------|
| `web` | World English Bible | English | USFX |
| `kjv` | King James Version | English | OSIS |
| `fin-1992` | Finnish Bible 1992 | Finnish | BEBLIA |
| `fin-biblia-33-38` | Finnish Bible 1933/38 | Finnish | OSIS |
| `greek` | Greek New Testament | Ancient Greek | BEBLIA |

All 18 Greek variants in the catalog (Textus Receptus, Byzantine, SBL GNT, etc.) are supported.

---

## Architecture

```
Web UI (React/Vite)
      │ HTTP
Express server (Node.js/TypeScript)   ← session auth, AI proxy, rate limiting
      │ child_process.spawn
Clible CLI (Python)                   ← verse engine, FTS5 search, analytics
      │ sqlite3
SQLite (clible.db)                    ← seeded from XML; read-only at runtime
      │
PostgreSQL (Neon)                     ← user accounts, sessions, settings
```

The Express server is a thin bridge: it sanitises request parameters, spawns `clible` commands with `--json`, and forwards the structured output to the browser. All Bible logic lives in the Python CLI layer; the web layer adds auth, AI, and user state on top.

**Key design choices:**
- **Offline-first** — Bible text is seeded once, then all lookups are local (no API dependency at runtime)
- **Layered architecture** — UI → Services → Repositories → SQLite; each layer is independently testable
- **Dependency injection** — no global state or singletons; tests inject in-memory SQLite connections
- **FTS5** — SQLite full-text search with triggers keeping the index in sync; no external search engine needed

See [docs/architecture/overview.md](docs/architecture/overview.md) and [docs/architecture/adr/](docs/architecture/adr/) for the detailed design and rationale.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Web frontend | React 18, TypeScript, Vite |
| Web backend | Node.js, Express, TypeScript |
| CLI | Python 3.12+, Click, Rich |
| Verse data | SQLite + FTS5 |
| User data | PostgreSQL (Neon) |
| AI | Google Gemini (`@google/genai`) |
| Session storage | `connect-pg-simple` |
| Container | Docker (single image: CLI + web) |
| CI/CD | GitHub Actions (lint, test, build, push to Artifact Registry) |
| Package management | uv (Python), npm (Node) |

---

## CLI reference

### Translations

```bash
clible seed available           # browse the catalog
clible seed install web         # download and seed a translation (~4 MB)
clible seed list                # show installed translations
clible seed remove web          # uninstall
```

### Verse lookup

```bash
clible verse "John 3:16"
clible verse "John 3:16-18"     # verse range
clible verse "Genesis 1:1" -t kjv
```

Reference format: `"Book Chapter:Verse"` or `"Book Chapter:Start-End"`.

### Search

```bash
clible search grace
clible search love --scope book --reference John
clible search peace --scope testament --reference NT
clible search faith --scope chapter --reference "Hebrews 11"
clible search hope --limit 20
```

Scope options: `bible` (default), `book`, `testament`, `chapter`, `verse`.

### Analytics

```bash
clible analytics reference "John 3:16"
clible analytics chapter John 3 --top 15
clible analytics book Romans
clible analytics compare "John 3:16-18" --left web --right kjv
```

### Export

Any `verse`, `search`, or `analytics` command accepts `--export`:

```bash
clible verse "Psalm 23:1-6" --export "PATH=~/notes,FILENAME=ps23,FORMAT=md"
clible search grace --scope book --reference John --export "FORMAT=json"
clible analytics reference "John 3:16" --export "FORMAT=html"
```

Formats: `md`, `html`, `json`, `csv`, `txt`, `xml`.

### Multilanguage

Interface and labels are always English. Bible text language is controlled by `-t / --translation`. For analytics stopword filtering, set `CLIBLE_ANALYTICS_LANGUAGE` (supports `en`, `fi`, `grc`, `el`):

```bash
CLIBLE_ANALYTICS_LANGUAGE=grc clible analytics reference "John 3:16" -t greek
```

---

## Development

```bash
git clone <repo-url>
cd clible-v2
uv sync --all-groups        # install Python deps
uv run pytest -v            # run tests (>91% coverage)
uv run ruff check .         # lint
uv run ruff format --check .
```

Run the web app locally:

```bash
cd src/clible-web
npm install
npm run dev    # Vite dev server + Express, with /api/* proxy
```

See [docs/guides/development.md](docs/guides/development.md) for the full development workflow.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CLIBLE_DB_PATH` | `{data_dir}/clible.db` | SQLite database path |
| `CLIBLE_DATA_DIR` | `src/clible/data` | Data directory |
| `CLIBLE_ANALYTICS_LANGUAGE` | `en` | Stopword language for analytics |

Web-specific (required for the web app):

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key (AI features; optional) |
| `SESSION_SECRET` | 64-char hex string for session signing |
| `DATABASE_URL` | PostgreSQL connection string |

---

## Documentation

- [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) — implementation status and file map
- [ROADMAP.md](ROADMAP.md) — current status and feature direction
- [docs/architecture/overview.md](docs/architecture/overview.md) — layered architecture and design patterns
- [docs/architecture/adr/](docs/architecture/adr/) — Architecture Decision Records
- [docs/api/openapi.yml](docs/api/openapi.yml) — OpenAPI 3.1 spec for the web API
- [docs/guides/development.md](docs/guides/development.md) — local setup and workflow
- [NOTICE.md](NOTICE.md) — data sources and licensed translation notices

---

## Troubleshooting

**`Error: Unknown translation: <id>`** — run `clible seed available` for the valid ID list.

**`Error: Translation '<id>' is already installed`** — remove it first with `clible seed remove <id>` if you want to reinstall.

**`Verse(s) not found`** — check the reference format (`Book Chapter:Verse`), confirm a translation is installed (`clible seed list`), and pass `-t <id>` to specify which one.

**Analytics results are sparse** — analyze a larger scope (`analytics chapter` or `analytics book`), or set `CLIBLE_ANALYTICS_LANGUAGE` to match the Bible text language.
