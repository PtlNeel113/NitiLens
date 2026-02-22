# 🚀 NitiLens — Google Cloud Deployment Guide

Deploy NitiLens AI Compliance Platform to **Google Cloud Platform** using Cloud Run, Cloud SQL, Artifact Registry, and Secret Manager.

---

## Prerequisites

### 1. Google Cloud Account & Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. **Enable billing** on the project (required for Cloud Run & Cloud SQL)
4. Note your **Project ID** (visible in the project selector dropdown)

### 2. Install Google Cloud CLI

Download and install from: https://cloud.google.com/sdk/docs/install

**Windows (recommended):** Download the installer `.exe` and run it.

After installation, verify:

```powershell
gcloud version
```

### 3. Authenticate & Configure

```powershell
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Verify configuration
gcloud config get-value project
```

### 4. Install Docker (Optional — for local testing)

If you want to test Docker builds locally before deploying:
- Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

## Deployment — Quick Start

The project includes an automated deployment script that handles everything.

### Run the Deployment Script

```powershell
# From the project root directory
.\deploy-gcp.ps1
```

**What the script does (7 steps):**

| Step | Action | Details |
|------|--------|---------|
| 1 | Enable APIs | Cloud Build, Cloud Run, Cloud SQL, Artifact Registry, Secret Manager |
| 2 | Artifact Registry | Creates Docker image repository in `asia-south1` |
| 3 | Cloud SQL | Creates PostgreSQL 14 instance (`db-f1-micro`) — takes 5-10 min |
| 4 | Secrets | Stores database URL and JWT secret in Secret Manager |
| 5 | Deploy Backend | Builds & deploys backend to Cloud Run via Cloud Build |
| 6 | Deploy Frontend | Builds & deploys frontend to Cloud Run with backend URL |
| 7 | CORS Update | Configures backend to accept requests from frontend URL |

> [!NOTE]
> First deployment takes ~15-20 minutes (mostly Cloud SQL creation). Subsequent deployments take ~5 minutes.

---

## Post-Deployment Steps

### 1. Initialize the Database

```powershell
# Connect to Cloud SQL
gcloud sql connect nitilens-db --user=nitilens_user --database=nitilens

# The backend container also runs init_db.py on startup, which creates tables automatically
```

### 2. Verify Services

```powershell
# Get service URLs
gcloud run services list --region=asia-south1

# Check backend health
$BACKEND_URL = gcloud run services describe nitilens-backend --region=asia-south1 --format='value(status.url)'
curl "$BACKEND_URL/health"

# Check frontend
$FRONTEND_URL = gcloud run services describe nitilens-frontend --region=asia-south1 --format='value(status.url)'
Write-Host "Frontend: $FRONTEND_URL"
```

### 3. View Logs

```powershell
# Backend logs
gcloud run services logs read nitilens-backend --region=asia-south1 --limit=50

# Frontend logs
gcloud run services logs read nitilens-frontend --region=asia-south1 --limit=50
```

### 4. Custom Domain (Optional)

```powershell
# Map a custom domain to the frontend
gcloud run domain-mappings create --service=nitilens-frontend --domain=app.nitilens.com --region=asia-south1

# Map a custom domain to the backend API
gcloud run domain-mappings create --service=nitilens-backend --domain=api.nitilens.com --region=asia-south1
```

---

## Redeployment (After Code Changes)

### Redeploy Backend Only

```powershell
cd backend
gcloud builds submit --config=cloudbuild.yaml
```

### Redeploy Frontend Only

```powershell
# Get the backend URL first
$BACKEND_URL = gcloud run services describe nitilens-backend --region=asia-south1 --format='value(status.url)'

# Update the cloudbuild file and deploy
(Get-Content cloudbuild-frontend.yaml) -replace '_BACKEND_URL:.*', "_BACKEND_URL: $BACKEND_URL" | Set-Content cloudbuild-frontend.yaml
gcloud builds submit --config=cloudbuild-frontend.yaml
```

### Redeploy Everything

```powershell
.\deploy-gcp.ps1
```

---

## Configuration Reference

### Default Settings

| Setting | Value |
|---------|-------|
| **Region** | `asia-south1` (Mumbai) |
| **Backend Memory** | 2 GiB |
| **Backend CPU** | 2 vCPUs |
| **Backend Instances** | 1–10 |
| **Frontend Memory** | 1 GiB |
| **Frontend CPU** | 1 vCPU |
| **Frontend Instances** | 0–5 |
| **Database** | PostgreSQL 14, `db-f1-micro` |
| **Estimated Cost** | ~$40-50/month (dev tier) |

### Environment Variables

The backend uses these env vars in production (set via Cloud Run):

| Variable | Source |
|----------|--------|
| `DATABASE_URL` | Secret Manager (`database-url`) |
| `JWT_SECRET_KEY` | Secret Manager (`jwt-secret`) |
| `ENVIRONMENT` | Set to `production` |
| `CORS_ORIGINS` | Set to frontend Cloud Run URL |

### To Add Additional Secrets

```powershell
# Create a new secret
echo "your-api-key-value" | gcloud secrets create MY_SECRET --data-file=-

# Grant access to Cloud Run service account
$SA = "$(gcloud config get-value project)@appspot.gserviceaccount.com"
gcloud secrets add-iam-policy-binding MY_SECRET --member="serviceAccount:$SA" --role="roles/secretmanager.secretAccessor"

# Update backend to use the secret
gcloud run services update nitilens-backend --region=asia-south1 --set-secrets="MY_ENV_VAR=MY_SECRET:latest"
```

---

## Troubleshooting

### "gcloud: command not found"
Install the Google Cloud CLI: https://cloud.google.com/sdk/docs/install

### Cloud Build fails
```powershell
# View build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

### Backend crashes on startup
- Check logs: `gcloud run services logs read nitilens-backend --region=asia-south1`
- Common issue: Database connection — ensure Cloud SQL instance is running and the secret `database-url` has the correct connection string

### Frontend shows "localhost:8000" errors
- The frontend was deployed without `VITE_API_URL` — redeploy the frontend with the correct backend URL (see Redeployment section above)

### CORS Errors
```powershell
# Update CORS origins
gcloud run services update nitilens-backend --region=asia-south1 --set-env-vars="CORS_ORIGINS=https://your-frontend-url.run.app"
```

### Reduce Costs
```powershell
# Set backend to scale to 0 (adds ~5-10s cold start)
gcloud run services update nitilens-backend --region=asia-south1 --min-instances=0

# Use a smaller DB tier
# Note: db-f1-micro is already the smallest tier

# Delete services when not needed
gcloud run services delete nitilens-frontend --region=asia-south1
gcloud run services delete nitilens-backend --region=asia-south1
gcloud sql instances delete nitilens-db
```

---

## Architecture on GCP

```
                    ┌─────────────────────┐
                    │   Cloud Run         │
    Users ────────► │   (Frontend)        │
                    │   nginx + React SPA │
                    └────────┬────────────┘
                             │ API calls
                             ▼
                    ┌─────────────────────┐      ┌──────────────┐
                    │   Cloud Run         │      │  Secret      │
                    │   (Backend)         │◄────►│  Manager     │
                    │   FastAPI + Uvicorn │      └──────────────┘
                    └────────┬────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │   Cloud SQL         │
                    │   (PostgreSQL 14)   │
                    └─────────────────────┘
```
