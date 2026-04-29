#!/usr/bin/env bash
set -euo pipefail

required_vars=(
  "GCP_PROJECT_ID"
  "GCP_REGION"
  "CLIBLE_GCP_ARTIFACT_REGISTRY"
  "SESSION_SECRET"
  "GEMINI_API_KEY_FOR_BETA_TESTERS"
  "DATABASE_URL"
)

missing=()

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    missing+=("$var_name")
  fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "Missing required environment variables for gcp web deploy:"
  for var_name in "${missing[@]}"; do
    echo "  - $var_name"
  done
  echo
  echo "Hint:"
  echo "  set -a; source .env.production; set +a"
  exit 1
fi

echo "GCP web deploy preflight passed."
echo "Resolved values:"
echo "  GCP_PROJECT_ID=${GCP_PROJECT_ID}"
echo "  GCP_REGION=${GCP_REGION}"
echo "  CLIBLE_GCP_ARTIFACT_REGISTRY=${CLIBLE_GCP_ARTIFACT_REGISTRY}"
echo "  SESSION_SECRET=<set>"
echo "  GEMINI_API_KEY_FOR_BETA_TESTERS=<set>"
echo "  DATABASE_URL=<set>"
