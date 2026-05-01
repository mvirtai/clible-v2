# Beta Deployment Quick Reference

## One-Command Deploy

```bash
./scripts/deploy-beta.sh
```

## What You Need

1. Gemini API key: https://aistudio.google.com/apikey
2. GCP project with billing enabled
3. gcloud CLI + Docker installed

## Default Settings

- **Rate limit**: 20 AI requests/hour per user
- **Instances**: 0-3 (scales to zero)
- **Memory**: 512Mi
- **Region**: europe-north1
- **Cost**: ~$1-3/month for 5 beta testers

## Quick Commands

```bash
# View logs
gcloud run services logs read clible-web --region=europe-north1

# Update rate limit
gcloud run services update clible-web \
  --update-env-vars MAX_REQUESTS_PER_HOUR=30 \
  --region=europe-north1

# Check service URL
gcloud run services describe clible-web \
  --region=europe-north1 \
  --format='value(status.url)'

# Delete service
gcloud run services delete clible-web --region=europe-north1
```

## Files Created

- `.env.production` - Deployment config (keep secure!)
- Artifact Registry: `europe-north1-docker.pkg.dev/PROJECT/clible`
- Cloud Run service: `clible-web`

## Rate Limit Headers

API responses include:
- `X-RateLimit-Limit`: Max requests allowed
- `X-RateLimit-Remaining`: Requests left
- `X-RateLimit-Reset`: Seconds until reset

## Cost Control

Free tier covers:
- 2M requests/month
- 360k GB-seconds compute
- 1 GB network egress

To stay in free tier:
- Keep max-instances ≤ 3
- Use default 512Mi memory
- Monitor usage in GCP Console

## Support

Full guide: [docs/BETA_DEPLOYMENT.md](./BETA_DEPLOYMENT.md)
