---
layout: home

hero:
  name: clible
  text: Offline-first Bible study
  tagline: Full-text search, text analytics, and AI-powered insights — built on a layered architecture that runs without an internet connection at query time.
  actions:
    - theme: brand
      text: Get started
      link: /guide/getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/mvirtai/clible-v2

features:
  - icon: 📖
    title: Verse lookup
    details: Resolve any reference like "John 3:16" or "Genesis 1:1-3" instantly from a local SQLite database.
  - icon: 🔎
    title: FTS5 full-text search
    details: SQLite-backed search across the whole Bible, scoped to a book, chapter, testament, or verse range.
  - icon: 📊
    title: Text analytics
    details: Word frequency, lexical diversity, n-grams, concordance, and side-by-side translation comparison.
  - icon: 🤖
    title: AI insights
    details: Optional Gemini-powered study notes and tone analysis, rate-limited and key-protected.
  - icon: 🧱
    title: Layered architecture
    details: UI → Services → Repositories → SQLite. Each layer is independently testable.
  - icon: 🐳
    title: Single-image deploy
    details: Web + CLI ship in one Docker image. Cloud Run, Fly.io, or any container host works.
---

## At a glance

```bash
# install dependencies
uv sync --all-groups

# seed an English translation (one-time, ~4 MB)
uv run clible seed install web

# look up a verse
uv run clible verse "John 3:16"

# full-text search
uv run clible search "grace" --scope book --reference Romans

# analytics for a chapter
uv run clible analytics chapter John 3
```

## Documentation map

| You want to…                                | Start here                                      |
|---------------------------------------------|-------------------------------------------------|
| Try the CLI locally                         | [Getting started](/guide/getting-started)       |
| Understand the layers                       | [Architecture overview](/architecture/overview) |
| Read the design decisions                   | [ADR-001](/architecture/adr/001-offline-first-sqlite) |
| Use the web API                             | [API reference](/api/reference)                 |
| Deploy to Cloud Run                         | [Deployment guide](/guide/deployment)           |
| Contribute or extend the project            | [Development guide](/guide/development)         |

