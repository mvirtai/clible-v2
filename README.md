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
uv run clible seed install fin-1776          # Finnish Bible 1776 (BEBLIA)

# Look up verses
uv run clible verse "John 3:16"
uv run clible verse "Genesis 1:1"
uv run clible verse "John 3:1-6" -t kjv

# Compare two translations side-by-side
uv run clible analytics compare "John 3:16-18"
```

## Commands

### Translations (`clible seed`)

| Command | Description |
| ------- | ----------- |
| `clible seed available` | List translations in the catalog |
| `clible seed install <id>` | Download, parse, and install a translation |
| `clible seed list` | List installed translations |
| `clible seed remove <id>` | Uninstall a translation and its verses |

Supported formats: **USFX** (`web`), **OSIS** (`kjv`, `fin-biblia-33-38`), **BEBLIA** (`fin-1992`, `fin-1776`, `fin-stlk`).

### Verse lookup (`clible verse`)

```bash
clible verse "John 3:16"
clible verse "1 Corinthians 13:4" -t web
```

- **Reference format:** `"Book Chapter:Verse"` (e.g. `"Genesis 1:1"`, `"1 Corinthians 13:4"`)
- **`-t`, `--translation`:** Translation ID. Defaults to the first installed (usually `web`)

### Text analytics (`clible analytics`)

Analyze token frequencies, lexical diversity, and n-grams for any scope.
Stopwords (articles, prepositions, pronouns) are filtered by default, and the stopword language is resolved from the selected translation metadata.

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

- **`-t`, `--translation`:** Translation ID. Defaults to the first installed.
- **`--top` / `-n`:** Number of top items to show (default 10).
- **`analytics compare --left/--right`:** Defaults are `fin-1992` (left) and `fin17xx` (right alias for `fin-1776`).

### Runbook: Finnish translation comparison

```bash
# 1) Install required translations
uv run clible seed install fin-1992
uv run clible seed install fin-1776

# 2) Verify they are installed
uv run clible seed list

# 3) Compare a reference
uv run clible analytics compare "John 3:16-18"
uv run clible analytics compare "Psalm 23:1-4" --left fin-1992 --right fin17xx
```

## Troubleshooting

- **`Error: Unknown translation: <id>`**
  - Run `uv run clible seed available` and use one of the listed IDs.
- **`Error: Translation '<id>' is already installed`**
  - The translation already exists in local DB. Use `uv run clible seed list` to inspect or `uv run clible seed remove <id>` before reinstalling.
- **`Comparison failed. Missing translation(s): ...`**
  - `analytics compare` requires both selected translations installed. Install them first, usually:
    - `uv run clible seed install fin-1992`
    - `uv run clible seed install fin-1776`
- **`Verse(s) not found.`**
  - Check the reference format (`"Book Chapter:Verse"` or range `"Book Chapter:Start-End"`), and confirm data exists for the selected translation.

## Configuration

Override via environment variables:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `CLIBLE_DB_PATH` | `{data_dir}/clible.db` | SQLite database path |
| `CLIBLE_DATA_DIR` | `src/clible/data` | Data and config directory |

## Architecture

- **CLI** (Click + Rich) → **Services** → **Repositories** → **SQLite**
- Repositories: TranslationRepo, BookRepo, VerseRepo
- Parsers: USFX, OSIS (XML → verses)
- No external API at runtime; all data local after seeding

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

## Documentation

- **[docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)** — Architecture, schema, implementation status
