# PR: renew --help messages across CLI

**Branch:** `feat/renew-help-messages-across-cli`  
**Base:** `main`  
**Type:** Feature  
**Date:** 2026-03-18

## Summary

- **Consistent Click `--help` behavior**
  - For all affected commands, Click’s default help option was disabled (`add_help_option=False` + empty `help_option_names`).
  - Added an explicit `--help` flag that prints the centralized Rich help text and exits.
  - Adjusted primary arguments to `required=False` so `--help` prints even when required arguments are omitted.

- **Analytics consistency**
  - Updated analytics subcommands to follow the same help wiring pattern.

## How to test locally

- Quality gates:
  - `uv run pytest -v`
  - `uv run ruff check .`
  - `uv run ruff format --check .`
- Smoke checks:
  - `uv run clible seed install web --help`
  - `uv run clible verse "John 3:16" --help`
  - `uv run clible search grace --help`
  - `uv run clible backup gcs --help`
  - `uv run clible backup restore-gcs gs://my-bucket/backups/clible.db --help`

## Why this matters

- Users get consistent, Rich-formatted help without mixing Click’s raw output with custom help.
- Help content becomes easier to maintain because templates live in one place (`src/clible/ui/help_texts.py`).
