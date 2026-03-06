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
uv run clible seed install fin-biblia  # Finnish Bible (OSIS)

# Look up verses
uv run clible verse "John 3:16"
uv run clible verse "Genesis 1:1"
```

## Commands

### Translations (`clible seed`)

| Command | Description |
| ------- | ----------- |
| `clible seed available` | List translations in the catalog |
| `clible seed install <id>` | Download, parse, and install a translation |
| `clible seed list` | List installed translations |
| `clible seed remove <id>` | Uninstall a translation and its verses |

Supported formats: **USFX** (web), **OSIS** (kjv, fin-biblia).

### Verse lookup (`clible verse`)

```bash
clible verse "John 3:16"
clible verse "1 Corinthians 13:4" -t web
```

- **Reference format:** `"Book Chapter:Verse"` (e.g. `"Genesis 1:1"`, `"1 Corinthians 13:4"`)
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

- **`-t`, `--translation`:** Translation ID. Defaults to the first installed.
- **`--top` / `-n`:** Number of top items to show (default 10).

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
