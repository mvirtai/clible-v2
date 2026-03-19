# Terraform: GitHub Actions WIF/OIDC Setup

This Terraform configuration creates the Google Cloud infrastructure needed for GitHub Actions to authenticate and push Docker images to Artifact Registry using Workload Identity Federation (OIDC).

## Quick Start

```bash
cd infra/terraform/gcp-ci-wif
terraform init
terraform plan
terraform apply
terraform output -json  # Copy outputs to GitHub Secrets
```

Then add GitHub Secrets (repo Settings → Secrets and variables → Actions):

- `WIF_PROVIDER` = output `wif_provider_resource_name`
- `GCP_SERVICE_ACCOUNT` = output `service_account_email`
- `GCP_PROJECT_ID` = output `project_id`
- `CLIBLE_GCP_ARTIFACT_REGISTRY` = output `artifact_registry_prefix`

Push to `main` and verify CI succeeds.

## What This Creates

- **Workload Identity Pool** (`clible-github-actions-pool`)
- **Workload Identity Provider** (OIDC, GitHub Actions issuer)
- **IAM binding** on the service account (`github-actions-sa`) with `roles/iam.workloadIdentityUser`

The provider restricts authentication to the repository `mvirtai/clible-v2` only.

## Prerequisites

- `terraform` CLI installed
- `gcloud` CLI authenticated and project set:

  ```bash
  gcloud auth application-default login
  gcloud config set project clible-v2dev
  ```
  
- Service account `github-actions-sa@clible-v2dev.iam.gserviceaccount.com` already exists with `roles/artifactregistry.writer`
- Artifact Registry repository already exists at `europe-north1-docker.pkg.dev/clible-v2dev/clible`

## Usage

### Initialize Terraform

```bash
cd infra/terraform/gcp-ci-wif
terraform init
```

This downloads the Google provider and sets up local state (`.tfstate` file stored in this directory).

### Plan Changes

```bash
terraform plan
```

Review the resources that will be created.

### Apply Configuration

```bash
terraform apply
```

Confirm with `yes` when prompted. This creates the WIF pool, provider, and IAM binding.

### Get Outputs for GitHub Secrets

After `terraform apply` completes, run:

```bash
terraform output -json
```

Or get individual values:

```bash
terraform output wif_provider_resource_name
terraform output service_account_email
terraform output project_id
terraform output artifact_registry_prefix
```

## Configure GitHub Secrets

1. Go to your GitHub repository: **Settings → Secrets and variables → Actions → Secrets**
2. Add these secrets using the Terraform outputs:
   - `WIF_PROVIDER` = output `wif_provider_resource_name`
   - `GCP_SERVICE_ACCOUNT` = output `service_account_email`
   - `GCP_PROJECT_ID` = output `project_id`
   - `CLIBLE_GCP_ARTIFACT_REGISTRY` = output `artifact_registry_prefix`

## Verify

After setting GitHub secrets, push a commit to `main` and check the GitHub Actions workflow logs:

1. The "Authenticate to Google Cloud (Artifact Registry)" step should succeed
2. The "Push Docker image to GCP" step should complete successfully

## State Management

This setup uses **local state** (stored in `terraform.tfstate` in this directory).

**Important:** Do NOT commit `terraform.tfstate` to version control. It may contain sensitive data. The `.gitignore` should exclude `*.tfstate*`.

For team collaboration or production use, migrate to a GCS backend:

```hcl
terraform {
  backend "gcs" {
    bucket = "clible-v2dev-tf-state"
    prefix = "gcp-ci-wif"
  }
}
```

Then run `terraform init -migrate-state`.

## Cleanup

To destroy resources (useful for testing):

```bash
terraform destroy
```
