# Google Cloud setup (optional)

This document describes how to use clible with Google Cloud: backing up the database to GCS, restoring it back locally, optionally seeding translations from a GCS bucket, and pushing the Docker image to Artifact Registry.

## Prerequisites

- A Google Cloud project
- `gcloud` CLI installed and authenticated (`gcloud auth login`, `gcloud config set project PROJECT_ID`)

## GCS bucket for backups

1. Create a bucket (e.g. `clible-data`):

   ```bash
   gsutil mb -l europe-north1 gs://YOUR_BUCKET_NAME
   ```

2. Configure authentication for the environment where you run `clible backup gcs`:
   - **Local / CI:** Run `gcloud auth application-default login` so Application Default Credentials (ADC) are used.
   - **Service account:** Create a key and set `GOOGLE_APPLICATION_CREDENTIALS` to the JSON key path.

3. Set environment variables:
   - `CLIBLE_GCS_BUCKET` — bucket name (required for backup)
   - `CLIBLE_GCS_BACKUP_PREFIX` — object prefix (default: `backups`). Backups are stored as `gs://BUCKET/PREFIX/clible-YYYYMMDD-HHMMSS.db`.

4. Run backup:

   ```bash
   clible backup gcs
   ```

5. Restore a backup back to the configured local database path:

   ```bash
   clible backup restore-gcs "gs://YOUR_BUCKET_NAME/backups/clible-YYYYMMDD-HHMMSS.db"
   ```

   The command downloads the object to a temporary file, asks for confirmation,
   stores the current local database as `*.pre-restore-<timestamp>.bak`, and
   then replaces the configured database file.

**Troubleshooting**

- **`invalid_grant` / "Bad Request"**: Your Application Default Credentials have expired or were revoked. Run `gcloud auth application-default login` again and retry.
- **"quota project" warning**: If you see a warning about end-user credentials without a quota project, you can set `GOOGLE_CLOUD_PROJECT` to your GCP project ID to silence it, or ignore it if uploads succeed.

## Seed from GCS (optional base URL)

You can serve translation XML files from a GCS bucket and point clible at that location instead of the default GitHub URLs.

1. Upload XML files to your bucket (e.g. under `seed/`). Use the same filenames as in the catalog (`src/clible/data/translations.json`), e.g. `eng-web.usfx.xml`, `eng-kjv.osis.xml`.

2. Make the objects publicly readable (e.g. bucket or object ACL, or a load balancer / CDN in front of GCS). Public URL format:
   `https://storage.googleapis.com/YOUR_BUCKET/seed/FILENAME`

3. Set the base URL (no trailing filename):

   ```bash
   export CLIBLE_SEED_BASE_URL="https://storage.googleapis.com/YOUR_BUCKET/seed"
   ```

4. Install a translation as usual; it will fetch from the base URL + catalog filename:

   ```bash
   clible seed install web
   ```

## Docker image: Artifact Registry

1. Enable the Artifact Registry API and create a repository:

   ```bash
   gcloud services enable artifactregistry.googleapis.com
   gcloud artifacts repositories create clible --repository-format=docker --location=europe-north1
   ```

2. Configure Docker to use Artifact Registry:

   ```bash
   gcloud auth configure-docker europe-docker.pkg.dev
   ```

3. Set the registry prefix (host + project + repo, **without** image name or tag):
   - `CLIBLE_GCP_ARTIFACT_REGISTRY=europe-docker.pkg.dev/YOUR_PROJECT_ID/clible`

4. Build and push:

   ```bash
   task d-build
   export CLIBLE_GCP_ARTIFACT_REGISTRY=europe-docker.pkg.dev/YOUR_PROJECT_ID/clible
   task d-push-gcp
   ```

   Images will be tagged as `europe-docker.pkg.dev/YOUR_PROJECT_ID/clible/clible-v2:GIT_SHA` and `:latest`.

## Environment variable summary

| Variable | Used by | Description |
| -------- | ------- | ----------- |
| `CLIBLE_GCS_BUCKET` | `clible backup gcs` | GCS bucket name for database backups |
| `CLIBLE_GCS_BACKUP_PREFIX` | `clible backup gcs` | Object prefix (default: `backups`) |
| `CLIBLE_SEED_BASE_URL` | `clible seed install` | Base URL for seed XML (e.g. GCS public prefix) |
| `CLIBLE_GCP_ARTIFACT_REGISTRY` | `task d-push-gcp` | Artifact Registry prefix (e.g. `europe-docker.pkg.dev/PROJECT/REPO`) |

## Future options

- **Private GCS seed:** Using the `google-cloud-storage` SDK to download from a private bucket when the catalog or config points to a `gs://` URL.
- **Cloud Run / scheduled backup:** Run the CLI in a container (e.g. Cloud Run job or GCE) and trigger backup on a schedule (e.g. Cloud Scheduler).
