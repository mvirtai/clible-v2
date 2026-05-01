# devops: WIF/OIDC CI Docker push to GCP (Terraform-lite)

This PR improves CI so quality checks use the project’s `Taskfile` (`task check`) and the Docker image is pushed to GCP Artifact Registry only for `main` branch pushes. It also adds a Terraform-lite configuration to provision the required GitHub Actions WIF/OIDC resources and service account impersonation.

## Summary

- Update GitHub Actions CI to run `task check` + `task build` on PRs and push Docker images only on `main` pushes
- Add GitHub Actions → GCP authentication via Workload Identity Federation (OIDC) for Artifact Registry pushes
- Add Terraform-lite under `infra/terraform/gcp-ci-wif/` to create:
  - Workload Identity Pool + OIDC Provider restricted to `mvirtai/clible-v2`
  - IAM binding on the CI service account for `roles/iam.workloadIdentityUser`
- Update documentation to include Terraform-based CI setup flow
- Update `.gitignore` to exclude Terraform state files

## Files added

- `infra/terraform/gcp-ci-wif/versions.tf`
- `infra/terraform/gcp-ci-wif/variables.tf`
- `infra/terraform/gcp-ci-wif/main.tf`
- `infra/terraform/gcp-ci-wif/outputs.tf`
- `infra/terraform/gcp-ci-wif/README.md`

## Files modified

- `.github/workflows/ci.yml`
- `.gitignore`
- `docs/GCP_SETUP.md`

## Tests

- CI runs `task check` which executes:
  - `uv run ruff check .`
  - `uv run ruff format --check .`
  - `uv run pytest -v`
- After Terraform setup, verify `main` branch push logs include:
  - `Authenticate to Google Cloud (Artifact Registry)`
  - `Push Docker image to GCP`

## Usage

1. Provision WIF resources:

   ```bash
   cd infra/terraform/gcp-ci-wif
   terraform init
   terraform plan
   terraform apply
   ```

2. Copy Terraform outputs into GitHub Actions secrets:
   - `WIF_PROVIDER`
   - `GCP_SERVICE_ACCOUNT`
   - `GCP_PROJECT_ID`
   - `CLIBLE_GCP_ARTIFACT_REGISTRY`
3. Push a commit to `main` and check the workflow succeeds and pushes to GCP.

## Notes

- IDE linter warnings about `secrets.*` context may appear; the workflow runtime behavior should be validated via GitHub Actions logs.
