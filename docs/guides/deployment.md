# Deployment Guide

This guide covers deploying clible-v2 to production. The web app runs as a Docker container; the CLI tool is bundled inside it.

---

## Architecture

- **Web app**: Node.js/Express + React (Vite), port 3000
- **CLI**: Python tool spawned as a child process by the Express server
- **Verse data**: SQLite database — seeded with `clible seed install` and optionally backed up to GCS
- **User data**: PostgreSQL (Neon or Cloud SQL) — sessions, settings, auth

---

## Option 1: Google Cloud Run (recommended)

Serverless, auto-scaling, HTTPS and custom domain built-in. Scales to zero between requests.

### One-time setup

```bash
# Enable required APIs
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  storage.googleapis.com

# Create Artifact Registry repository
gcloud artifacts repositories create clible \
  --repository-format=docker \
  --location=europe-north1

# Create GCS bucket for SQLite backup (optional)
gcloud storage buckets create gs://YOUR_BUCKET_NAME \
  --location=europe-north1 \
  --uniform-bucket-level-access
```

### Build and deploy

```bash
# Build and tag image
task web-docker-build
docker tag clible-web-ci europe-north1-docker.pkg.dev/YOUR_PROJECT/clible/clible-web:latest

# Authenticate Docker
gcloud auth configure-docker europe-north1-docker.pkg.dev

# Push
docker push europe-north1-docker.pkg.dev/YOUR_PROJECT/clible/clible-web:latest

# Deploy
gcloud run deploy clible-web \
  --image=europe-north1-docker.pkg.dev/YOUR_PROJECT/clible/clible-web:latest \
  --platform=managed \
  --region=europe-north1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --set-env-vars="GEMINI_API_KEY=${GEMINI_API_KEY},SESSION_SECRET=${SESSION_SECRET},DATABASE_URL=${DATABASE_URL}"
```

### Map custom domain

```bash
gcloud run domain-mappings create \
  --service=clible-web \
  --domain=bible.yourdomain.com \
  --region=europe-north1
```

### Beta / quick deploy

The `scripts/deploy-beta.sh` script automates the full build → push → deploy flow:

```bash
./scripts/deploy-beta.sh
```

Default settings: 512Mi memory, 0–3 instances, europe-north1. Cost estimate: ~$1–3/month for a small beta.

**Quick commands after deploy:**

```bash
# View logs
gcloud run services logs read clible-web --region=europe-north1

# Check service URL
gcloud run services describe clible-web \
  --region=europe-north1 \
  --format='value(status.url)'

# Update an env var
gcloud run services update clible-web \
  --update-env-vars MAX_REQUESTS_PER_HOUR=30 \
  --region=europe-north1
```

---

## Option 2: Google Compute Engine (VM)

Better for persistent SQLite without GCS sync. More maintenance overhead.

```bash
gcloud compute instances create clible-web-vm \
  --zone=europe-north1-a \
  --machine-type=e2-small \
  --boot-disk-size=20GB \
  --image-family=cos-stable \
  --image-project=cos-cloud

# SSH in and run container
gcloud compute ssh clible-web-vm --zone=europe-north1-a

docker run -d \
  --name clible-web \
  --restart=unless-stopped \
  -p 80:3000 \
  -v /mnt/disks/data:/data \
  -e GEMINI_API_KEY=${GEMINI_API_KEY} \
  -e SESSION_SECRET=${SESSION_SECRET} \
  -e DATABASE_URL=${DATABASE_URL} \
  europe-north1-docker.pkg.dev/YOUR_PROJECT/clible/clible-web:latest
```

Add Caddy for automatic HTTPS:

```caddy
bible.yourdomain.com {
    reverse_proxy clible-web:3000
}
```

---

## Option 3: Railway / Render / Fly.io

Zero-config alternatives with free tiers.

| Platform     | Command                                         |
|-------------|--------------------------------------------------|
| Railway      | `railway login && railway init && railway up`   |
| Fly.io       | `fly launch --dockerfile src/clible-web/Dockerfile` |
| Render       | Connect GitHub repo → Web Service → Docker      |

---

## Environment variables

