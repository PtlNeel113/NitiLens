# Show Container Image URLs for NitiLens

Write-Host ""
Write-Host "🐳 NitiLens Container Image URLs" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
try {
    $null = gcloud version 2>$null
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
    Write-Host ""
    Write-Host "Or use the template URLs below:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Backend:  asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/backend:latest" -ForegroundColor White
    Write-Host "Frontend: asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/frontend:latest" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "📋 Project ID: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Configuration
$REGION = "asia-south1"
$REPO_NAME = "nitilens"

# Backend URL
$BACKEND_URL = "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest"
Write-Host "🔧 Backend Container Image:" -ForegroundColor Cyan
Write-Host "   $BACKEND_URL" -ForegroundColor White
Write-Host ""

# Frontend URL
$FRONTEND_URL = "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest"
Write-Host "🎨 Frontend Container Image:" -ForegroundColor Cyan
Write-Host "   $FRONTEND_URL" -ForegroundColor White
Write-Host ""

# Check if repository exists
Write-Host "📦 Checking Artifact Registry..." -ForegroundColor Cyan
try {
    gcloud artifacts repositories describe $REPO_NAME --location=$REGION 2>$null | Out-Null
    Write-Host "   ✅ Repository exists" -ForegroundColor Green
    
    # List backend images
    Write-Host ""
    Write-Host "🔍 Backend Images:" -ForegroundColor Cyan
    $backendImages = gcloud artifacts docker images list "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend" --format="table(package,version,create_time)" 2>$null
    if ($backendImages) {
        Write-Host $backendImages
    } else {
        Write-Host "   ⚠️  No backend images found. Run: cd backend && gcloud builds submit" -ForegroundColor Yellow
    }
    
    # List frontend images
    Write-Host ""
    Write-Host "🔍 Frontend Images:" -ForegroundColor Cyan
    $frontendImages = gcloud artifacts docker images list "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend" --format="table(package,version,create_time)" 2>$null
    if ($frontendImages) {
        Write-Host $frontendImages
    } else {
        Write-Host "   ⚠️  No frontend images found. Run: gcloud builds submit --config=cloudbuild-frontend.yaml" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "   ⚠️  Repository not found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Create repository with:" -ForegroundColor Cyan
    Write-Host "   gcloud artifacts repositories create $REPO_NAME --repository-format=docker --location=$REGION" -ForegroundColor White
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Quick Commands:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Build Backend:" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   gcloud builds submit --tag $BACKEND_URL" -ForegroundColor White
Write-Host ""
Write-Host "Build Frontend:" -ForegroundColor Yellow
Write-Host "   gcloud builds submit --tag $FRONTEND_URL -f Dockerfile.frontend" -ForegroundColor White
Write-Host ""
Write-Host "Deploy Backend:" -ForegroundColor Yellow
Write-Host "   gcloud run deploy nitilens-backend --image $BACKEND_URL --region $REGION" -ForegroundColor White
Write-Host ""
Write-Host "Deploy Frontend:" -ForegroundColor Yellow
Write-Host "   gcloud run deploy nitilens-frontend --image $FRONTEND_URL --region $REGION" -ForegroundColor White
Write-Host ""
Write-Host "Pull Locally:" -ForegroundColor Yellow
Write-Host "   gcloud auth configure-docker $REGION-docker.pkg.dev" -ForegroundColor White
Write-Host "   docker pull $BACKEND_URL" -ForegroundColor White
Write-Host "   docker pull $FRONTEND_URL" -ForegroundColor White
Write-Host ""
