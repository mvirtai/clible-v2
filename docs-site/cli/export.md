# `--export` flag

Any `verse`, `search`, or `analytics` command accepts the `--export` flag, which writes the rendered output to a file in one of several formats.

## Syntax

```bash
clible <command> --export "KEY=VALUE,KEY=VALUE,…"
```

## Keys

| Key        | Default          | Purpose                                       |
|------------|------------------|-----------------------------------------------|
| `PATH`     | current dir      | Directory to write the file to                |
| `FILENAME` | auto             | Base filename without extension               |
| `FORMAT`   | `md`             | One of `md`, `html`, `json`, `csv`, `txt`, `xml` |

Keys are case-insensitive and order does not matter.

## Examples

```bash
# Save a verse range as Markdown
clible verse "Psalm 23:1-6" --export "PATH=~/notes,FILENAME=ps23,FORMAT=md"

# Search results as JSON
clible search grace --scope book --reference John --export "FORMAT=json"

# Analytics report as HTML
clible analytics reference "John 3:16" --export "FORMAT=html"

# CSV for spreadsheets
clible search peace --scope testament --reference NT --export "FORMAT=csv"
```

## Format support by command

| Format | verse | search | analytics |
|--------|-------|--------|-----------|
| `md`   | yes   | yes    | yes       |
| `html` | yes   | yes    | yes       |
| `json` | yes   | yes    | yes       |
| `csv`  | yes   | yes    | yes       |
| `txt`  | yes   | yes    | yes       |
| `xml`  | yes   | yes    | yes       |

The serialiser logic lives in [`src/clible/ui/`](https://github.com/vivaldev/clible-v2/tree/main/src/clible/ui) and stays UI-only — it never touches the database.