| Variable                      | Required | Description |
|-------------------------------|----------|-------------|
| `GEMINI_API_KEY`              | Yes      | Google Gemini API key for AI features |
| `SESSION_SECRET`              | Yes      | Random 64-char hex string for session signing |
| `DATABASE_URL`                | Yes      | PostgreSQL connection string (Neon or Cloud SQL) |
| `NODE_ENV`                    | No       | Set to `production` |
| `CLIBLE_DB_PATH`              | No       | SQLite path (default: `/data/clible.db`) |
| `CLIBLE_GCS_BUCKET`           | No       | GCS bucket name for SQLite backup |
| `CLIBLE_GCS_BACKUP_PREFIX`    | No       | Object prefix in bucket (default: `backups`) |
| `CLIBLE_GCS_UPLOAD_TIMEOUT`   | No       | Upload timeout in seconds (default: 300) |
| `CLIBLE_SEED_BASE_URL`        | No       | Override seed XML download URL |
| `MAX_REQUESTS_PER_HOUR`       | No       | AI request rate limit per user (default: 20) |

Generate a session secret:

```bash
openssl rand -hex 32
```

---

## GCS backup for SQLite

The CLI can back up the verse database to a GCS bucket:

```bash
# Backup
clible backup gcs

# Restore
clible backup restore-gcs "gs://YOUR_BUCKET/backups/clible-YYYYMMDD-HHMMSS.db"
```

Set `CLIBLE_GCS_BUCKET` in the environment. For authentication, use Application Default Credentials:

```bash
gcloud auth application-default login
```

**Troubleshooting:**
- `invalid_grant` — ADC expired, run `gcloud auth application-default login` again
- Upload timeout — increase `CLIBLE_GCS_UPLOAD_TIMEOUT` (default 300 s)

---

## CI/CD with GitHub Actions

The `.github/workflows/deploy-web.yml` workflow builds and deploys on push to `main`. It uses Workload Identity Federation (no long-lived service account keys).

**One-time Terraform setup:**

```bash
cd infra/terraform/gcp-ci-wif
terraform init && terraform apply
```

**Add GitHub Secrets** (Settings → Secrets → Actions):
- `WIF_PROVIDER` — from `terraform output -raw wif_provider_resource_name`
- `GCP_SERVICE_ACCOUNT` — from `terraform output -raw service_account_email`
- `GCP_PROJECT_ID` — from `terraform output -raw project_id`
- `CLIBLE_GCP_ARTIFACT_REGISTRY` — from `terraform output -raw artifact_registry_prefix`

See `infra/terraform/gcp-ci-wif/README.md` for full details.

---

## Cost estimates (monthly)

| Platform         | Tier                | Cost     |
|-----------------|---------------------|----------|
| Cloud Run        | 1M req, 360k GB-s   | ~$5–15   |
| Compute Engine   | e2-small            | ~$15–20  |
| Fly.io           | Shared CPU-1x       | ~$3      |
| Railway          | Hobby               | $5       |
| Render           | Starter             | $7       |

Cloud Run free tier: 2M requests/month, 360k GB-seconds, 1 GB egress.

---

## Security checklist

- [ ] Use a secrets manager (GCP Secret Manager or GitHub Secrets)
- [ ] Set `NODE_ENV=production`
- [ ] HTTPS only (Cloud Run and Caddy handle this automatically)
- [ ] Rate limiting enabled (`MAX_REQUESTS_PER_HOUR`)
- [ ] Least-privilege IAM for the Cloud Run service account
- [ ] Rotate `SESSION_SECRET` periodically
- [ ] Enable Dependabot for dependency updates

---

## Troubleshooting

**Container won't start**

```bash
docker logs clible-web
task web-docker-run PORT=3000  # test locally first
```

**Database locked errors** — Only one Cloud Run instance should write to SQLite at a time. If you scale beyond one instance, use PostgreSQL for all data or enable Cloud Storage FUSE for transparent shared access.

**Docker push 403 Forbidden** — Run `gcloud auth configure-docker europe-north1-docker.pkg.dev` and retry.

**Docker push 404 Not Found** — Fix Application Default Credentials:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
gcloud auth configure-docker europe-north1-docker.pkg.dev
```
