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
uv run clible seed available
uv run clible seed install web      # World English Bible (USFX)
uv run clible seed install kjv      # King James Version (OSIS)
uv run clible seed install fin-biblia-33-38  # Finnish Bible 1933/1938 (OSIS)

# Look up verses
uv run clible verse "John 3:16"
uv run clible verse "John 3:16-18"
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

Supported formats: **USFX** (web), **OSIS** (kjv, fin-biblia-33-38), **BEBLIA** (fin-1992, fin-1776, fin-stlk).

### Verse lookup (`clible verse`)

```bash
clible verse "John 3:16"
clible verse "John 3:16-18"
clible verse "1 Corinthians 13:4" -t web
```

- **Reference format:** `"Book Chapter:Verse"` or `"Book Chapter:Start-End"` (e.g. `"Genesis 1:1"`, `"John 3:16-18"`)
- **Range constraint:** ranges must stay inside one chapter (`"John 3:16-4:2"` is not supported)
- **`-t`, `--translation`:** Translation ID. Defaults to `web` if installed, otherwise first installed translation

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

- **`-t`, `--translation`:** Translation ID. Defaults to `web` if installed, otherwise first installed translation.
- **`--top` / `-n`:** Number of top items to show (default 10).

#### Comparison workflow runbook (`analytics compare`)

1. Install both comparison translations:
   ```bash
   clible seed install fin-1992
   clible seed install fin-1776
   ```
2. Run compare:
   ```bash
   clible analytics compare "John 3:16-18"
   ```
3. Optional: override either side with explicit IDs:
   ```bash
   clible analytics compare "Psalm 23:1-4" --left fin-1992 --right fin-1776
   ```

Notes:
- `fin17xx` and `fin-17xx` are aliases for an installed `fin-1776` (or first installed `fin-17*` translation).
- Left and right translations must be different IDs.

## Configuration

Override via environment variables:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `CLIBLE_DB_PATH` | `{data_dir}/clible.db` | SQLite database path |
| `CLIBLE_DATA_DIR` | `src/clible/data` | Data and config directory |

## Architecture

- **CLI** (Click + Rich) → **Services** → **Repositories** → **SQLite**
- Repositories: TranslationRepo, BookRepo, VerseRepo
- Parsers: USFX, OSIS, BEBLIA (XML → verses)
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

### PR workflow automation

```bash
# Preview generated PR title/body without creating a PR
task pr-compare ARGS="--preview-only"

# Create PR interactively (asks for confirmation)
task pr-compare

# Create PR without prompt
task pr-compare ARGS="--yes --base main --title 'feat: ...'"
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

| Problem | Likely cause | Fix |
| ------- | ------------ | --- |
| `Verse(s) not found` | No translations installed, unsupported reference format, or verse not in selected translation | Run `clible seed list`, install a translation (`clible seed install web`), then retry with `Book Chapter:Verse` or `Book Chapter:Start-End` |
| `Comparison failed. Missing translation(s)` | `analytics compare` translations are not installed | Install both translations (`clible seed install fin-1992` and `clible seed install fin-1776`) |
| `Comparison failed. Left and right translations are the same.` | `--left` and `--right` resolve to the same translation ID | Use two distinct IDs |
| Comparison shows `No verses found for this reference...` | Reference exists in one translation but not in the other, or neither has that passage | Try another reference or verify installed translations with `clible seed list` |

## Documentation

- **[docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)** — Architecture, schema, implementation status
