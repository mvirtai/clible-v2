# ADR-002: Strict layer separation (UI → Services → Repositories → DB)

**Status:** Accepted  
**Date:** 2025

---

## Context

Without clear boundaries, CLI tools tend to grow into tangled scripts where database queries, business logic, and output formatting are interleaved in the same function. This makes testing difficult (you cannot unit-test a function that writes SQL and prints Rich tables at the same time), and small changes ripple unpredictably across the codebase.

## Decision

The codebase enforces four distinct layers with explicit rules about what each layer may access:

| Layer        | Can access                        | Cannot access                  |
|--------------|-----------------------------------|--------------------------------|
| UI           | Services                          | Repos, DB, parsers, HTTP       |
| Services     | Repos, parsers, storage backends  | UI, Click, Rich                |
| Repositories | `sqlite3.Connection`              | Services, UI, network          |
| Parsers      | File system (read XML only)       | DB, UI, services internals     |

**Repositories** return plain `dict` or `TypedDict` values. They never print, log, or make network calls. They receive a connection object — they do not create one.

**Services** coordinate repositories and parsers. They own business logic: resolving a `translation_id`, deciding which parser to use, building search queries. They do not import `rich` or `click`.

**UI (commands/)** calls services and renders results. It never queries the database directly.

## Consequences

**Positive:**
- Each layer is independently testable: inject an in-memory SQLite connection for repos, a mock parser for services, without booting the full CLI
- Changes to SQL schema only touch repository files; changes to output formatting only touch command files
- New CLI commands are thin wrappers — they call a service method and render the result
- The same service layer can be reused if a different UI (e.g. a REST API) is added

**Negative:**
- More files and classes for simple operations — fetching a verse involves a command, a service, and a repository
- Developers new to the codebase need to understand the layering before making changes

**Trade-off accepted:** The additional structure is worth it because it keeps the test surface clean and prevents the codebase from becoming a "big ball of mud" as features are added.
