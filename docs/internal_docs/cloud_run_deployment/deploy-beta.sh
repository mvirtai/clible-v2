#!/bin/bash
# Minimal Cloud Run deployment for beta testing with Gemini API rate limits

set -euo pipefail

echo "🚀 clible-v2 Beta Testing Deployment (Cloud Run)"
echo "================================================"
echo ""

# Check prerequisites
command -v gcloud >/dev/null 2>&1 || { echo "❌ gcloud CLI required. Install: https://cloud.google.com/sdk/docs/install"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required. Install: https://docs.docker.com/get-docker/"; exit 1; }

# Get project ID
if [ -z "${GCP_PROJECT_ID:-}" ]; then
    read -p "Enter GCP Project ID: " GCP_PROJECT_ID
    export GCP_PROJECT_ID
fi

REGION="${GCP_REGION:-europe-north1}"

echo "📋 Configuration:"
echo "   Project: $GCP_PROJECT_ID"
echo "   Region: $REGION"
echo ""

# Enable APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  --project=$GCP_PROJECT_ID

# Create Artifact Registry
echo "📦 Setting up Artifact Registry..."
gcloud artifacts repositories create clible \
  --repository-format=docker \
  --location=$REGION \
  --description="clible-v2 container images" \
  --project=$GCP_PROJECT_ID 2>/dev/null || echo "   Repository exists"

REGISTRY="$REGION-docker.pkg.dev/$GCP_PROJECT_ID/clible"

# Configure Docker
echo "🐳 Configuring Docker..."
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

# Get secrets
if [ -z "${GEMINI_API_KEY:-}" ]; then
    read -sp "Enter Gemini API Key: " GEMINI_API_KEY
    echo ""
    export GEMINI_API_KEY
fi

if [ -z "${SESSION_SECRET:-}" ]; then
    SESSION_SECRET=$(openssl rand -hex 32)
    export SESSION_SECRET
fi

# Rate limits
MAX_REQUESTS_PER_HOUR="${MAX_REQUESTS_PER_HOUR:-20}"

echo ""
echo "⚙️  Rate Limiting:"
echo "   Max AI requests per hour: $MAX_REQUESTS_PER_HOUR"
echo ""

# Build and push
echo "🏗️  Building web image..."
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
  --max-instances=3 \
  --concurrency=80 \
  --timeout=60 \
  --set-env-vars="GEMINI_API_KEY=$GEMINI_API_KEY,SESSION_SECRET=$SESSION_SECRET,NODE_ENV=production,MAX_REQUESTS_PER_HOUR=$MAX_REQUESTS_PER_HOUR" \
  --project=$GCP_PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe clible-web \
  --region=$REGION \
  --project=$GCP_PROJECT_ID \
  --format='value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "💾 Save to .env.production:"
cat > .env.production << EOF
GCP_PROJECT_ID=$GCP_PROJECT_ID
GCP_REGION=$REGION
CLIBLE_GCP_ARTIFACT_REGISTRY=$REGISTRY
GEMINI_API_KEY=$GEMINI_API_KEY
SESSION_SECRET=$SESSION_SECRET
MAX_REQUESTS_PER_HOUR=$MAX_REQUESTS_PER_HOUR
SERVICE_URL=$SERVICE_URL
EOF
echo "   Saved to .env.production"
echo ""
echo "🔍 Test deployment:"
echo "   curl $SERVICE_URL"
echo ""
echo "📊 View logs:"
echo "   gcloud run services logs read clible-web --region=$REGION --project=$GCP_PROJECT_ID"
