# NitiLens - Google Cloud Platform Deployment Guide

## Prerequisites

### 1. Install Google Cloud SDK

**Windows**:
```powershell
# Download and install from:
# https://cloud.google.com/sdk/docs/install

# Or use PowerShell:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

**Linux/Mac**:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 2. Initialize gcloud

```bash
gcloud init
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## Architecture on GCP

```
┌─────────────────────────────────────────────────────────┐
│                   Cloud Load Balancer                    │
│                    (HTTPS/SSL)                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Cloud Run Services                    │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  Frontend        │      │  Backend API     │        │
│  │  (React/Nginx)   │      │  (FastAPI)       │        │
│  │  Auto-scaling    │      │  Auto-scaling    │        │
│  └──────────────────┘      └──────────────────┘        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Cloud SQL (PostgreSQL)                      │
│  - Automatic backups                                     │
│  - High availability                                     │
│  - Private IP                                            │
└─────────────────────────────────────────────────────────┘
```

## Step-by-Step Deployment

### Step 1: Set Environment Variables

```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="asia-south1"
export REPO_NAME="nitilens"
export BACKEND_SERVICE="nitilens-backend"
export FRONTEND_SERVICE="nitilens-frontend"
export DB_INSTANCE="nitilens-db"
```

### Step 2: Create Artifact Registry Repository

```bash
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="NitiLens Docker images"
```

### Step 3: Create Cloud SQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create $DB_INSTANCE \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=$REGION \
    --root-password=CHANGE_THIS_PASSWORD \
    --storage-type=SSD \
    --storage-size=10GB \
    --backup \
    --backup-start-time=03:00

# Create database
gcloud sql databases create nitilens --instance=$DB_INSTANCE

# Create user
gcloud sql users create nitilens_user \
    --instance=$DB_INSTANCE \
    --password=CHANGE_THIS_PASSWORD
```

### Step 4: Store Secrets in Secret Manager

```bash
# Database URL
echo -n "postgresql://nitilens_user:CHANGE_THIS_PASSWORD@/nitilens?host=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE" | \
    gcloud secrets create database-url --data-file=-

# JWT Secret
echo -n "$(openssl rand -hex 32)" | \
    gcloud secrets create jwt-secret --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding database-url \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding jwt-secret \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Step 5: Build and Deploy Backend

#### Create cloudbuild.yaml for Backend

Create `backend/cloudbuild.yaml`:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/backend:${SHORT_SHA}'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/backend:latest'
      - '-f'
      - 'Dockerfile'
      - '.'
    dir: 'backend'

  # Push the container image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '--all-tags'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/backend'

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${_SERVICE_NAME}'
      - '--image'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/backend:${SHORT_SHA}'
      - '--region'
      - '${_REGION}'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--add-cloudsql-instances'
      - '${PROJECT_ID}:${_REGION}:${_DB_INSTANCE}'
      - '--set-secrets'
      - 'DATABASE_URL=database-url:latest,JWT_SECRET_KEY=jwt-secret:latest'
      - '--set-env-vars'
      - 'ENVIRONMENT=production,CORS_ORIGINS=https://${_FRONTEND_URL}'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '2'
      - '--max-instances'
      - '10'
      - '--min-instances'
      - '1'

substitutions:
  _REGION: asia-south1
  _REPO_NAME: nitilens
  _SERVICE_NAME: nitilens-backend
  _DB_INSTANCE: nitilens-db
  _FRONTEND_URL: your-frontend-url.run.app

images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/backend:${SHORT_SHA}'
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/backend:latest'
```

#### Deploy Backend

```bash
cd backend
gcloud builds submit --config=cloudbuild.yaml
```

### Step 6: Build and Deploy Frontend

#### Create cloudbuild.yaml for Frontend

Create `cloudbuild-frontend.yaml`:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/frontend:${SHORT_SHA}'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/frontend:latest'
      - '-f'
      - 'Dockerfile.frontend'
      - '--build-arg'
      - 'VITE_API_URL=${_BACKEND_URL}'
      - '.'

  # Push the container image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '--all-tags'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/frontend'

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${_SERVICE_NAME}'
      - '--image'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/frontend:${SHORT_SHA}'
      - '--region'
      - '${_REGION}'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--memory'
      - '1Gi'
      - '--cpu'
      - '1'
      - '--max-instances'
      - '5'

substitutions:
  _REGION: asia-south1
  _REPO_NAME: nitilens
  _SERVICE_NAME: nitilens-frontend
  _BACKEND_URL: https://your-backend-url.run.app

images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/frontend:${SHORT_SHA}'
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/frontend:latest'
```

#### Deploy Frontend

```bash
gcloud builds submit --config=cloudbuild-frontend.yaml
```

### Step 7: Initialize Database

```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')

# Connect to Cloud SQL and run migrations
gcloud sql connect $DB_INSTANCE --user=nitilens_user

# In the SQL prompt:
\c nitilens

# Exit SQL prompt and run init script
# You'll need to exec into a Cloud Run instance or use Cloud Shell
```

### Step 8: Configure Custom Domain (Optional)

```bash
# Map custom domain to backend
gcloud run domain-mappings create \
    --service=$BACKEND_SERVICE \
    --domain=api.yourdomain.com \
    --region=$REGION

# Map custom domain to frontend
gcloud run domain-mappings create \
    --service=$FRONTEND_SERVICE \
    --domain=app.yourdomain.com \
    --region=$REGION
```

## Quick Deploy Commands

### One-Command Backend Deploy

```bash
cd backend
gcloud builds submit \
    --tag asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/backend \
    && gcloud run deploy nitilens-backend \
    --image asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/backend \
    --region asia-south1 \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances $PROJECT_ID:asia-south1:nitilens-db \
    --set-secrets DATABASE_URL=database-url:latest,JWT_SECRET_KEY=jwt-secret:latest \
    --memory 2Gi \
    --cpu 2
```

