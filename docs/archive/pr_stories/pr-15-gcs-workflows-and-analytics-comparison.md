## PR 15 — GCS workflows and analytics comparison

### Summary

- Add end-to-end Google Cloud Storage workflows for the SQLite database: `clible backup gcs` and `clible backup restore-gcs`.
- Add a Docker/Artifact Registry workflow so the `clible-v2` image can be built, tagged, and pushed to GCP with `task d-push-gcp`.
- Extend the analytics CLI with `clible analytics compare`, which compares two translations side-by-side with word-level diffs and similarity metrics.

### What changed

- **Backup & restore**
  - `clible backup gcs` uploads the configured SQLite database to a GCS bucket using Application Default Credentials.
  - `clible backup restore-gcs gs://...` downloads a backup, writes a local `.pre-restore-<timestamp>.bak` of the current DB, and then replaces it.
  - Both commands now show a Rich spinner with a short status message (file size, download/apply phase) so long-running operations feel responsive.
  - GCS upload timeout is configurable via `CLIBLE_GCS_UPLOAD_TIMEOUT` (default 300 seconds) and is covered by tests.

- **Configuration & docs**
  - `Config` now includes GCS-related settings: bucket name, backup prefix, upload timeout, and seed base URL.
  - `docs/GCP_SETUP.md` documents the full flow:
    - creating a bucket and a Docker Artifact Registry repository,
    - setting up ADC (`gcloud auth application-default login` + quota project),
    - configuring Docker (`gcloud auth configure-docker ...`),
    - running `task d-push-gcp` and `clible backup gcs` / `restore-gcs`.
  - The GCP docs also include troubleshooting sections for common 403/404 errors and upload timeouts.

- **Analytics comparison (CLI)**
  - `clible analytics compare "<reference>" --left <id> --right <id>`:
    - fetches aligned verses from two translations,
    - shows them side-by-side with word-level Rich diffs,
    - reports similarity metrics (per-verse similarity, exact match count, average similarity, shared vocabulary, “most similar” verse).
  - CLI tests cover success and failure paths (missing translations, same translation on both sides, references with no verses).
  - Service-layer tests cover alignment, similarity calculation, and edge cases (unmatched verses, empty results).

### How to test locally

- **Quality gates**
  - `uv run pytest -q`
  - `uv run ruff check .`
  - `uv run ruff format --check .`

- **GCS backup & restore (requires GCP)**
  1. Follow `docs/GCP_SETUP.md` to:
     - create a bucket and Docker repo,
     - enable Artifact Registry API,
     - set up ADC and Docker auth.
  2. Set environment variables (e.g. via `.env` / `.envrc`):
     - `CLIBLE_GCS_BUCKET`
     - `CLIBLE_GCS_BACKUP_PREFIX` (optional, default `backups`)
     - `CLIBLE_GCS_UPLOAD_TIMEOUT` (optional, e.g. 600 for slow uplinks)
  3. Run:
     - `clible backup gcs`
     - `clible backup restore-gcs "gs://.../clible-YYYYMMDD-HHMMSS.db"`

- **Artifact Registry push**
  - `task d-build`
  - `export CLIBLE_GCP_ARTIFACT_REGISTRY=europe-north1-docker.pkg.dev/<PROJECT_ID>/clible`
  - `task d-push-gcp`

- **Analytics comparison**
  - Install at least two translations (e.g. `fin-1992` and `fin-1776`).
  - Run:
    - `clible analytics compare "John 3:16-18"`
    - `clible analytics compare "Psalm 23:1-5" --left fin-1992 --right fin17xx`

### Why this matters

- Makes `clible-v2` feel like a “real” tool: it can back up and restore its state to GCS and has a documented path to run as a Docker image in GCP.
- Improves CLI UX for long-running operations with progress feedback instead of silent waits.
- Adds a compelling analytics feature (translation comparison) that showcases both the text analytics layer and the CLI’s Rich rendering.

