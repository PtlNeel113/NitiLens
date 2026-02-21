# NitiLens GCP Deployment Script (PowerShell)
# This script deploys NitiLens to Google Cloud Platform

$ErrorActionPreference = "Stop"

Write-Host "🚀 NitiLens GCP Deployment Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
try {
    $null = gcloud version
} catch {
    Write-Host "❌ gcloud CLI is not installed" -ForegroundColor Red
    Write-Host "Please install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Get project ID
$PROJECT_ID = gcloud config get-value project 2>$null
if ([string]::IsNullOrEmpty($PROJECT_ID)) {
    Write-Host "❌ No GCP project configured" -ForegroundColor Red
    Write-Host "Run: gcloud config set project YOUR_PROJECT_ID" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Project ID: $PROJECT_ID" -ForegroundColor Green

# Configuration
$REGION = "asia-south1"
$REPO_NAME = "nitilens"
$BACKEND_SERVICE = "nitilens-backend"
$FRONTEND_SERVICE = "nitilens-frontend"
$DB_INSTANCE = "nitilens-db"

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Region: $REGION"
Write-Host "  Repository: $REPO_NAME"
Write-Host "  Backend Service: $BACKEND_SERVICE"
Write-Host "  Frontend Service: $FRONTEND_SERVICE"
Write-Host "  Database Instance: $DB_INSTANCE"
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Continue with deployment? (y/n)"
if ($confirmation -ne 'y') {
    Write-Host "Deployment cancelled" -ForegroundColor Yellow
    exit 0
}

# Step 1: Enable APIs
Write-Host ""
Write-Host "📦 Step 1: Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
Write-Host "✅ APIs enabled" -ForegroundColor Green

# Step 2: Create Artifact Registry
Write-Host ""
Write-Host "📦 Step 2: Creating Artifact Registry repository..." -ForegroundColor Cyan
try {
    gcloud artifacts repositories describe $REPO_NAME --location=$REGION 2>$null
    Write-Host "Repository already exists" -ForegroundColor Yellow
} catch {
    gcloud artifacts repositories create $REPO_NAME `
        --repository-format=docker `
        --location=$REGION `
        --description="NitiLens Docker images"
    Write-Host "✅ Repository created" -ForegroundColor Green
}

# Step 3: Check Cloud SQL
Write-Host ""
Write-Host "🗄️  Step 3: Checking Cloud SQL instance..." -ForegroundColor Cyan
try {
    gcloud sql instances describe $DB_INSTANCE 2>$null
    Write-Host "Database instance already exists" -ForegroundColor Yellow
} catch {
    Write-Host "⚠️  Database instance not found" -ForegroundColor Yellow
    Write-Host "Creating Cloud SQL instance (this takes 5-10 minutes)..." -ForegroundColor Cyan
    
    $DB_PASSWORD = Read-Host "Enter database root password" -AsSecureString
    $DB_PASSWORD_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($DB_PASSWORD)
    )
    
    gcloud sql instances create $DB_INSTANCE `
        --database-version=POSTGRES_14 `
        --tier=db-f1-micro `
        --region=$REGION `
        --root-password=$DB_PASSWORD_PLAIN `
        --storage-type=SSD `
        --storage-size=10GB `
        --backup `
        --backup-start-time=03:00
    
    Write-Host "✅ Database instance created" -ForegroundColor Green
    
    # Create database
    gcloud sql databases create nitilens --instance=$DB_INSTANCE
    
    # Create user
    gcloud sql users create nitilens_user `
        --instance=$DB_INSTANCE `
        --password=$DB_PASSWORD_PLAIN
    
    Write-Host "✅ Database and user created" -ForegroundColor Green
}

# Step 4: Configure secrets
Write-Host ""
Write-Host "🔐 Step 4: Configuring secrets..." -ForegroundColor Cyan

# Database URL
$DB_URL = "postgresql://nitilens_user:CHANGE_PASSWORD@/nitilens?host=/cloudsql/$PROJECT_ID`:$REGION`:$DB_INSTANCE"
try {
    gcloud secrets describe database-url 2>$null
    Write-Host "database-url secret already exists" -ForegroundColor Yellow
} catch {
    $DB_URL | gcloud secrets create database-url --data-file=-
    Write-Host "✅ database-url secret created" -ForegroundColor Green
}

# JWT Secret
try {
    gcloud secrets describe jwt-secret 2>$null
    Write-Host "jwt-secret already exists" -ForegroundColor Yellow
} catch {
    $JWT_SECRET = -join ((48..57) + (97..102) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    $JWT_SECRET | gcloud secrets create jwt-secret --data-file=-
    Write-Host "✅ jwt-secret created" -ForegroundColor Green
}

# Grant access to secrets
$SERVICE_ACCOUNT = "$PROJECT_ID@appspot.gserviceaccount.com"
gcloud secrets add-iam-policy-binding database-url `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/secretmanager.secretAccessor" 2>$null
gcloud secrets add-iam-policy-binding jwt-secret `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/secretmanager.secretAccessor" 2>$null
Write-Host "✅ Secret access configured" -ForegroundColor Green

# Step 5: Deploy Backend
Write-Host ""
Write-Host "🚀 Step 5: Deploying backend..." -ForegroundColor Cyan
Push-Location backend
gcloud builds submit --config=cloudbuild.yaml
Pop-Location
Write-Host "✅ Backend deployed" -ForegroundColor Green

# Get backend URL
$BACKEND_URL = gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)'
Write-Host "Backend URL: $BACKEND_URL" -ForegroundColor Green

# Step 6: Deploy Frontend
Write-Host ""
Write-Host "🚀 Step 6: Deploying frontend..." -ForegroundColor Cyan
# Update frontend cloudbuild with backend URL
(Get-Content cloudbuild-frontend.yaml) -replace '_BACKEND_URL:.*', "_BACKEND_URL: $BACKEND_URL" | Set-Content cloudbuild-frontend.yaml
gcloud builds submit --config=cloudbuild-frontend.yaml
Write-Host "✅ Frontend deployed" -ForegroundColor Green

# Get frontend URL
$FRONTEND_URL = gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)'
Write-Host "Frontend URL: $FRONTEND_URL" -ForegroundColor Green

# Step 7: Update CORS
Write-Host ""
Write-Host "🔧 Step 7: Updating CORS configuration..." -ForegroundColor Cyan
gcloud run services update $BACKEND_SERVICE `
    --region=$REGION `
    --set-env-vars CORS_ORIGINS=$FRONTEND_URL
Write-Host "✅ CORS updated" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Application URLs:" -ForegroundColor Cyan
Write-Host "  Frontend: $FRONTEND_URL" -ForegroundColor White
Write-Host "  Backend:  $BACKEND_URL" -ForegroundColor White
Write-Host ""
Write-Host "📊 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Initialize database: gcloud sql connect $DB_INSTANCE --user=nitilens_user"
Write-Host "  2. Run migrations and seed data"
Write-Host "  3. Test the application"
Write-Host "  4. Configure custom domain (optional)"
Write-Host ""
Write-Host "📝 View logs:" -ForegroundColor Cyan
Write-Host "  Backend:  gcloud run services logs read $BACKEND_SERVICE --region=$REGION"
Write-Host "  Frontend: gcloud run services logs read $FRONTEND_SERVICE --region=$REGION"
Write-Host ""
Write-Host "💰 Estimated monthly cost: ~`$40-50 (development tier)" -ForegroundColor Yellow
Write-Host ""
