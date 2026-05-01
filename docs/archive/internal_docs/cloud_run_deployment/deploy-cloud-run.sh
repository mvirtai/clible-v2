#!/bin/bash
# Enhanced Cloud Run deployment with rate limiting and monitoring

set -euo pipefail

echo "🚀 clible-v2 Cloud Run Deployment (with Rate Limiting)"
echo "======================================================="
echo ""

# Check prerequisites
command -v gcloud >/dev/null 2>&1 || { echo "❌ gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker not found. Install from https://docs.docker.com/get-docker/"; exit 1; }

# Get project ID
if [ -z "${GCP_PROJECT_ID:-}" ]; then
    read -p "Enter GCP Project ID: " GCP_PROJECT_ID
    export GCP_PROJECT_ID
fi

# Set region
REGION="${GCP_REGION:-europe-north1}"

echo ""
echo "📋 Configuration:"
echo "   Project: $GCP_PROJECT_ID"
echo "   Region: $REGION"
echo ""

# Enable APIs
echo "🔧 Enabling required GCP APIs..."
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  storage.googleapis.com \
  firestore.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  --project=$GCP_PROJECT_ID

# Create Artifact Registry
echo "📦 Creating Artifact Registry repository..."
gcloud artifacts repositories create clible \
  --repository-format=docker \
  --location=$REGION \
  --description="clible-v2 container images" \
  --project=$GCP_PROJECT_ID 2>/dev/null || echo "   Repository already exists"

# Set registry URL
REGISTRY="$REGION-docker.pkg.dev/$GCP_PROJECT_ID/clible"
export CLIBLE_GCP_ARTIFACT_REGISTRY=$REGISTRY

# Create GCS bucket
BUCKET="$GCP_PROJECT_ID-clible-data"
echo "🪣 Creating GCS bucket..."
gcloud storage buckets create gs://$BUCKET \
  --location=$REGION \
  --uniform-bucket-level-access \
  --project=$GCP_PROJECT_ID 2>/dev/null || echo "   Bucket already exists"

# Create service account
echo "👤 Creating service account..."
gcloud iam service-accounts create clible-web-sa \
  --display-name="clible-web Cloud Run Service Account" \
  --project=$GCP_PROJECT_ID 2>/dev/null || echo "   Service account already exists"

SA_EMAIL="clible-web-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com"

# Grant permissions
echo "🔐 Granting permissions..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectAdmin" \
  --project=$GCP_PROJECT_ID >/dev/null 2>&1 || true

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/datastore.user" \
  --condition=None >/dev/null 2>&1 || true

# Initialize Firestore (for rate limiting)
echo "🔥 Initializing Firestore..."
gcloud firestore databases create \
  --location=$REGION \
  --project=$GCP_PROJECT_ID 2>/dev/null || echo "   Firestore already initialized"

# Configure Docker
echo "🐳 Configuring Docker authentication..."
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

# Get secrets
if [ -z "${GEMINI_API_KEY:-}" ]; then
    read -sp "Enter Gemini API Key: " GEMINI_API_KEY
    echo ""
    export GEMINI_API_KEY
fi

if [ -z "${SESSION_SECRET:-}" ]; then
    echo "Generating session secret..."
    SESSION_SECRET=$(openssl rand -hex 32)
    export SESSION_SECRET
fi

# Rate limiting configuration
MAX_REQUESTS_PER_HOUR="${MAX_REQUESTS_PER_HOUR:-20}"
MAX_REQUESTS_PER_DAY="${MAX_REQUESTS_PER_DAY:-50}"
MAX_DAILY_COST_PER_USER="${MAX_DAILY_COST_PER_USER:-0.10}"

echo ""
echo "⚙️  Rate Limiting Configuration:"
echo "   Max requests per hour: $MAX_REQUESTS_PER_HOUR"
echo "   Max requests per day: $MAX_REQUESTS_PER_DAY"
echo "   Max daily cost per user: \$$MAX_DAILY_COST_PER_USER"
echo ""

