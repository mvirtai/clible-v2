# Beta Testing Deployment Guide

Quick guide to deploy clible-v2 for beta testing on Google Cloud Run with your Gemini API key and rate limits.

## Why Cloud Run for Beta Testing?

- **Free tier**: 2 million requests/month, 360k GB-seconds compute
- **Pay-per-use**: Only charged when requests are being handled
- **Auto-scaling**: Scales to zero when idle (no cost)
- **HTTPS included**: Automatic SSL certificate
- **Simple**: Single command deployment

## Cost Estimate (Beta Testing)

With 5 beta testers, 20 AI requests/hour each:

- **Compute**: ~$0.50-2/month (scales to zero when idle)
- **Gemini API**: ~$0.10-1/month (depends on usage)
- **Total**: **~$1-3/month** (likely stays in free tier)

## Prerequisites

1. **Google Cloud account** (free tier available)
2. **Gemini API key** from [Google AI Studio](https://aistudio.google.com/apikey)
3. **gcloud CLI** installed: https://cloud.google.com/sdk/docs/install
4. **Docker** installed: https://docs.docker.com/get-docker/

## Quick Start

### 1. Setup GCP Project

```bash
# Login to Google Cloud
gcloud auth login

# Create new project (or use existing)
gcloud projects create clible-beta --name="Clible Beta"

# Set as active project
gcloud config set project clible-beta

# Enable billing (required for Cloud Run)
# Visit: https://console.cloud.google.com/billing
```

### 2. Deploy

```bash
# From repo root
./scripts/deploy-beta.sh
```

The script will:
- Enable required APIs
- Create Artifact Registry
- Build and push Docker image
- Deploy to Cloud Run
- Configure rate limiting (20 requests/hour default)

You'll be prompted for:
- GCP Project ID
- Gemini API Key

### 3. Test

```bash
# Visit the URL shown after deployment
# Example: https://clible-web-abc123-ew.a.run.app

# Test API
curl https://YOUR-URL.run.app
```

## Configuration

### Rate Limits

Default: 20 AI requests per hour per user

To change:

```bash
export MAX_REQUESTS_PER_HOUR=50
./scripts/deploy-beta.sh
```

Or update after deployment:

```bash
gcloud run services update clible-web \
  --update-env-vars MAX_REQUESTS_PER_HOUR=50 \
  --region=europe-north1
```

### Scaling Limits

Default: 0-3 instances (good for beta)

To adjust:

```bash
gcloud run services update clible-web \
  --min-instances=0 \
  --max-instances=5 \
  --region=europe-north1
```

## Monitoring

### View Logs

```bash
gcloud run services logs read clible-web \
  --region=europe-north1 \
  --limit=50
```

### View Metrics

Visit: https://console.cloud.google.com/run

Select your service → Metrics tab

### Check Costs

Visit: https://console.cloud.google.com/billing

## Beta Tester Instructions

Share this with your beta testers:

```
Welcome to clible-v2 beta!

URL: https://YOUR-URL.run.app

Features:
- Bible verse lookup
- Full-text search
- AI-powered insights (20 requests/hour)
- Text analytics

Please report issues to: YOUR_EMAIL

Rate limits:
- 20 AI requests per hour
- Resets every hour
```

## Updating the App

```bash
# Make changes to code
# Then redeploy
./scripts/deploy-beta.sh
```

Cloud Run will:
- Build new image
- Deploy with zero downtime
- Keep old version until new one is ready

## Troubleshooting

### "Permission denied" errors

```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login
```

### "Billing not enabled"

Visit: https://console.cloud.google.com/billing
Enable billing for your project (free tier available)

### "API not enabled"

```bash
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  --project=YOUR_PROJECT_ID
```

### High costs

Check usage:
```bash
gcloud run services describe clible-web \
  --region=europe-north1 \
  --format="value(status.traffic)"
```

Reduce max instances:
```bash
gcloud run services update clible-web \
  --max-instances=2 \
  --region=europe-north1
```

## Cleanup

When beta testing is done:

```bash
# Delete Cloud Run service
gcloud run services delete clible-web --region=europe-north1

# Delete Artifact Registry images
gcloud artifacts repositories delete clible --location=europe-north1

# Delete project (removes everything)
gcloud projects delete clible-beta
```

## Next Steps

After successful beta testing:

1. **Custom domain**: Map your own domain
2. **Authentication**: Add user accounts
3. **Analytics**: Track usage patterns
4. **Backup**: Setup database backups
5. **CI/CD**: Automate deployments

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production setup.

## Support

- **GCP Free Tier**: https://cloud.google.com/free
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Gemini API Pricing**: https://ai.google.dev/pricing
