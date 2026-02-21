# 🚀 NitiLens Enterprise Deployment Guide

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (for local dev)
- Redis 7+ (for local dev)

### One-Command Deployment

```bash
chmod +x setup.sh
./setup.sh
```

Choose option 1 for Docker deployment (recommended) or option 2 for local development.

## Production Deployment

### 1. Environment Configuration

Create `backend/.env` from template:

```bash
cp backend/.env.example backend/.env
```

Update with production values:

```bash
# Database - Use managed PostgreSQL service
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/nitilens

# Redis - Use managed Redis service
REDIS_URL=redis://prod-redis.example.com:6379/0

# Security - Generate strong secrets
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Email - SendGrid production key
EMAIL_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@yourdomain.com

# Slack - Production webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/PROD/WEBHOOK

# Environment
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 2. Database Setup

```bash
# Create production database
createdb nitilens_db

# Run migrations
cd backend
alembic upgrade head

# Initialize with seed data
python init_db.py
```

### 3. Docker Production Build

Update `docker-compose.yml` for production:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      JWT_SECRET: ${JWT_SECRET}
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
  
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.worker worker --loglevel=info --concurrency=4
    restart: always
    deploy:
      replicas: 5
  
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    restart: always
```

Deploy:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 4. Kubernetes Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nitilens-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nitilens-backend
  template:
    metadata:
      labels:
        app: nitilens-backend
    spec:
      containers:
      - name: backend
        image: nitilens/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: nitilens-secrets
              key: database-url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: nitilens-backend
spec:
  selector:
    app: nitilens-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy to Kubernetes:

```bash
kubectl apply -f k8s/
```

### 5. AWS Deployment

#### Using ECS Fargate

```bash
# Build and push images
docker build -t nitilens-backend:latest ./backend
docker tag nitilens-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/nitilens-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/nitilens-backend:latest

# Create ECS task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-def.json

# Create ECS service
aws ecs create-service \
  --cluster nitilens-cluster \
  --service-name nitilens-backend \
  --task-definition nitilens-backend:1 \
  --desired-count 3 \
  --launch-type FARGATE
```

#### Using Elastic Beanstalk

```bash
# Initialize EB
eb init -p docker nitilens-platform

# Create environment
eb create nitilens-prod --database.engine postgres

# Deploy
eb deploy
```

### 6. Database Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### 7. Monitoring Setup

#### Prometheus Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'nitilens'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

#### Grafana Dashboard

Import dashboard from `monitoring/grafana-dashboard.json`

Key metrics:
- Request rate
- Response time
- Error rate
- Violation detection rate
- Database connections
- Worker queue size

### 8. Backup Strategy

#### Database Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > backups/nitilens_$DATE.sql
aws s3 cp backups/nitilens_$DATE.sql s3://nitilens-backups/
```

#### File Backups

```bash
# Backup uploaded policies
aws s3 sync /app/data/policies s3://nitilens-policies/
```

### 9. SSL/TLS Configuration

#### Using Let's Encrypt

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

#### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://frontend:80;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
    }
}
```

### 10. Performance Optimization

#### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_violations_org_severity ON violations(org_id, severity);
CREATE INDEX idx_violations_detected_at ON violations(detected_at DESC);
CREATE INDEX idx_policies_org_status ON policies(org_id, status);
CREATE INDEX idx_rules_policy_status ON rules(policy_id, status);

-- Analyze tables
ANALYZE violations;
ANALYZE policies;
ANALYZE rules;
```

#### Redis Caching

```python
# Cache frequently accessed data
@cache.memoize(timeout=3600)
def get_policy_rules(policy_id):
    return db.query(Rule).filter(Rule.policy_id == policy_id).all()
```

#### Worker Optimization

```bash
# Increase worker concurrency
celery -A app.worker worker --concurrency=8 --prefetch-multiplier=4

# Use multiple queues
celery -A app.worker worker -Q high_priority,default,low_priority
```

### 11. Security Hardening

```bash
# Update all packages
apt-get update && apt-get upgrade -y

# Configure firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Install fail2ban
apt-get install fail2ban
systemctl enable fail2ban
```

### 12. Logging

#### Centralized Logging

```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Log Aggregation (ELK Stack)

```bash
# Send logs to Elasticsearch
docker run -d \
  --name filebeat \
  -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
  docker.elastic.co/beats/filebeat:8.0.0
```

### 13. Health Checks

```bash
# Add to monitoring
*/5 * * * * curl -f http://localhost:8000/health || alert-team

# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

### 14. Disaster Recovery

#### Backup Restoration

```bash
# Restore database
psql $DATABASE_URL < backups/nitilens_20240221.sql

# Restore files
aws s3 sync s3://nitilens-backups/policies /app/data/policies
```

#### Failover Strategy

- Primary region: us-east-1
- Backup region: us-west-2
- RTO: 1 hour
- RPO: 15 minutes

### 15. Cost Optimization

#### AWS Cost Estimates

- **Basic Setup** (~$200/month)
  - RDS PostgreSQL: $50
  - ElastiCache Redis: $30
  - ECS Fargate (2 tasks): $80
  - ALB: $20
  - S3 + CloudFront: $20

- **Production Setup** (~$800/month)
  - RDS PostgreSQL (Multi-AZ): $200
  - ElastiCache Redis (Cluster): $100
  - ECS Fargate (10 tasks): $400
  - ALB: $20
  - S3 + CloudFront: $30
  - CloudWatch: $50

## Troubleshooting

### Common Issues

1. **Database connection errors**
   ```bash
   # Check connection
   psql $DATABASE_URL -c "SELECT 1"
   ```

2. **Redis connection errors**
   ```bash
   # Test Redis
   redis-cli -u $REDIS_URL ping
   ```

3. **Worker not processing tasks**
   ```bash
   # Check worker logs
   docker-compose logs worker
   
   # Restart workers
   docker-compose restart worker
   ```

4. **High memory usage**
   ```bash
   # Check container stats
   docker stats
   
   # Adjust worker concurrency
   celery -A app.worker worker --concurrency=2
   ```

## Support

For production support:
- Email: support@nitilens.com
- Slack: #nitilens-support
- On-call: +1-XXX-XXX-XXXX

---

**Last Updated:** 2024-02-21
