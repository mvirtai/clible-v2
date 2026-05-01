#!/bin/bash
# Quick deployment script for clible-v2 web app

set -euo pipefail

echo "🚀 clible-v2 Cloud Deployment Setup"
echo "===================================="
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

# Grant storage permissions
echo "🔐 Granting permissions..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectAdmin" \
  --project=$GCP_PROJECT_ID >/dev/null

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
  --set-env-vars="GEMINI_API_KEY=$GEMINI_API_KEY,SESSION_SECRET=$SESSION_SECRET,NODE_ENV=production,CLIBLE_GCS_BUCKET=$BUCKET" \
  --service-account=$SA_EMAIL \
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
echo "📝 To map a custom domain:"
echo "   gcloud run domain-mappings create --service=clible-web --domain=bible.yourdomain.com --region=$REGION --project=$GCP_PROJECT_ID"
echo ""
echo "💾 Save these values to .env:"
echo "   GCP_PROJECT_ID=$GCP_PROJECT_ID"
echo "   CLIBLE_GCP_ARTIFACT_REGISTRY=$REGISTRY"
echo "   CLIBLE_GCS_BUCKET=$BUCKET"
echo "   GEMINI_API_KEY=$GEMINI_API_KEY"
echo "   SESSION_SECRET=$SESSION_SECRET"
