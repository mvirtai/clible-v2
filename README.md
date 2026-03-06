# clible

A command-line Bible study tool. Offline-first workflow: seed local XML data from
[seven1m/open-bibles](https://github.com/seven1m/open-bibles) and
[Beblia/Holy-Bible-XML-Format](https://github.com/Beblia/Holy-Bible-XML-Format),
then query and analyze verses without runtime API calls.

## Installation

```bash
git clone <repo-url>
cd clible-v2
uv sync
```

## Quick Start

```bash
# 1) Install translations (one-time per DB)
uv run clible seed install web              # World English Bible (USFX)
uv run clible seed install kjv              # King James Version (OSIS)
uv run clible seed install fin-biblia-33-38 # Finnish 1933/1938 (OSIS)

# Optional for Finnish translation comparison:
uv run clible seed install fin-1992         # BEBLIA
uv run clible seed install fin-1776         # BEBLIA

# 2) Lookup verses (single and range)
uv run clible verse "John 3:16"
uv run clible verse "John 3:16-18" -t kjv

# 3) Run analytics
uv run clible analytics reference "John 3:16-18"
uv run clible analytics compare "John 3:16-18"
```

## Commands

### Translations (`clible seed`)

| Command | Description |
| ------- | ----------- |
| `clible seed available` | List translations from the static catalog |
| `clible seed install <id>` | Download, parse, and install a translation |
| `clible seed list` | List installed translations |
| `clible seed remove <id>` | Remove translation (verses deleted via CASCADE) |

Supported XML formats:

- **USFX** (e.g. `web`)
- **OSIS** (e.g. `kjv`, `fin-biblia-33-38`)
- **BEBLIA** (e.g. `fin-1992`, `fin-1776`, `fin-stlk`)

### Verse lookup (`clible verse`)

```bash
clible verse "John 3:16"
clible verse "John 3:1-6" -t kjv
clible verse "1 Corinthians 13:4"
```

- **Reference format:** `"Book Chapter:Verse"` or `"Book Chapter:Start-End"`
- **Range constraint:** ranges are within a single chapter (example: `John 3:1-6`)
- **`-t`, `--translation`:** Translation ID. Defaults to `web` if installed, otherwise first installed translation.

### Text analytics (`clible analytics`)

Analyze token frequencies, lexical diversity, and n-grams for verse/chapter/book scopes.
Stopwords are filtered by default using language-specific lists from `stopwords.json`.

```bash
# Analyze specific verses
clible analytics reference "John 3:16"
clible analytics reference "John 3:16-18" --top 5

# Analyze an entire chapter or book
clible analytics chapter John 3
clible analytics book Genesis -t kjv --top 20

# Compare translations side-by-side with diffs and similarity metrics
clible analytics compare "John 3:16-18"
clible analytics compare "Psalm 23:1-4" --left fin-1992 --right fin17xx
```

`analytics compare` defaults to `--left fin-1992 --right fin17xx`.
`fin17xx` is an alias that resolves to `fin-1776` (or another installed `fin-17*` ID).

## Configuration

Override via environment variables:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `CLIBLE_DB_PATH` | `{data_dir}/clible.db` | SQLite database path |
| `CLIBLE_DATA_DIR` | `src/clible/data` | Data and config directory |

## Architecture

- **CLI** (Click + Rich) → **Services** → **Repositories** → **SQLite**
- Repositories: `TranslationRepo`, `BookRepo`, `VerseRepo`
- Services: `SeedService`, `VerseService`, `AnalyticService`
- Parsers: `USFXParser`, `OSISParser`, `BebliaParser`
- No runtime API calls after seeding completes

## Developer Runbook

### Local quality checks

```bash
uv sync --all-groups
task check
```

`task check` runs Ruff lint, Ruff format check, and pytest.

### Docker build and publish

```bash
# Optional: create local environment file
cp .env.example .env
direnv allow

# Build runtime image with commit + latest tags
task d-build

# Show image tags
task d-show-tags

# Push both tags (requires docker login)
task d-push
```

Set `CLIBLE_DOCKER_REPO` to override the default image repository.

## Troubleshooting and Common Pitfalls

- **`Verse(s) not found`**
  - Ensure at least one translation is installed: `clible seed list`
  - Verify reference format (`Book Chapter:Verse` or same-chapter range)
  - Confirm translation exists if using `-t`

- **`analytics compare` fails with missing translation(s)**
  - Install the required pair:
    - `clible seed install fin-1992`
    - `clible seed install fin-1776`
  - If `fin17xx` alias cannot resolve, use `--right fin-1776` explicitly.

- **Seed install fails**
  - Check network access (downloads happen during install)
  - Re-run `clible seed available` to verify catalog IDs
  - If a translation is already installed, remove first: `clible seed remove <id>`

## Documentation

- **[docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)** — Architecture, schema, implementation status, workflows
