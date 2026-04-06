# clible

A command-line Bible study tool. Offline-first: seed local XML data from [seven1m/open-bibles](https://github.com/seven1m/open-bibles), then query verses without network calls.

## Installation

```bash
git clone <repo-url>
cd clible-v2
uv sync
```

## Quick Start

```bash
# One-time: install translations (XML download + local import)
uv run clible seed install web      # World English Bible (USFX)
uv run clible seed install kjv      # King James Version (OSIS)
uv run clible seed install fin-biblia-33-38  # Finnish 1933/1938 (OSIS)
uv run clible seed install fin-1992  # Finnish 1992 (BEBLIA)
uv run clible seed install fin-1776  # Finnish 1776 (BEBLIA)

# Look up verses
uv run clible verse "John 3:16"
uv run clible verse "Genesis 1:1"
uv run clible verse "John 3:16-18" -t kjv
```

## Commands

### Translations (`clible seed`)

| Command | Description |
| ------- | ----------- |
| `clible seed available` | List translations in the catalog |
| `clible seed install <id>` | Download, parse, and install a translation |
| `clible seed list` | List installed translations |
| `clible seed remove <id>` | Uninstall a translation and its verses |

Supported formats:

- **USFX** (`web`)
- **OSIS** (`kjv`, `fin-biblia-33-38`)
- **BEBLIA** (`fin-1992`, `fin-1776`, `fin-stlk`)

### Verse lookup (`clible verse`)

```bash
clible verse "John 3:16"
clible verse "John 3:16-18"
clible verse "1 Corinthians 13:4" -t web
```

- **Reference format:** `"Book Chapter:Verse"` or same-chapter range `"Book Chapter:Verse-Verse"`  
  (e.g. `"Genesis 1:1"`, `"John 3:16-18"`, `"1 Corinthians 13:4"`).
- **Constraint:** verse ranges must stay inside one chapter (`John 3:16-18` supported, `John 3:16-4:2` not supported).
- **`-t`, `--translation`:** Translation ID. Defaults to the first installed (usually `web`)

### Text analytics (`clible analytics`)

Analyze token frequencies, lexical diversity, and n-grams for any scope.
Stopwords (articles, prepositions, pronouns) are filtered by default.

```bash
# Analyze specific verses
clible analytics reference "John 3:16"
clible analytics reference "John 3:16-18" --top 5

# Analyze an entire chapter
clible analytics chapter John 3
clible analytics chapter Genesis 1 -t kjv

# Analyze an entire book
clible analytics book John --top 20
clible analytics book Genesis -t kjv

# Compare Finnish translations side-by-side with diffs
clible analytics compare "John 3:16-18"
clible analytics compare "Psalm 23:1-4" --left fin-1992 --right fin17xx
```

**Output per scope:** metrics table (total tokens, unique tokens, type-token ratio) + top-N words, bigrams, and trigrams.
`analytics compare` prints a side-by-side verse table with word-level diffs and a similarity summary (exact match rate, average similarity, shared vocabulary).
Default compare pair is `fin-1992` vs `fin17xx` (alias that resolves to installed `fin-1776`, or another installed `fin-17*` translation).

- **`-t`, `--translation`:** Translation ID. Defaults to the first installed.
- **`--top` / `-n`:** Number of top items to show (default 10).

## Operational runbook

```bash
# 1) See what can be installed
uv run clible seed available

# 2) Install one or more translations
uv run clible seed install web
uv run clible seed install kjv

# 3) Verify local installation state
uv run clible seed list

# 4) Query locally (no runtime API calls after seeding)
uv run clible verse "John 3:16" -t web
uv run clible analytics chapter John 3 -t web
```

`seed install` workflow:
1. Download XML from catalog URL.
2. Parse XML using the format-specific parser (USFX / OSIS / BEBLIA).
3. Insert translation metadata and verse rows into SQLite.
4. Keep verse full-text search (FTS5) index in sync via DB triggers.

## Configuration

Override via environment variables:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `CLIBLE_DB_PATH` | `{data_dir}/clible.db` | SQLite database path |
| `CLIBLE_DATA_DIR` | `src/clible/data` | Data and config directory |
| `CLIBLE_API_BASE_URL` | `https://api.bible-api.com` | API base URL in config (reserved for API-oriented workflows) |
| `CLIBLE_TRANSLATIONS` | `KJV,ESV,NIV` | Comma-separated translation codes in config |
| `CLIBLE_REQUEST_TIMEOUT` | `10` | HTTP timeout used by network requests |
| `CLIBLE_REQUEST_DELAY` | `1` | Delay setting for API-oriented workflows |

## Architecture

- **CLI** (Click + Rich) → **Services** → **Repositories** → **SQLite**
- Services: `SeedService`, `VerseService`, `AnalyticService`
- Repositories: `TranslationRepo`, `BookRepo`, `VerseRepo`
- Parsers: **USFX**, **OSIS**, **BEBLIA** (XML → normalized verse rows)
- No external API during verse lookup/analytics at runtime; verse data is local after seeding

## Development

```bash
uv sync --all-groups
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

## Task Automation

This repo uses [Task](https://taskfile.dev/) to automate common development and Docker workflows.

```bash
task lint
task format-check
task test
task check
```

### Docker build and publish

```bash
# Optional but recommended for direnv users:
cp .env.example .env
direnv allow

# Build Docker image with tags:
# - docker.io/mvirtai/clible-v2:latest
# - docker.io/mvirtai/clible-v2:<git-commit>
task d-build

# Show local tags for the built image
task d-show-tags

# Push both tags (run docker login first)
task d-push
```

`task d-push` always shows image tags before pushing.
The target repository can be overridden with `CLIBLE_DOCKER_REPO`.

## Troubleshooting

- **`Verse(s) not found.`**
  - Ensure at least one translation is installed (`clible seed list`).
  - Confirm reference format is valid (`Book Chapter:Verse` or `Book Chapter:Verse-Verse`).
  - Confirm the requested translation exists (`-t <translation_id>`).

- **`Comparison failed. Missing translation(s): ...`**
  - Install required pair first:
    - `uv run clible seed install fin-1992`
    - `uv run clible seed install fin-1776`

- **`Unknown translation: <id>` during install**
  - Check valid IDs with `uv run clible seed available`.

- **`Translation '<id>' is already installed`**
  - Skip reinstall, or remove first with `uv run clible seed remove <id>`.

## Documentation

- **[docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)** — Architecture, schema, implementation status
