# Free & Low-Cost Deployment (No Domain Required)

Deploy clible-v2 web app without buying a domain. All options provide a free subdomain with HTTPS.

## Recommended: Free Tier Options

### Option 1: Render.com (Best Free Tier)

**Cost**: FREE (750 hours/month)
**URL**: `https://clible-web.onrender.com` (auto-generated)
**Pros**: Simple, persistent disk, auto-sleep after 15min inactivity
**Cons**: Cold starts (~30s wake-up)

#### Deploy in 3 steps:

1. **Push code to GitHub** (if not already)

2. **Sign up at [render.com](https://render.com)** with GitHub

3. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your `clible-v2` repository
   - Settings:
     - **Name**: `clible-web`
     - **Runtime**: Docker
     - **Dockerfile Path**: `src/clible-web/Dockerfile`
     - **Instance Type**: Free
   - Add environment variables:
     - `GEMINI_API_KEY`: your-key
     - `SESSION_SECRET`: (click "Generate")
     - `NODE_ENV`: production
   - Add Disk:
     - **Name**: `clible-data`
     - **Mount Path**: `/home/clible/.clible-data`
     - **Size**: 1GB
   - Click "Create Web Service"

**Done!** Your app will be live at `https://clible-web-xxxx.onrender.com`

---

### Option 2: Railway.app (Generous Free Trial)

**Cost**: $5 credit/month (enough for small apps)
**URL**: `https://clible-web-production.up.railway.app` (auto-generated)
**Pros**: No cold starts, fast deployment, great DX
**Cons**: Credit runs out with heavy usage

#### Deploy:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Get URL
railway domain
```

Or use the web dashboard:
1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Select `clible-v2`
4. Add environment variables in Settings
5. Get URL from Deployments tab

---

### Option 3: Fly.io (Best Performance)

**Cost**: FREE (3 shared-cpu VMs, 3GB storage)
**URL**: `https://clible-web.fly.dev` (auto-generated)
**Pros**: Global edge deployment, no cold starts, persistent volumes
**Cons**: Requires credit card (not charged on free tier)

#### Deploy:

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch (creates fly.toml)
fly launch --dockerfile src/clible-web/Dockerfile --name clible-web

# Set secrets
fly secrets set GEMINI_API_KEY=your-key
fly secrets set SESSION_SECRET=$(openssl rand -hex 32)

# Create volume for database
fly volumes create clible_data --size 1 --region fra

# Deploy
fly deploy
```

**fly.toml** configuration:
```toml
app = "clible-web"
primary_region = "fra"

[build]
  dockerfile = "src/clible-web/Dockerfile"

[env]
  NODE_ENV = "production"
  PORT = "3000"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[mounts]]
  source = "clible_data"
  destination = "/home/clible/.clible-data"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_gb = 1
```

---

### Option 4: Google Cloud Run (Always Free Tier)

**Cost**: FREE (2M requests/month, 360k GB-seconds)
**URL**: `https://clible-web-xxxxx-uc.a.run.app` (auto-generated)
**Pros**: Scales to zero, Google infrastructure, generous free tier
**Cons**: Cold starts, requires GCP account

#### Quick deploy:

```bash
# Use the deployment script
./scripts/deploy-gcp.sh

# Or manually:
gcloud run deploy clible-web \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API_KEY=xxx,SESSION_SECRET=xxx"
```

**Note**: SQLite persistence requires Cloud Storage (see DEPLOYMENT.md)

---

### Option 5: Vercel (Frontend Focus)

**Cost**: FREE (hobby tier)
**URL**: `https://clible-web.vercel.app` (auto-generated)
**Pros**: Instant deployment, great for static sites
**Cons**: Serverless functions have 10s timeout, not ideal for SQLite

#### Deploy:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Or connect GitHub repo in [vercel.com](https://vercel.com) dashboard.

---

## Comparison Table

| Platform | Free Tier | Cold Starts | Persistent Storage | Setup Time | Best For |
|----------|-----------|-------------|-------------------|------------|----------|
| **Render** | ✅ 750h/mo | ⚠️ Yes (~30s) | ✅ 1GB disk | 5 min | Hobby projects |
| **Railway** | ⚠️ $5 credit | ✅ No | ✅ Volumes | 2 min | Active development |
| **Fly.io** | ✅ 3 VMs | ✅ No | ✅ 3GB volumes | 5 min | Production-ready |
| **Cloud Run** | ✅ 2M req/mo | ⚠️ Yes (~5s) | ⚠️ Needs GCS | 10 min | Scalable apps |
| **Vercel** | ✅ Unlimited | ✅ No | ❌ Serverless | 2 min | Static/API |

---

## Recommended Path

### For Testing/Demo:
**Use Render** - Completely free, zero config, just works.

### For Active Use:
**Use Fly.io** - Best free tier, no cold starts, persistent storage.

### For Production:
**Use Railway** ($5/mo) or **upgrade Render** ($7/mo) - Reliable, no cold starts.

---

## Getting a Free Subdomain

All platforms provide free HTTPS subdomains:

- **Render**: `your-app.onrender.com`
- **Railway**: `your-app.up.railway.app`
- **Fly.io**: `your-app.fly.dev`
- **Cloud Run**: `your-app-hash.run.app`
- **Vercel**: `your-app.vercel.app`

You can use these indefinitely without buying a domain.

---

## When to Buy a Domain

Buy a custom domain ($10-15/year) when:
- You want a professional URL (e.g., `bible.yourname.com`)
- You need custom branding
- You're ready for production users

**Cheap domain registrars**:
- **Cloudflare** ($9/year for .com, no markup)
- **Namecheap** ($10-12/year)
- **Porkbun** ($10/year)

All platforms support custom domains on free tiers.

---

## Quick Start: Deploy to Render Now

1. **Create `render.yaml`** (already in repo):
```yaml
services:
  - type: web
    name: clible-web
    runtime: docker
    dockerfilePath: ./src/clible-web/Dockerfile
    dockerContext: .
    plan: free
    envVars:
      - key: NODE_ENV
        value: production
      - key: GEMINI_API_KEY
        sync: false
      - key: SESSION_SECRET
        generateValue: true
    disk:
      name: clible-data
      mountPath: /home/clible/.clible-data
      sizeGB: 1
```

2. **Push to GitHub**:
```bash
git add .
git commit -m "Add deployment configs"
git push
```

3. **Deploy**:
   - Go to [render.com](https://render.com)
   - Sign in with GitHub
   - "New +" → "Blueprint"
   - Select your repo
   - Add `GEMINI_API_KEY` in dashboard
   - Click "Apply"

**Live in 3 minutes!** 🚀

---

## Cost Estimates (Monthly)

| Usage Level | Platform | Cost |
|-------------|----------|------|
| **Hobby** (few users) | Render Free | $0 |
| **Light** (<100 users) | Fly.io Free | $0 |
| **Medium** (100-1k users) | Railway | $5-10 |
| **Heavy** (1k-10k users) | Render Starter | $7-15 |
| **Production** (10k+ users) | Cloud Run | $15-50 |

---

## Next Steps

1. **Choose platform** (Render for easiest start)
2. **Deploy** (follow steps above)
3. **Test** your app at the provided URL
4. **Optional**: Buy domain later and map it
5. **Optional**: Set up monitoring (UptimeRobot free tier)

No credit card required for Render, Railway trial, or Fly.io free tier!