# Build and push
echo "🏗️  Building web Docker image..."
docker build -f src/clible-web/Dockerfile -t $REGISTRY/clible-web:latest .

echo "⬆️  Pushing to Artifact Registry..."
docker push $REGISTRY/clible-web:latest

# Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy clible-web \
  --image=$REGISTRY/clible-web:latest \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --concurrency=80 \
  --timeout=60 \
  --set-env-vars="
GEMINI_API_KEY=$GEMINI_API_KEY,
SESSION_SECRET=$SESSION_SECRET,
NODE_ENV=production,
CLIBLE_GCS_BUCKET=$BUCKET,
MAX_REQUESTS_PER_HOUR=$MAX_REQUESTS_PER_HOUR,
MAX_REQUESTS_PER_DAY=$MAX_REQUESTS_PER_DAY,
MAX_DAILY_COST_PER_USER=$MAX_DAILY_COST_PER_USER,
ENABLE_RATE_LIMITING=true,
USE_FIRESTORE_RATE_LIMIT=true,
GCP_PROJECT_ID=$GCP_PROJECT_ID
" \
  --service-account=$SA_EMAIL \
  --project=$GCP_PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe clible-web \
  --region=$REGION \
  --project=$GCP_PROJECT_ID \
  --format='value(status.url)')

# Create budget alert (optional)
echo ""
read -p "Set up budget alert? (y/n): " SETUP_BUDGET
if [ "$SETUP_BUDGET" = "y" ]; then
    read -p "Enter monthly budget in USD (e.g., 50): " BUDGET_AMOUNT
    
    BILLING_ACCOUNT=$(gcloud billing projects describe $GCP_PROJECT_ID --format='value(billingAccountName)' | sed 's/.*\///')
    
    if [ -n "$BILLING_ACCOUNT" ]; then
        gcloud billing budgets create \
          --billing-account=$BILLING_ACCOUNT \
          --display-name="clible Monthly Budget" \
          --budget-amount=$BUDGET_AMOUNT \
          --threshold-rule=percent=50 \
          --threshold-rule=percent=90 \
          --threshold-rule=percent=100 \
          --project=$GCP_PROJECT_ID 2>/dev/null || echo "   Budget already exists"
        echo "✅ Budget alert created: \$$BUDGET_AMOUNT/month"
    else
        echo "⚠️  Could not find billing account. Set up budget manually in GCP Console."
    fi
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📊 Monitoring:"
echo "   Logs: gcloud logging tail 'resource.type=cloud_run_revision' --project=$GCP_PROJECT_ID"
echo "   Metrics: https://console.cloud.google.com/run/detail/$REGION/clible-web/metrics?project=$GCP_PROJECT_ID"
echo ""
echo "📝 To map a custom domain:"
echo "   gcloud run domain-mappings create --service=clible-web --domain=bible.yourdomain.com --region=$REGION --project=$GCP_PROJECT_ID"
echo ""
echo "💾 Save these values to .env:"
cat > .env.production << EOF
GCP_PROJECT_ID=$GCP_PROJECT_ID
GCP_REGION=$REGION
CLIBLE_GCP_ARTIFACT_REGISTRY=$REGISTRY
CLIBLE_GCS_BUCKET=$BUCKET
GEMINI_API_KEY=$GEMINI_API_KEY
SESSION_SECRET=$SESSION_SECRET
MAX_REQUESTS_PER_HOUR=$MAX_REQUESTS_PER_HOUR
MAX_REQUESTS_PER_DAY=$MAX_REQUESTS_PER_DAY
MAX_DAILY_COST_PER_USER=$MAX_DAILY_COST_PER_USER
SERVICE_URL=$SERVICE_URL
EOF
echo "   Saved to .env.production"
echo ""
echo "🔍 Test your deployment:"
echo "   curl $SERVICE_URL/health"
echo ""
echo "📈 View usage statistics:"
echo "   curl $SERVICE_URL/api/usage"
