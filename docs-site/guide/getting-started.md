# Getting started

This page walks through installing clible, seeding your first translation, and running the most common commands. The same engine drives both the CLI and the web app.

## Requirements

| Tool | Version | Why |
|------|---------|-----|
| Python | 3.12+ | CLI runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Python dependency management |
| Node.js | 20+ | Web app + docs site |
| Docker | latest | Optional (container deploy) |

## Install

```bash
git clone https://github.com/mvirtai/clible-v2.git
cd clible-v2
uv sync --all-groups
```

## Seed a translation (one-time)

clible does not ship Bible text. Install at least one translation from the catalog:

```bash
uv run clible seed available
uv run clible seed install web
```

## First commands

```bash
uv run clible verse "John 3:16"
uv run clible search "grace" --scope book --reference Romans
uv run clible analytics chapter John 3
```

## Run the web app locally

```bash
cd src/clible-web
npm install
cp ../../.env.example .env
npm run dev
```

You need a Postgres connection string for sessions and user settings. See `docs/CLOUD_SQL_SETUP.md` for Neon / Cloud SQL setup.

## Run the docs site locally

```bash
cd docs-site
npm install
npm run dev
```

