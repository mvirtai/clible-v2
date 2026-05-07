# `clible analytics`

Text-analytics commands: word frequency, lexical diversity, n-grams, concordance, and side-by-side translation comparison.

## Subcommands

```bash
clible analytics reference "<reference>"
clible analytics chapter <book> <chapter>
clible analytics book <book>
clible analytics compare "<reference>" --left <id> --right <id>
```

## Examples

```bash
clible analytics reference "John 3:16"
clible analytics chapter John 3 --top 15
clible analytics book Romans
clible analytics compare "John 3:16-18" --left web --right kjv
```

## What you get

For each scope, the command computes:

- **Token metrics** — total tokens, unique tokens, lexical diversity
- **Top words** — most frequent words after stopword filtering
- **Bigrams and trigrams** — most frequent 2-word and 3-word phrases
- **Concordance** — every occurrence of a chosen word with surrounding context

The `compare` subcommand additionally produces a word-level diff between two translations of the same passage.

## Stopwords and language

Stopwords are loaded from [`src/clible/data/stopwords.json`](https://github.com/vivaldev/clible-v2/blob/main/src/clible/data/stopwords.json). The language is picked from the translation's `language` field by default. Override explicitly:

```bash
CLIBLE_ANALYTICS_LANGUAGE=grc clible analytics reference "John 3:16" -t greek
```

Supported codes: `en`, `fi`, `grc`, `el`.

## JSON output

With `--json`, the result is one object containing all metrics and the top words/n-grams as arrays. The web UI consumes this same payload — see the [API reference](/api/reference#tag/bible).
