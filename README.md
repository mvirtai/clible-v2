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
# One-time: install a translation (~4 MB download each)
uv run clible seed install web      # World English Bible (USFX)
uv run clible seed install kjv      # King James Version (OSIS)
uv run clible seed install fin-biblia-33-38  # Finnish Bible 1933/1938 (OSIS)
uv run clible seed install fin-1992          # Finnish Bible 1992 (BEBLIA)

# Look up verses
uv run clible verse "John 3:16"
uv run clible verse "Genesis 1:1"
uv run clible verse "John 3:16-18"
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

- **USFX**: `web`
- **OSIS**: `kjv`, `fin-biblia-33-38`
- **BEBLIA**: `fin-1992`, `fin-1776`, `fin-stlk`
- **ZEFANIA**: `test-zefania`

### Verse lookup (`clible verse`)

```bash
clible verse "John 3:16"
clible verse "John 3:16-18"
clible verse "1 Corinthians 13:4" -t web
```

- **Reference format:** `"Book Chapter:Verse"` or range `"Book Chapter:Start-End"` (e.g. `"Genesis 1:1"`, `"John 3:16-18"`)
- **`-t`, `--translation`:** Translation ID. Defaults to `web` if installed, otherwise first installed

### Search (`clible search`)

Full-text search with scope control and statistics:

```bash
# Search entire Bible (default)
clible search grace

# Search within a book
clible search love --scope book --reference John

# Search within Old or New Testament
clible search peace --scope testament --reference NT

# Search within a chapter
clible search faith --scope chapter --reference "Hebrews 11"

# Search specific verse range
clible search hope --scope verse --reference "Romans 8:24-25"

# Limit results
clible search joy --limit 10
```

Shows statistics (total occurrences, unique verses, top books) before displaying verses. For large result sets (>20 verses), prompts with options: `all` (all verses), `N` (first N verses), or `no` (statistics only).

- **`-s`, `--scope`:** Search scope: `verse`, `chapter`, `book`, `testament`, or `bible` (default)
- **`-r`, `--reference`:** Scope reference (e.g. "John", "NT", "John 3:16")
- **`-t`, `--translation`:** Translation ID
- **`-n`, `--limit`:** Maximum verses to display

### Text analytics (`clible analytics`)

Analyze token frequencies, lexical diversity, and n-grams for any scope.
Stopwords (articles, prepositions, pronouns) are filtered by default.
Stopword language is resolved from the selected translation's `language` in `src/clible/data/translations.json` (fallback: `en`).

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

# Compare two translations side-by-side with diffs
clible analytics compare "John 3:16-18"
clible analytics compare "Psalm 23:1-4" --left fin-1992 --right fin17xx
```

**Output per scope:** metrics table (total tokens, unique tokens, type-token ratio) + top-N words, bigrams, and trigrams.

`analytics compare` prints a side-by-side verse table with word-level diffs and a similarity summary (exact match rate, average similarity, shared vocabulary).

- **`-t`, `--translation`:** Translation ID. Defaults to `web` if installed, otherwise first installed.
- **`--top` / `-n`:** Number of top items to show (default 10).

## Configuration

Override via environment variables:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `CLIBLE_DB_PATH` | `{data_dir}/clible.db` | SQLite database path |
| `CLIBLE_DATA_DIR` | `src/clible/data` | Data and config directory |

### Google Cloud (optional)

For GCS backup, seed-from-GCS, and Docker push to Artifact Registry, see **[docs/GCP_SETUP.md](docs/GCP_SETUP.md)**.

| Variable | Description |
| -------- | ----------- |
| `CLIBLE_GCS_BUCKET` | GCS bucket for `clible backup gcs` |
| `CLIBLE_GCS_BACKUP_PREFIX` | Object prefix for backups (default: `backups`) |
| `CLIBLE_SEED_BASE_URL` | Base URL for seed XML (e.g. public GCS prefix) |
| `CLIBLE_GCP_ARTIFACT_REGISTRY` | Artifact Registry prefix for `task d-push-gcp` |

### Backup and restore (`clible backup`)

```bash
# Upload the local SQLite database to GCS
clible backup gcs

# Restore the local database from a GCS object
clible backup restore-gcs "gs://my-bucket/backups/clible-20260306-180000.db"
```

`restore-gcs` asks for confirmation before replacing the local DB. Use `--force`
to skip the prompt in scripted environments.

## Architecture

- **CLI** (Click + Rich) → **Services** → **Repositories** → **SQLite**
- Repositories: TranslationRepo, BookRepo, VerseRepo
- Parsers: USFX, OSIS, BEBLIA (XML → verses)
- Full-text search: SQLite FTS5 index (`verses_fts`) for concordance/search codepaths
- No external API at runtime; all data local after seeding

## Development

```bash
uv sync --all-groups
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

## Operational runbook

### Translation lifecycle

```bash
# See what can be installed
clible seed available

# Install one translation
clible seed install web

# Verify installation
clible seed list

# Remove translation and its verses
clible seed remove web
```

### Local quality gates

```bash
# Standard checks
task check

# Run a focused test subset
task test-one PATTERN=verse_service
```

`task d-build` depends on `task check`, so Docker images are only built after lint, format-check, and tests pass.

## Troubleshooting

### `Error: Unknown translation: <id>`

- Cause: ID is not in `src/clible/data/translations.json`.
- Fix: run `clible seed available` and use an ID from that list.

### `Error: Translation '<id>' is already installed`

- Cause: duplicate install attempt.
- Fix: either keep the existing install or run `clible seed remove <id>` first.

### `Verse(s) not found`

- Cause: invalid reference format, missing verses in selected translation, or no installed translations.
- Fix:
  1. Use `Book Chapter:Verse` or `Book Chapter:Start-End` format (e.g. `John 3:16-18`).
  2. Confirm installed translations with `clible seed list`.
  3. Set translation explicitly with `-t <id>`.

### Analytics results are sparse or empty

- Cause: very short input and/or stopword filtering removes most tokens.
- Fix:
  1. Analyze a larger scope (`analytics chapter` or `analytics book`).
  2. Try another translation/language (`-t web` vs `-t fin-1992`).
  3. Increase output depth with `--top`.

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

To push to **Google Cloud Artifact Registry** instead of Docker Hub, set `CLIBLE_GCP_ARTIFACT_REGISTRY` (e.g. `europe-north1-docker.pkg.dev/myproject/clible`) and run `task d-push-gcp`. See [docs/GCP_SETUP.md](docs/GCP_SETUP.md).

## Documentation

- **[docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)** — Architecture, schema, implementation status
- **[docs/GCP_SETUP.md](docs/GCP_SETUP.md)** — Google Cloud (GCS backup, seed from GCS, Artifact Registry)