### One-Command Frontend Deploy

```bash
gcloud builds submit \
    --tag asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/frontend \
    -f Dockerfile.frontend \
    && gcloud run deploy nitilens-frontend \
    --image asia-south1-docker.pkg.dev/$PROJECT_ID/nitilens/frontend \
    --region asia-south1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi
```

## Environment Variables

### Backend Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE
JWT_SECRET_KEY=your-secret-key
ENVIRONMENT=production
CORS_ORIGINS=https://your-frontend-url.run.app
```

### Frontend Environment Variables

```bash
VITE_API_URL=https://your-backend-url.run.app
```

## Monitoring & Logging

### View Logs

```bash
# Backend logs
gcloud run services logs read $BACKEND_SERVICE --region=$REGION --limit=50

# Frontend logs
gcloud run services logs read $FRONTEND_SERVICE --region=$REGION --limit=50
```

### View Metrics

```bash
# Open Cloud Console
gcloud run services describe $BACKEND_SERVICE --region=$REGION
```

### Set Up Alerts

```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="High Error Rate" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=0.05 \
    --condition-threshold-duration=300s
```

## Scaling Configuration

### Auto-Scaling Settings

```bash
# Update backend scaling
gcloud run services update $BACKEND_SERVICE \
    --region=$REGION \
    --min-instances=1 \
    --max-instances=10 \
    --concurrency=80

# Update frontend scaling
gcloud run services update $FRONTEND_SERVICE \
    --region=$REGION \
    --min-instances=0 \
    --max-instances=5 \
    --concurrency=100
```

## Cost Optimization

### Estimated Monthly Costs

**Development Environment**:
- Cloud Run (Backend): ~$20/month (1 instance, low traffic)
- Cloud Run (Frontend): ~$10/month (0-1 instances)
- Cloud SQL (db-f1-micro): ~$10/month
- **Total: ~$40/month**

**Production Environment**:
- Cloud Run (Backend): ~$100-200/month (1-5 instances)
- Cloud Run (Frontend): ~$50/month (1-3 instances)
- Cloud SQL (db-n1-standard-1): ~$50/month
- Cloud Build: ~$20/month
- **Total: ~$220-320/month**

### Cost Reduction Tips

1. **Use minimum instances = 0** for non-critical services
2. **Enable Cloud SQL automatic backups** only for production
3. **Use Cloud Build triggers** instead of manual builds
4. **Set up budget alerts** at $100, $200, $300
5. **Use preemptible instances** for background jobs

## CI/CD with Cloud Build Triggers

### Set Up Automatic Deployment

```bash
# Create trigger for backend
gcloud builds triggers create github \
    --repo-name=NitiLens \
    --repo-owner=PtlNeel113 \
    --branch-pattern="^main$" \
    --build-config=backend/cloudbuild.yaml \
    --included-files="backend/**"

# Create trigger for frontend
gcloud builds triggers create github \
    --repo-name=NitiLens \
    --repo-owner=PtlNeel113 \
    --branch-pattern="^main$" \
    --build-config=cloudbuild-frontend.yaml \
    --included-files="src/**,index.html,package.json"
```

## Troubleshooting

### Common Issues

**1. Cloud SQL Connection Failed**
```bash
# Check Cloud SQL instance status
gcloud sql instances describe $DB_INSTANCE

# Verify Cloud Run has Cloud SQL connection
gcloud run services describe $BACKEND_SERVICE --region=$REGION | grep cloudsql
```

**2. Secret Access Denied**
```bash
# Grant access to secrets
gcloud secrets add-iam-policy-binding database-url \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

**3. CORS Errors**
```bash
# Update CORS_ORIGINS environment variable
gcloud run services update $BACKEND_SERVICE \
    --region=$REGION \
    --set-env-vars CORS_ORIGINS=https://your-frontend-url.run.app
```

**4. Out of Memory**
```bash
# Increase memory
gcloud run services update $BACKEND_SERVICE \
    --region=$REGION \
    --memory 4Gi
```

## Security Best Practices

1. **Use Secret Manager** for sensitive data
2. **Enable Cloud Armor** for DDoS protection
3. **Set up VPC** for private networking
4. **Enable Cloud SQL SSL** connections
5. **Use IAM roles** for least privilege access
6. **Enable audit logging** for compliance
7. **Set up Cloud KMS** for encryption keys

## Backup & Disaster Recovery

### Automated Backups

```bash
# Enable automated backups
gcloud sql instances patch $DB_INSTANCE \
    --backup-start-time=03:00 \
    --retained-backups-count=7

# Create on-demand backup
gcloud sql backups create --instance=$DB_INSTANCE
```

### Restore from Backup

```bash
# List backups
gcloud sql backups list --instance=$DB_INSTANCE

# Restore from backup
gcloud sql backups restore BACKUP_ID \
    --backup-instance=$DB_INSTANCE \
    --backup-id=BACKUP_ID
```

## Production Checklist

- [ ] Enable Cloud SQL automated backups
- [ ] Set up Cloud Monitoring alerts
- [ ] Configure custom domain with SSL
- [ ] Enable Cloud Armor for DDoS protection
- [ ] Set up Cloud Build triggers for CI/CD
- [ ] Configure budget alerts
- [ ] Enable audit logging
- [ ] Set up error reporting
- [ ] Configure uptime checks
- [ ] Document runbooks for incidents

## Support

For issues or questions:
- GitHub: https://github.com/PtlNeel113/NitiLens
- GCP Documentation: https://cloud.google.com/run/docs
- Cloud SQL: https://cloud.google.com/sql/docs
