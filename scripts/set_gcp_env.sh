#!/usr/bin/env bash

# Helper script to set clible-v2dev GCP environment variables and configure Docker
# Source this file to apply to your current shell: source scripts/set_gcp_env.sh

export CLIBLE_GCP_ARTIFACT_REGISTRY="europe-north1-docker.pkg.dev/clible-v2dev/clible"
export CLIBLE_GCS_BUCKET="clible_v2dev_bucket"

echo "Configured Docker to use europe-north1-docker.pkg.dev..."
gcloud auth configure-docker europe-north1-docker.pkg.dev --quiet

echo
echo "GCP environment variables are set:"
echo "CLIBLE_GCP_ARTIFACT_REGISTRY=${CLIBLE_GCP_ARTIFACT_REGISTRY}"
echo "CLIBLE_GCS_BUCKET=${CLIBLE_GCS_BUCKET}"
echo
echo "Docker is configured for GCP Artifact Registry pushes."
