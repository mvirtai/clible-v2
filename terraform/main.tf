# Terraform configuration for clible-v2 on Google Cloud Platform

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-north1"
}

variable "domain" {
  description = "Custom domain for the web app"
  type        = string
  default     = ""
}

variable "gemini_api_key" {
  description = "Gemini API key"
  type        = string
  sensitive   = true
}

variable "session_secret" {
  description = "Session secret for web app"
  type        = string
  sensitive   = true
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "run" {
  service = "run.googleapis.com"
}

resource "google_project_service" "artifact_registry" {
  service = "artifactregistry.googleapis.com"
}

resource "google_project_service" "storage" {
  service = "storage.googleapis.com"
}

# Artifact Registry repository
resource "google_artifact_registry_repository" "clible" {
  location      = var.region
  repository_id = "clible"
  format        = "DOCKER"
  description   = "clible-v2 container images"
}

# GCS bucket for data persistence
resource "google_storage_bucket" "clible_data" {
  name          = "${var.project_id}-clible-data"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 5
    }
    action {
      type = "Delete"
    }
  }
}

# Service account for Cloud Run
resource "google_service_account" "clible_web" {
  account_id   = "clible-web-sa"
  display_name = "clible-web Cloud Run Service Account"
}

# Grant storage access to service account
resource "google_storage_bucket_iam_member" "clible_web_storage" {
  bucket = google_storage_bucket.clible_data.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.clible_web.email}"
}

# Cloud Run service
resource "google_cloud_run_v2_service" "clible_web" {
  name     = "clible-web"
  location = var.region

  template {
    service_account = google_service_account.clible_web.email

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/clible/clible-web:latest"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "NODE_ENV"
        value = "production"
      }

      env {
        name  = "GEMINI_API_KEY"
        value = var.gemini_api_key
      }

      env {
        name  = "SESSION_SECRET"
        value = var.session_secret
      }

      env {
        name  = "CLIBLE_GCS_BUCKET"
        value = google_storage_bucket.clible_data.name
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.run,
    google_artifact_registry_repository.clible
  ]
}

# Allow unauthenticated access
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.clible_web.name
  location = google_cloud_run_v2_service.clible_web.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "service_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.clible_web.uri
}

output "artifact_registry" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/clible"
}

output "gcs_bucket" {
  description = "GCS bucket name for data"
  value       = google_storage_bucket.clible_data.name
}
