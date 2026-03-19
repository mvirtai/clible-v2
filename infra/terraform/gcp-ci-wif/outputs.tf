output "wif_provider_resource_name" {
  description = "Full WIF provider resource name for GitHub Actions auth (use as WIF_PROVIDER secret)"
  value       = google_iam_workload_identity_pool_provider.github_oidc.name
}

output "service_account_email" {
  description = "Service account email for GCP_SERVICE_ACCOUNT secret"
  value       = var.service_account_email
}

output "project_id" {
  description = "GCP project ID for GCP_PROJECT_ID secret"
  value       = var.project_id
}

output "artifact_registry_prefix" {
  description = "Artifact Registry prefix for CLIBLE_GCP_ARTIFACT_REGISTRY secret"
  value       = "europe-north1-docker.pkg.dev/${var.project_id}/clible"
}
