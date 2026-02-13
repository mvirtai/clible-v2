# Developer Skills and Context

This file documents the developer's current skill level, background, and
learning trajectory. AI assistants should use this to calibrate explanations,
code suggestions, and architectural guidance.

---

## Who Is Building This

**Name:** Valtteri
**Role:** Junior Data / Software Engineer (active job seeker)
**Career goal:** Grow from junior to solid mid-level backend-oriented engineer

This project is a portfolio piece and a learning vehicle. The code must be
clean, professional, and explainable in an interview. It should demonstrate
real engineering skills, not AI-generated boilerplate.

---

## Language Proficiency

| Language       | Level              | Notes                                       |
|----------------|--------------------|---------------------------------------------|
| Python         | Strong             | Daily use. Backend, scripting, data work.    |
| SQL            | Beginner–Inter.    | CRUD, joins, basic modeling. Learning query  |
|                |                    | planning, indexing, and migrations.          |
| JavaScript/TS  | Intermediate       | Frontend, React. Not the focus right now.    |
| Go             | Beginner           | Learning for backend services and tooling.   |
| Java / Kotlin  | Beginner           | Actively learning for backend.               |
| Bash / Shell   | Basic–Intermediate | Linux workflows, scripting, fish shell.      |

---

## Concept Familiarity

### Comfortable with (can explain and apply)
- Git fundamentals (branching, merging, rebasing, stashing)
- Python standard library (pathlib, dataclasses, typing, json, sqlite3)
- Basic SQL (SELECT, INSERT, JOIN, GROUP BY, WHERE, ORDER BY)
- HTTP fundamentals (GET, POST, status codes, JSON APIs)
- Rich library for terminal formatting
- Click for CLI building
- pytest basics (test functions, assertions, fixtures)
- Virtual environments and dependency management (uv, pip)
- Docker basics (Dockerfile, build, run, volumes)
- Linux terminal workflows

### Learning (understands concept, needs practice)
- Repository pattern and layered architecture
- Database migrations
- Dependency injection
- Mocking in tests (pytest-mock, patching)
- SQL indexing and query optimization
- Foreign key constraints and cascade behavior
- Error handling strategies (custom exceptions, error boundaries)
- CI/CD pipelines (GitHub Actions)
- Clean architecture principles

### Exposure only (has seen, needs explanation)
- async/await in Python
- ORMs (SQLAlchemy, etc.) — not used in this project by design
- Design patterns beyond basics (Observer, Strategy, Factory)
- Database connection pooling
- API rate limiting strategies
- Textual TUI framework

---

## Working Style

- **Prefers step-by-step.** Show the reasoning before the code.
- **Wants to understand why.** Not just "use this pattern" but "here's what
  problem it solves and what the alternative looks like."
- **Learns by building.** Concrete examples > abstract theory.
- **Reads code.** Prefers reading clean implementations over long prose.
- **Values simplicity.** Will push back on over-engineering. If stdlib solves
  it, use stdlib.

---

## What "Good Help" Looks Like

1. **Explain before implementing.** A 3-line explanation of why before a
   20-line code block.
2. **Match the skill level.** Don't use advanced metaclass magic when a
   simple class works. Don't over-abstract when a function is fine.
3. **Show alternatives.** "You could do X or Y. X is simpler but Y scales
   better. For this project, X is the right call because..."
4. **Teach patterns through this project.** When introducing a pattern
   (repository, DI, service layer), tie it to a concrete problem in clible.
5. **Flag gotchas.** SQLite quirks, Python footguns, common mistakes.
6. **Review like a senior.** Point out issues: naming, structure, missing
   error handling, test gaps.

---

## What "Bad Help" Looks Like

- Generating 200 lines of code without explanation
- Using patterns the developer can't explain in an interview
- Adding dependencies for things the stdlib handles
- Writing code that "works" but teaches nothing
- Skipping tests because "it's simple"
- Over-documenting obvious code while under-explaining complex decisions

---

## Project-Specific Context

This is a **rebuild** of an existing project (clible v1). The developer has
already built all the features once. The goal of v2 is:

1. Better architecture (layered, testable, maintainable)
2. Deeper understanding of each component
3. Cleaner, more professional codebase
4. A portfolio piece that demonstrates real engineering skill

The developer already knows *what* the app does. The focus is on *how* to
build it properly.
