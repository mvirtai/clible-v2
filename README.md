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
|---------|-------------|
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

## Configuration

Override via environment variables:

| Variable | Default | Description |
|----------|---------|--------------|
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

## Documentation

- **[docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)** — Architecture, schema, implementation status
