#!/usr/bin/env bash
set -euo pipefail

TITLE_DEFAULT="feat: add fin-1992 vs fin17xx side-by-side comparison"
BASE_DEFAULT="main"
YES_MODE="false"
PREVIEW_ONLY="false"

TITLE="${PR_TITLE:-$TITLE_DEFAULT}"
BASE_BRANCH="${PR_BASE:-$BASE_DEFAULT}"
HEAD_BRANCH="${PR_HEAD:-$(git branch --show-current)}"

while (($# > 0)); do
  case "$1" in
    --yes)
      YES_MODE="true"
      shift
      ;;
    --preview-only)
      PREVIEW_ONLY="true"
      shift
      ;;
    --title)
      TITLE="$2"
      shift 2
      ;;
    --base)
      BASE_BRANCH="$2"
      shift 2
      ;;
    --head)
      HEAD_BRANCH="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: $0 [--yes] [--preview-only] [--title <title>] [--base <branch>] [--head <branch>]"
      exit 1
      ;;
  esac
done

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required."
  exit 1
fi

if [ -z "$HEAD_BRANCH" ]; then
  echo "Could not resolve current git branch."
  exit 1
fi

PR_BODY_FILE="$(mktemp)"
trap 'rm -f "$PR_BODY_FILE"' EXIT

cat >"$PR_BODY_FILE" <<'EOF'
## Summary
- Add `clible analytics compare "<reference>"` for side-by-side translation comparison.
- Compare default pair `fin-1992` vs `fin17xx` (`fin17xx` alias resolves to `fin-1776`).
- Show verse-by-verse diff and per-verse similarity percentage.
- Add similarity analysis summary: exact match rate, average similarity, most similar verse, top shared vocabulary.

## Implementation details
- Add `compare` command in analytics CLI.
- Add translation alias resolver for `fin17xx` / `fin-17xx`.
- Add service-level comparison logic in `AnalyticService.compare_translations()`:
  - align verses by `(book_id, chapter, verse)`
  - compute similarity from sequence ratio + token-overlap ratio
  - generate aggregate summary metrics
- Register command in CLI entrypoint.
- Update README with compare examples.

## Validation
- Added service tests for:
  - aligned rows + similarity summary
  - missing verses between translations
  - empty comparison result
- Added CLI tests for:
  - successful side-by-side compare output
  - missing translation error path

## Notes
- No PR story file is included in this PR diff.
EOF

echo "----------------------------------------"
echo "PR preview"
echo "Base:  $BASE_BRANCH"
echo "Head:  $HEAD_BRANCH"
echo "Title: $TITLE"
echo "Body:"
echo "----------------------------------------"
cat "$PR_BODY_FILE"
echo "----------------------------------------"

if [ "$PREVIEW_ONLY" = "true" ]; then
  echo "Preview-only mode. PR was not created."
  exit 0
fi

if [ "$YES_MODE" != "true" ]; then
  read -r -p "Create PR with this content? [y/N]: " reply
  case "$reply" in
    y|Y|yes|YES)
      ;;
    *)
      echo "Cancelled."
      exit 0
      ;;
  esac
fi

gh pr create \
  --base "$BASE_BRANCH" \
  --head "$HEAD_BRANCH" \
  --title "$TITLE" \
  --body-file "$PR_BODY_FILE"

