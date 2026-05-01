# Cloud Deployment Guide

This guide covers deploying clible-v2 (CLI + web app) to production cloud environments with custom domain support.

## Architecture Overview

- **CLI tool**: Containerized Python app (SQLite backend)
- **Web app**: Node.js/Express + React (Vite), shares SQLite with CLI
- **Data**: SQLite database + XML seed files
- **Storage**: Persistent volumes for database and user data

## Deployment Options

### Option 1: Google Cloud Run (Recommended for Web)

**Pros**: Serverless, auto-scaling, HTTPS/custom domain built-in, cost-effective for variable traffic
**Cons**: Cold starts, stateless (requires Cloud Storage for SQLite persistence)

#### Prerequisites

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  storage.googleapis.com
```

#### Setup

1. **Create Artifact Registry repository**:

```bash
gcloud artifacts repositories create clible \
  --repository-format=docker \
  --location=europe-north1 \
  --description="clible-v2 container images"
```

1. **Configure environment**:

```bash
# .env
CLIBLE_GCP_ARTIFACT_REGISTRY=europe-north1-docker.pkg.dev/YOUR_PROJECT_ID/clible
CLIBLE_GCS_BUCKET=YOUR_PROJECT_ID-clible-data
GEMINI_API_KEY=your_gemini_key
SESSION_SECRET=$(openssl rand -hex 32)
```

1. **Create GCS bucket for database**:

```bash
gcloud storage buckets create gs://${CLIBLE_GCS_BUCKET} \
  --location=europe-north1 \
  --uniform-bucket-level-access
```

4.**Build and push web image**:

```bash
# Build web image
task web-docker-build

# Tag for GCP
docker tag clible-web-ci ${CLIBLE_GCP_ARTIFACT_REGISTRY}/clible-web:latest

# Authenticate Docker
gcloud auth configure-docker europe-north1-docker.pkg.dev

# Push
docker push ${CLIBLE_GCP_ARTIFACT_REGISTRY}/clible-web:latest
```

5.**Deploy to Cloud Run**:

```bash
gcloud run deploy clible-web \
  --image=${CLIBLE_GCP_ARTIFACT_REGISTRY}/clible-web:latest \
  --platform=managed \
  --region=europe-north1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --set-env-vars="GEMINI_API_KEY=${GEMINI_API_KEY},SESSION_SECRET=${SESSION_SECRET},CLIBLE_GCS_BUCKET=${CLIBLE_GCS_BUCKET}" \
  --service-account=clible-web-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

6.**Map custom domain**:

```bash
# Add domain mapping
gcloud run domain-mappings create \
  --service=clible-web \
  --domain=bible.yourdomain.com \
  --region=europe-north1

# Follow DNS instructions from output
```

#### Persistence Strategy for Cloud Run

Since Cloud Run is stateless, modify the web app to:

- Download SQLite DB from GCS on startup
- Periodically sync changes back to GCS
- Use Cloud Storage FUSE for transparent file access

---

### Option 2: Google Compute Engine (VM)

**Pros**: Full control, persistent disk, simple SQLite setup
**Cons**: Always-on costs, manual scaling, more maintenance

#### Setup

1. **Create VM instance**:

```bash
gcloud compute instances create clible-web-vm \
  --zone=europe-north1-a \
  --machine-type=e2-small \
  --boot-disk-size=20GB \
  --image-family=cos-stable \
  --image-project=cos-cloud \
  --tags=http-server,https-server
```

1. **Configure firewall**:

```bash
gcloud compute firewall-rules create allow-http \
  --allow=tcp:80 \
  --target-tags=http-server

gcloud compute firewall-rules create allow-https \
  --allow=tcp:443 \
  --target-tags=https-server
```

1. **SSH and setup Docker**:

```bash
gcloud compute ssh clible-web-vm --zone=europe-north1-a

# Install Docker (if not using Container-Optimized OS)
# Pull and run container
docker pull ${CLIBLE_GCP_ARTIFACT_REGISTRY}/clible-web:latest

docker run -d \
  --name clible-web \
  --restart=unless-stopped \
  -p 80:3000 \
  -v /mnt/disks/clible-data:/home/clible/.clible-data \
  -v /mnt/disks/clible-web-data:/app/web/data \
  -e GEMINI_API_KEY=${GEMINI_API_KEY} \
  -e SESSION_SECRET=${SESSION_SECRET} \
  ${CLIBLE_GCP_ARTIFACT_REGISTRY}/clible-web:latest
```

1. **Setup reverse proxy with Caddy** (automatic HTTPS):

```bash
# Install Caddy
docker run -d \
  --name caddy \
  --restart=unless-stopped \
  -p 80:80 \
  -p 443:443 \
  -v caddy_data:/data \
  -v caddy_config:/config \
  -v /root/Caddyfile:/etc/caddy/Caddyfile \
  caddy:latest

# Caddyfile content:
# bible.yourdomain.com {
#     reverse_proxy clible-web:3000
# }
```

---

### Option 3: AWS (ECS Fargate + RDS/EFS)

**Pros**: Managed containers, AWS ecosystem integration
**Cons**: More complex setup, higher cost

#### Setup

1. **Create ECR repository**:

```bash
aws ecr create-repository --repository-name clible-web --region eu-north-1
```

1. **Push image**:

```bash
aws ecr get-login-password --region eu-north-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.eu-north-1.amazonaws.com

docker tag clible-web-ci YOUR_ACCOUNT.dkr.ecr.eu-north-1.amazonaws.com/clible-web:latest
docker push YOUR_ACCOUNT.dkr.ecr.eu-north-1.amazonaws.com/clible-web:latest
```

1. **Create EFS for persistent storage**:

