variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "clible-v2dev"
}

variable "service_account_email" {
  description = "Service account email for GitHub Actions CI"
  type        = string
  default     = "github-actions-sa@clible-v2dev.iam.gserviceaccount.com"
}

variable "pool_id" {
  description = "Workload Identity Pool ID"
  type        = string
  default     = "clible-github-actions-pool"
}

variable "provider_id" {
  description = "Workload Identity Provider ID"
  type        = string
  default     = "github-oidc-provider"
}

variable "github_repository" {
  description = "GitHub repository in OWNER/REPO format"
  type        = string
  default     = "mvirtai/clible-v2"
}
