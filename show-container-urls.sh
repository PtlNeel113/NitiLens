#!/bin/bash

# Show Container Image URLs for NitiLens

echo ""
echo "🐳 NitiLens Container Image URLs"
echo "================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed"
    echo "Please install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ No GCP project configured"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    echo ""
    echo "Or use the template URLs below:"
    echo ""
    echo "Backend:  asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/backend:latest"
    echo "Frontend: asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/frontend:latest"
    echo ""
    exit 1
fi

echo "📋 Project ID: $PROJECT_ID"
echo ""

# Configuration
REGION="asia-south1"
REPO_NAME="nitilens"

# Backend URL
BACKEND_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest"
echo "🔧 Backend Container Image:"
echo "   $BACKEND_URL"
echo ""

# Frontend URL
FRONTEND_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest"
echo "🎨 Frontend Container Image:"
echo "   $FRONTEND_URL"
echo ""

# Check if repository exists
echo "📦 Checking Artifact Registry..."
if gcloud artifacts repositories describe $REPO_NAME --location=$REGION &>/dev/null; then
    echo "   ✅ Repository exists"
    
    # List backend images
    echo ""
    echo "🔍 Backend Images:"
    if gcloud artifacts docker images list "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend" --format="table(package,version,create_time)" 2>/dev/null; then
        :
    else
        echo "   ⚠️  No backend images found. Run: cd backend && gcloud builds submit"
    fi
    
    # List frontend images
    echo ""
    echo "🔍 Frontend Images:"
    if gcloud artifacts docker images list "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend" --format="table(package,version,create_time)" 2>/dev/null; then
        :
    else
        echo "   ⚠️  No frontend images found. Run: gcloud builds submit --config=cloudbuild-frontend.yaml"
    fi
    
else
    echo "   ⚠️  Repository not found"
    echo ""
    echo "Create repository with:"
    echo "   gcloud artifacts repositories create $REPO_NAME --repository-format=docker --location=$REGION"
fi

echo ""
echo "================================="
echo ""
echo "📝 Quick Commands:"
echo ""
echo "Build Backend:"
echo "   cd backend"
echo "   gcloud builds submit --tag $BACKEND_URL"
echo ""
echo "Build Frontend:"
echo "   gcloud builds submit --tag $FRONTEND_URL -f Dockerfile.frontend"
echo ""
echo "Deploy Backend:"
echo "   gcloud run deploy nitilens-backend --image $BACKEND_URL --region $REGION"
echo ""
echo "Deploy Frontend:"
echo "   gcloud run deploy nitilens-frontend --image $FRONTEND_URL --region $REGION"
echo ""
echo "Pull Locally:"
echo "   gcloud auth configure-docker $REGION-docker.pkg.dev"
echo "   docker pull $BACKEND_URL"
echo "   docker pull $FRONTEND_URL"
echo ""