```bash
aws efs create-file-system \
  --region eu-north-1 \
  --performance-mode generalPurpose \
  --tags Key=Name,Value=clible-data
```

1. **Deploy with ECS Fargate**:

- Create ECS cluster
- Define task definition with EFS volume mounts
- Create service with Application Load Balancer
- Configure Route53 for custom domain

---

### Option 4: DigitalOcean App Platform

**Pros**: Simple deployment, managed platform, affordable
**Cons**: Less control, limited customization

#### Setup

1. **Create `app.yaml`**:

```yaml
name: clible-web
region: fra
services:
  - name: web
    github:
      repo: your-username/clible-v2
      branch: main
      deploy_on_push: true
    dockerfile_path: src/clible-web/Dockerfile
    http_port: 3000
    instance_count: 1
    instance_size_slug: basic-xs
    envs:
      - key: GEMINI_API_KEY
        scope: RUN_TIME
        type: SECRET
      - key: SESSION_SECRET
        scope: RUN_TIME
        type: SECRET
    routes:
      - path: /
domains:
  - domain: bible.yourdomain.com
    type: PRIMARY
```

1. **Deploy**:

```bash
doctl apps create --spec app.yaml
```

---

### Option 5: Railway / Render / Fly.io

**Pros**: Zero-config deployment, free tier available
**Cons**: Limited resources on free tier

#### Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and init
railway login
railway init

# Deploy
railway up
```

#### Render

1. Connect GitHub repo
2. Select "Web Service"
3. Docker deployment
4. Set environment variables
5. Add custom domain in dashboard

#### Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch app
fly launch --dockerfile src/clible-web/Dockerfile

# Add custom domain
fly certs add bible.yourdomain.com
```

---

## Domain Configuration

### DNS Setup (Generic)

For any cloud provider, configure DNS:

```
Type: A or CNAME
Name: bible (or @)
Value: [Cloud provider IP/hostname]
TTL: 3600
```

### SSL/TLS Certificates

- **Cloud Run**: Automatic with domain mapping
- **Compute Engine + Caddy**: Automatic Let's Encrypt
- **AWS ALB**: AWS Certificate Manager
- **DigitalOcean/Railway/Render/Fly**: Automatic

---

## Environment Variables (Production)

Required for all deployments:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key
SESSION_SECRET=random_64_char_hex_string

# Optional
NODE_ENV=production
CLIBLE_DB_PATH=/data/clible.db
CLIBLE_GCS_BUCKET=your-bucket-name  # For GCP deployments
```

---

## CI/CD Pipeline

### GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2
      
      - name: Configure Docker
        run: gcloud auth configure-docker europe-north1-docker.pkg.dev
      
      - name: Build and push
        run: |
          docker build -f src/clible-web/Dockerfile -t ${{ secrets.GCP_REGISTRY }}/clible-web:${{ github.sha }} .
          docker push ${{ secrets.GCP_REGISTRY }}/clible-web:${{ github.sha }}
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy clible-web \
            --image=${{ secrets.GCP_REGISTRY }}/clible-web:${{ github.sha }} \
            --region=europe-north1 \
            --platform=managed
```

---

## Monitoring & Observability

### Cloud Run

```bash
# View logs
gcloud run services logs read clible-web --region=europe-north1 --limit=50

# Monitor metrics
gcloud monitoring dashboards list
```

### Generic (All platforms)

- **Uptime monitoring**: UptimeRobot, Pingdom
- **Error tracking**: Sentry
- **Analytics**: Google Analytics, Plausible

---

## Cost Estimates (Monthly)

| Platform | Tier | Cost |
|----------|------|------|
| Cloud Run | 1M requests, 360k GB-s | ~$5-15 |
| Compute Engine | e2-small (2 vCPU, 2GB) | ~$15-20 |
| AWS Fargate | 0.25 vCPU, 0.5GB | ~$10-15 |
| DigitalOcean | Basic (512MB) | $5 |
| Railway | Hobby | $5 |
| Render | Starter | $7 |
| Fly.io | Shared CPU-1x | $3 |

---

## Recommended Setup

**For production with custom domain:**

1. **Google Cloud Run** (web app) + **Cloud Storage** (database backup)
2. **Caddy** reverse proxy for automatic HTTPS
3. **GitHub Actions** for CI/CD
4. **Sentry** for error tracking

**Quick start:**

```bash
# 1. Setup GCP
task push-to-gcp

# 2. Deploy
gcloud run deploy clible-web \
  --image=${CLIBLE_GCP_ARTIFACT_REGISTRY}/clible-web:latest \
  --region=europe-north1 \
  --allow-unauthenticated

# 3. Map domain
gcloud run domain-mappings create --service=clible-web --domain=bible.yourdomain.com
```

---

## Security Checklist

- [ ] Use secrets manager (GCP Secret Manager, AWS Secrets Manager)
- [ ] Enable HTTPS only
- [ ] Set up WAF/DDoS protection (Cloudflare)
- [ ] Implement rate limiting
- [ ] Regular security updates (Dependabot)
- [ ] Backup database regularly
- [ ] Use least-privilege IAM roles
- [ ] Enable audit logging

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs clible-web-ci

# Test locally first
task web-docker-run PORT=3000
```

### Database locked errors

- Ensure only one instance writes to SQLite
- Consider PostgreSQL for multi-instance deployments

### High memory usage

- Increase container memory limits
- Optimize SQLite queries
- Enable query result caching

---

## Next Steps

1. Choose deployment platform
2. Set up domain and DNS
3. Configure CI/CD pipeline
4. Deploy and test
5. Set up monitoring
6. Configure backups

For GCP-specific setup, see [GCP_SETUP.md](./GCP_SETUP.md).
