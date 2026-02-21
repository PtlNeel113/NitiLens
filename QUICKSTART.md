# ⚡ NitiLens Enterprise - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Clone & Setup

```bash
# Clone the repository
git clone <repository-url>
cd nitilens-enterprise

# Make setup script executable
chmod +x setup.sh

# Run automated setup
./setup.sh
```

### Step 2: Choose Installation Method

When prompted, select:
- **Option 1: Docker** (Recommended) - Everything configured automatically
- **Option 2: Local Development** - Manual setup for development

### Step 3: Access the Platform

After installation completes:

```
🌐 Frontend:  http://localhost:3000
🔧 Backend:   http://localhost:8000
📚 API Docs:  http://localhost:8000/docs
💚 Health:    http://localhost:8000/health
```

### Step 4: Login

Use default credentials:

```
Admin Account:
  Email: admin@nitilens.com
  Password: admin123

Demo Account:
  Email: demo@nitilens.com
  Password: demo123
```

## 📋 What You Get

### ✅ Pre-Configured Features

1. **Multi-Tenant Platform**
   - Demo organization created
   - Admin and demo users ready
   - RBAC permissions configured

2. **Database Schema**
   - PostgreSQL with all tables
   - Indexes optimized
   - Sample data loaded

3. **Real-Time Alerts**
   - WebSocket server running
   - Redis pub/sub configured
   - Email/Slack ready (add keys)

4. **Data Connectors**
   - PostgreSQL connector
   - MySQL connector
   - MongoDB connector
   - REST API connector
   - CSV upload

5. **Monitoring**
   - Health checks active
   - Prometheus metrics exposed
   - System stats available

## 🎯 Quick Tasks

### Upload Your First Policy

```bash
# Via API
curl -X POST http://localhost:8000/api/policies/upload \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@policy.pdf" \
  -F "policy_name=AML Policy" \
  -F "department=Finance" \
  -F "regulatory_framework=AML"
```

### Add a Data Connector

```bash
# PostgreSQL connector
curl -X POST http://localhost:8000/api/connectors/add \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "connector_name": "Production DB",
    "connector_type": "postgresql",
    "connection_config": {
      "host": "localhost",
      "port": 5432,
      "database": "mydb",
      "user": "user",
      "password": "pass"
    }
  }'
```

### Run Compliance Scan

```bash
# Scan all policies
curl -X POST http://localhost:8000/api/compliance/scan \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 1000
  }'
```

### Get Violations

```bash
# List all violations
curl http://localhost:8000/api/compliance/violations \
  -H "Authorization: Bearer <your-token>"

# Filter by severity
curl "http://localhost:8000/api/compliance/violations?severity=critical" \
  -H "Authorization: Bearer <your-token>"
```

## 🔧 Configuration

### Email Alerts (SendGrid)

Edit `backend/.env`:

```bash
EMAIL_API_KEY=SG.your-sendgrid-api-key
EMAIL_FROM=noreply@yourdomain.com
```

Restart backend:

```bash
docker-compose restart backend
```

### Slack Alerts

Edit `backend/.env`:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

Restart backend:

```bash
docker-compose restart backend
```

### Translation Service

For multi-language support, models download automatically on first use.

To use external API instead:

```bash
TRANSLATION_API_KEY=your-api-key
TRANSLATION_API_URL=https://api.translation-service.com
```

## 📊 Monitoring

### Check System Health

```bash
curl http://localhost:8000/health
```

### View Metrics

```bash
curl http://localhost:8000/metrics
```

### Get Platform Stats

```bash
curl http://localhost:8000/api/stats \
  -H "Authorization: Bearer <your-token>"
```

## 🐛 Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose logs -f

# Restart all services
docker-compose restart

# Rebuild if needed
docker-compose down
docker-compose up --build -d
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Redis Connection Error

```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Worker Not Processing

```bash
# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker

# Scale workers
docker-compose up -d --scale worker=3
```

## 📚 Next Steps

1. **Read Full Documentation**
   - [README-ENTERPRISE.md](README-ENTERPRISE.md) - Complete feature guide
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
   - API Docs: http://localhost:8000/docs

2. **Configure Your Organization**
   - Upload policies
   - Add data connectors
   - Configure alerts
   - Invite team members

3. **Run Your First Scan**
   - Connect to your data source
   - Run compliance scan
   - Review violations
   - Generate reports

4. **Customize**
   - Add custom rules
   - Configure thresholds
   - Set up scheduled scans
   - Create dashboards

## 💡 Tips

- **Use Docker for quick testing** - Everything works out of the box
- **Use local dev for customization** - Better for development
- **Check logs frequently** - `docker-compose logs -f`
- **Monitor resource usage** - `docker stats`
- **Backup regularly** - Database and uploaded files

## 🆘 Getting Help

- **Documentation**: Check README-ENTERPRISE.md
- **API Reference**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Email**: support@nitilens.com

## 🎉 You're Ready!

Your NitiLens Enterprise platform is now running. Start by:

1. Logging in at http://localhost:3000
2. Uploading a policy document
3. Connecting a data source
4. Running your first compliance scan

**Welcome to automated compliance monitoring!** 🚀

---

**Need help?** Check the full documentation or contact support.
