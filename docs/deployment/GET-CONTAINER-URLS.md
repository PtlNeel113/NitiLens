# How to Find Your Container Image URLs

## Quick Commands

### Get Your Project ID
```bash
gcloud config get-value project
```

### List All Container Images
```bash
# List backend images
gcloud artifacts docker images list asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/backend

# List frontend images
gcloud artifacts docker images list asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/frontend
```

### Get Latest Image URLs
```bash
# Backend latest image
echo "asia-south1-docker.pkg.dev/$(gcloud config get-value project)/nitilens/backend:latest"

# Frontend latest image
echo "asia-south1-docker.pkg.dev/$(gcloud config get-value project)/nitilens/frontend:latest"
```

## Container Image URL Structure

```
[REGION]-docker.pkg.dev/[PROJECT_ID]/[REPOSITORY]/[IMAGE]:[TAG]
```

### Components:

1. **REGION**: `asia-south1` (Mumbai, India)
2. **PROJECT_ID**: Your GCP project ID (e.g., `my-project-123456`)
3. **REPOSITORY**: `nitilens` (our Artifact Registry repository)
4. **IMAGE**: `backend` or `frontend`
5. **TAG**: `latest` or specific commit SHA (e.g., `abc123`)

## Example URLs

If your project ID is `nitilens-prod-2026`, your URLs would be:

### Backend:
```
asia-south1-docker.pkg.dev/nitilens-prod-2026/nitilens/backend:latest
```

### Frontend:
```
asia-south1-docker.pkg.dev/nitilens-prod-2026/nitilens/frontend:latest
```

## PowerShell Commands (Windows)

```powershell
# Get project ID
$PROJECT_ID = gcloud config get-value project

# Display backend URL
Write-Host "Backend Image URL:"
Write-Host "asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/backend:latest"

# Display frontend URL
Write-Host "`nFrontend Image URL:"
Write-Host "asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/frontend:latest"

# List all images
Write-Host "`nAll Backend Images:"
gcloud artifacts docker images list "asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/backend"

Write-Host "`nAll Frontend Images:"
gcloud artifacts docker images list "asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/frontend"
```

## Bash Commands (Linux/Mac)

```bash
# Get project ID
PROJECT_ID=$(gcloud config get-value project)

# Display backend URL
echo "Backend Image URL:"
echo "asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/backend:latest"

# Display frontend URL
echo ""
echo "Frontend Image URL:"
echo "asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/frontend:latest"

# List all images
echo ""
echo "All Backend Images:"
gcloud artifacts docker images list "asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/backend"

echo ""
echo "All Frontend Images:"
gcloud artifacts docker images list "asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/frontend"
```

## View in GCP Console

1. Go to: https://console.cloud.google.com/artifacts
2. Select your project
3. Click on `nitilens` repository
4. You'll see both `backend` and `frontend` images
5. Click on an image to see all tags and their URLs

## Using the URLs

### Deploy to Cloud Run

```bash
# Deploy backend
gcloud run deploy nitilens-backend \
  --image asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/backend:latest \
  --region asia-south1 \
  --platform managed

# Deploy frontend
gcloud run deploy nitilens-frontend \
  --image asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/frontend:latest \
  --region asia-south1 \
  --platform managed
```

### Pull Image Locally

```bash
# Authenticate Docker
gcloud auth configure-docker asia-south1-docker.pkg.dev

# Pull backend image
docker pull asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/backend:latest

# Pull frontend image
docker pull asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/frontend:latest
```

### Run Locally

```bash
# Run backend container
docker run -p 8000:8000 \
  -e DATABASE_URL="your-db-url" \
  -e JWT_SECRET_KEY="your-secret" \
  asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/backend:latest

# Run frontend container
docker run -p 80:80 \
  asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/frontend:latest
```

## Image Tags

### Available Tags:

1. **latest** - Most recent build
2. **[commit-sha]** - Specific commit (e.g., `abc123f`)
3. **v1.0.0** - Version tags (if you create them)

### List All Tags for an Image:

```bash
# Backend tags
gcloud artifacts docker tags list \
  asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/backend

# Frontend tags
gcloud artifacts docker tags list \
  asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/frontend
```

## Troubleshooting

### Error: "Repository not found"

```bash
# Create the repository
gcloud artifacts repositories create nitilens \
  --repository-format=docker \
  --location=asia-south1 \
  --description="NitiLens Docker images"
```

### Error: "Permission denied"

```bash
# Authenticate
gcloud auth login
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

### Error: "Image not found"

```bash
# Build and push the image first
cd backend
gcloud builds submit --tag asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/backend
```

## Quick Reference

| Component | Value |
|-----------|-------|
| Registry | `asia-south1-docker.pkg.dev` |
| Project ID | `YOUR_PROJECT_ID` (replace with actual) |
| Repository | `nitilens` |
| Backend Image | `backend` |
| Frontend Image | `frontend` |
| Default Tag | `latest` |

## Complete URLs Template

Replace `YOUR_PROJECT_ID` with your actual GCP project ID:

```
Backend:  asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/backend:latest
Frontend: asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nitilens/frontend:latest
```

## Get URLs After Deployment

After running the deployment script, you can get the deployed image URLs:

```bash
# Get backend image
gcloud run services describe nitilens-backend \
  --region asia-south1 \
  --format='value(spec.template.spec.containers[0].image)'

# Get frontend image
gcloud run services describe nitilens-frontend \
  --region asia-south1 \
  --format='value(spec.template.spec.containers[0].image)'
```
