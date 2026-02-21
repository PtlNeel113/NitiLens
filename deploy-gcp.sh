#!/bin/bash

# NitiLens GCP Deployment Script
# This script deploys NitiLens to Google Cloud Platform

set -e

echo "🚀 NitiLens GCP Deployment Script"
echo "=================================="

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
    exit 1
fi

echo "📋 Project ID: $PROJECT_ID"

# Configuration
REGION="asia-south1"
REPO_NAME="nitilens"
BACKEND_SERVICE="nitilens-backend"
FRONTEND_SERVICE="nitilens-frontend"
DB_INSTANCE="nitilens-db"

echo ""
echo "Configuration:"
echo "  Region: $REGION"
echo "  Repository: $REPO_NAME"
echo "  Backend Service: $BACKEND_SERVICE"
echo "  Frontend Service: $FRONTEND_SERVICE"
echo "  Database Instance: $DB_INSTANCE"
echo ""

# Ask for confirmation
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
fi

# Step 1: Enable APIs
echo ""
echo "📦 Step 1: Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
echo "✅ APIs enabled"

# Step 2: Create Artifact Registry
echo ""
echo "📦 Step 2: Creating Artifact Registry repository..."
if gcloud artifacts repositories describe $REPO_NAME --location=$REGION &>/dev/null; then
    echo "Repository already exists"
else
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="NitiLens Docker images"
    echo "✅ Repository created"
fi

# Step 3: Check Cloud SQL
echo ""
echo "🗄️  Step 3: Checking Cloud SQL instance..."
if gcloud sql instances describe $DB_INSTANCE &>/dev/null; then
    echo "Database instance already exists"
else
    echo "⚠️  Database instance not found"
    echo "Creating Cloud SQL instance (this takes 5-10 minutes)..."
    
    read -sp "Enter database root password: " DB_PASSWORD
    echo
    
    gcloud sql instances create $DB_INSTANCE \
        --database-version=POSTGRES_14 \
        --tier=db-f1-micro \
        --region=$REGION \
        --root-password=$DB_PASSWORD \
        --storage-type=SSD \
        --storage-size=10GB \
        --backup \
        --backup-start-time=03:00
    
    echo "✅ Database instance created"
    
    # Create database
    gcloud sql databases create nitilens --instance=$DB_INSTANCE
    
    # Create user
    gcloud sql users create nitilens_user \
        --instance=$DB_INSTANCE \
        --password=$DB_PASSWORD
    
    echo "✅ Database and user created"
fi

# Step 4: Configure secrets
echo ""
echo "🔐 Step 4: Configuring secrets..."

# Database URL
DB_URL="postgresql://nitilens_user:CHANGE_PASSWORD@/nitilens?host=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE"
if gcloud secrets describe database-url &>/dev/null; then
    echo "database-url secret already exists"
else
    echo -n "$DB_URL" | gcloud secrets create database-url --data-file=-
    echo "✅ database-url secret created"
fi

# JWT Secret
if gcloud secrets describe jwt-secret &>/dev/null; then
    echo "jwt-secret already exists"
else
    JWT_SECRET=$(openssl rand -hex 32)
    echo -n "$JWT_SECRET" | gcloud secrets create jwt-secret --data-file=-
    echo "✅ jwt-secret created"
fi

# Grant access to secrets
SERVICE_ACCOUNT="$PROJECT_ID@appspot.gserviceaccount.com"
gcloud secrets add-iam-policy-binding database-url \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" &>/dev/null
gcloud secrets add-iam-policy-binding jwt-secret \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" &>/dev/null
echo "✅ Secret access configured"

# Step 5: Deploy Backend
echo ""
echo "🚀 Step 5: Deploying backend..."
cd backend
gcloud builds submit --config=cloudbuild.yaml
cd ..
echo "✅ Backend deployed"

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')
echo "Backend URL: $BACKEND_URL"

# Step 6: Deploy Frontend
echo ""
echo "🚀 Step 6: Deploying frontend..."
# Update frontend cloudbuild with backend URL
sed -i.bak "s|_BACKEND_URL:.*|_BACKEND_URL: $BACKEND_URL|" cloudbuild-frontend.yaml
gcloud builds submit --config=cloudbuild-frontend.yaml
echo "✅ Frontend deployed"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)')
echo "Frontend URL: $FRONTEND_URL"

# Step 7: Update CORS
echo ""
echo "🔧 Step 7: Updating CORS configuration..."
gcloud run services update $BACKEND_SERVICE \
    --region=$REGION \
    --set-env-vars CORS_ORIGINS=$FRONTEND_URL
echo "✅ CORS updated"

# Summary
echo ""
echo "=================================="
echo "✅ Deployment Complete!"
echo "=================================="
echo ""
echo "🌐 Application URLs:"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend:  $BACKEND_URL"
echo ""
echo "📊 Next Steps:"
echo "  1. Initialize database: gcloud sql connect $DB_INSTANCE --user=nitilens_user"
echo "  2. Run migrations and seed data"
echo "  3. Test the application"
echo "  4. Configure custom domain (optional)"
echo ""
echo "📝 View logs:"
echo "  Backend:  gcloud run services logs read $BACKEND_SERVICE --region=$REGION"
echo "  Frontend: gcloud run services logs read $FRONTEND_SERVICE --region=$REGION"
echo ""
echo "💰 Estimated monthly cost: ~$40-50 (development tier)"
echo ""
