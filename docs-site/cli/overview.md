# CLI overview

The `clible` command is the engine that powers both the standalone CLI and the web app. The web server runs the CLI as a child process and returns the JSON output to the browser.

## Commands at a glance

| Command | Purpose |
|--------|---------|
| `seed` | Install, list, and remove translations |
| `verse` | Look up a single verse or a verse range |
| `search` | Full-text search with scope filters |
| `analytics` | Token statistics, n-grams, concordance, translation comparison |
| `backup` | Backup/restore the SQLite verse database (optional) |

Most commands support:

- `--json` to emit a single JSON document on stdout (used by the web bridge)
- `--export "KEY=VALUE,..."` to save output to a file (see [`--export`](/cli/export))

