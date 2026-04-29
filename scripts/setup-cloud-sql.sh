#!/usr/bin/env bash
# One-time setup: create a Cloud SQL PostgreSQL instance for clible-web.
# Run after sourcing .env.production:
#   set -a && source .env.production && set +a
#   bash scripts/setup-cloud-sql.sh
#
# Prerequisites: gcloud CLI authenticated, GCP_PROJECT_ID set.

set -euo pipefail

: "${GCP_PROJECT_ID:?GCP_PROJECT_ID must be set}"
: "${GCP_REGION:?GCP_REGION must be set}"
: "${CLIBLE_POSTGRES_USER:?CLIBLE_POSTGRES_USER must be set}"
: "${CLIBLE_POSTGRES_PASSWORD:?CLIBLE_POSTGRES_PASSWORD must be set}"

INSTANCE_NAME="clible-pg"
DB_NAME="clible"
TIER="db-f1-micro"   # cheapest shared-core; upgrade to db-g1-small for more RAM

echo "==> Enabling Cloud SQL Admin API..."
gcloud services enable sqladmin.googleapis.com --project="${GCP_PROJECT_ID}"

echo "==> Creating Cloud SQL instance: ${INSTANCE_NAME} (PostgreSQL 16, ${TIER}, ENTERPRISE)"
gcloud sql instances create "${INSTANCE_NAME}" \
  --database-version=POSTGRES_16 \
  --tier="${TIER}" \
  --edition=ENTERPRISE \
  --region="${GCP_REGION}" \
  --storage-type=SSD \
  --storage-size=10GB \
  --no-storage-auto-increase \
  --project="${GCP_PROJECT_ID}"

echo "==> Creating database: ${DB_NAME}"
gcloud sql databases create "${DB_NAME}" \
  --instance="${INSTANCE_NAME}" \
  --project="${GCP_PROJECT_ID}"

echo "==> Creating user: ${CLIBLE_POSTGRES_USER}"
gcloud sql users create "${CLIBLE_POSTGRES_USER}" \
  --instance="${INSTANCE_NAME}" \
  --password="${CLIBLE_POSTGRES_PASSWORD}" \
  --project="${GCP_PROJECT_ID}"

# Cloud Run's default compute service account needs cloudsql.client so it can
# connect via the built-in Cloud SQL Auth Proxy (unix socket, no extra sidecar).
PROJECT_NUMBER=$(gcloud projects describe "${GCP_PROJECT_ID}" --format='value(projectNumber)')
SA_EMAIL="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "==> Granting cloudsql.client to Cloud Run service account: ${SA_EMAIL}"
gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudsql.client"

CONNECTION_NAME=$(gcloud sql instances describe "${INSTANCE_NAME}" \
  --project="${GCP_PROJECT_ID}" \
  --format='value(connectionName)')

echo ""
echo "===================================================================="
echo "Cloud SQL instance ready."
echo "Add this to .env.production and Cloud Run env vars:"
echo ""
echo "  CLOUD_SQL_CONNECTION_NAME=${CONNECTION_NAME}"
echo "  PGDATABASE=${DB_NAME}"
echo "  PGUSER=${CLIBLE_POSTGRES_USER}"
echo "  PGPASSWORD=${CLIBLE_POSTGRES_PASSWORD}"
echo ""
echo "Then redeploy: task gcp-web-deploy"
echo "===================================================================="
