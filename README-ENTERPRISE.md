# 🚀 NitiLens Enterprise SaaS Compliance Platform

## Overview

NitiLens Enterprise is a production-ready, multi-tenant SaaS compliance platform that transforms policy documents into automated compliance monitoring across your entire organization.

## 🌟 Enterprise Features

### 1️⃣ Multi-Policy Support
- **Unlimited policies** per organization (Enterprise plan)
- **Version control** for policy documents
- **Department-based** policy management
- **Regulatory framework** categorization (AML, GDPR, SOX, HIPAA, etc.)
- **Policy comparison** tool for version differences
- **Cross-policy** compliance aggregation

### 2️⃣ Real Data Connectors
- **PostgreSQL** - Direct database integration
- **MySQL** - MySQL database connector
- **MongoDB** - NoSQL database support
- **REST API** - Generic API connector with authentication
- **CSV Upload** - File-based data import
- **Field mapping** - Map source fields to compliance schema
- **Encrypted credentials** - Secure credential storage

### 3️⃣ Real-Time Alert System
- **WebSocket** - Live browser notifications
- **Email** - SendGrid integration for email alerts
- **Slack** - Webhook integration for team notifications
- **Severity-based** routing (critical/high violations)
- **Alert logging** - Complete audit trail
- **Multi-channel** delivery

### 4️⃣ Multi-Language Processing
- **Automatic language detection** (langdetect)
- **Translation to English** for rule extraction
- **10+ languages supported** (ES, FR, DE, ZH, JA, KO, AR, RU, PT, IT)
- **Local translation models** (MarianMT)
- **Translation confidence** scoring
- **Original text preservation** for audit

### 5️⃣ Multi-Tenant Architecture
- **Organization isolation** - Complete data separation
- **Role-Based Access Control** (RBAC)
  - Super Admin
  - Compliance Admin
  - Reviewer
  - Viewer
- **Subscription plans** (Basic, Pro, Enterprise)
- **Usage limits** enforcement
- **Per-tenant** customization

### 6️⃣ Production Monitoring
- **Health checks** - `/health` endpoint
- **Prometheus metrics** - `/metrics` endpoint
- **System statistics** - Real-time platform stats
- **Performance monitoring** - Request/response tracking
- **Error logging** - Comprehensive error tracking

### 7️⃣ Scalable Architecture
- **Async processing** - Celery background workers
- **Batch processing** - Handle millions of records
- **Database indexing** - Optimized queries
- **Connection pooling** - Efficient resource usage
- **Horizontal scaling** - Add more workers as needed
- **Pagination** - All list endpoints paginated

### 8️⃣ Auto-Installation
- **One-command setup** - `./setup.sh`
- **Docker deployment** - `docker-compose up --build`
- **Automated migrations** - Database schema management
- **Seed data** - Default admin user
- **Environment configuration** - Auto-generated `.env`

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (Nginx)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐         ┌───────▼────────┐
        │   Frontend     │         │    Backend     │
        │   (React)      │         │   (FastAPI)    │
        └────────────────┘         └────────┬───────┘
                                            │
                ┌───────────────────────────┼───────────────┐
                │                           │               │
        ┌───────▼────────┐         ┌───────▼────────┐  ┌──▼──────┐
        │   PostgreSQL   │         │     Redis      │  │ Workers │
        │   (Database)   │         │   (Cache/WS)   │  │ (Celery)│
        └────────────────┘         └────────────────┘  └─────────┘
```

## 📦 Installation

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd nitilens-enterprise

# Run setup script
chmod +x setup.sh
./setup.sh

# Choose option 1 (Docker)
# Services will start automatically
```

Access the platform:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

```bash
# Run setup script
./setup.sh

# Choose option 2 (Local Development)
# Follow the prompts to configure PostgreSQL and Redis

# Start services in separate terminals:

# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
npm run dev

# Terminal 3 - Worker (Optional)
cd backend
celery -A app.worker worker --loglevel=info
```

## 🔐 Default Credentials

```
Admin User:
  Email: admin@nitilens.com
  Password: admin123

Demo User:
  Email: demo@nitilens.com
  Password: demo123
```

## 🔧 Configuration

### Environment Variables

Edit `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://nitilens:nitilens_password@localhost:5432/nitilens_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET=your-super-secret-jwt-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (SendGrid)
EMAIL_API_KEY=your-sendgrid-api-key
EMAIL_FROM=noreply@nitilens.com

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Subscription Limits
BASIC_POLICY_LIMIT=1
BASIC_TRANSACTION_LIMIT=10000
PRO_POLICY_LIMIT=10
PRO_TRANSACTION_LIMIT=1000000
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new organization
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Policies
- `GET /api/policies` - List policies
- `POST /api/policies/upload` - Upload policy PDF
- `GET /api/policies/compare` - Compare policy versions
- `DELETE /api/policies/{id}` - Delete policy

### Connectors
- `GET /api/connectors/list` - List connectors
- `POST /api/connectors/add` - Add connector
- `POST /api/connectors/test/{id}` - Test connection
- `DELETE /api/connectors/remove/{id}` - Remove connector

### Compliance
- `POST /api/compliance/scan` - Run compliance scan
- `GET /api/compliance/violations` - List violations
- `GET /api/compliance/summary` - Get summary stats

### Monitoring
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /api/stats` - Platform statistics

## 🔌 Connector Configuration

### PostgreSQL
```json
{
  "connector_name": "Production DB",
  "connector_type": "postgresql",
  "connection_config": {
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "dbuser",
    "password": "dbpass"
  },
  "field_mapping": {
    "id": "transaction_id",
    "amt": "amount",
    "dt": "date"
  }
}
```

### REST API
```json
{
  "connector_name": "ERP API",
  "connector_type": "rest_api",
  "connection_config": {
    "base_url": "https://api.example.com",
    "endpoint": "/transactions",
    "api_key": "your-api-key"
  }
}
```

## 🚀 Scaling

### Horizontal Scaling
```bash
# Scale workers
docker-compose up -d --scale worker=5

# Scale backend
docker-compose up -d --scale backend=3
```

### Database Optimization
- Indexes on: `org_id`, `policy_id`, `rule_id`, `severity`, `status`
- Connection pooling: 10 connections, 20 max overflow
- Query pagination: All list endpoints

### Performance Tuning
- Batch size: 1000 records per batch
- Worker concurrency: 4 per worker
- Redis caching: 1 hour TTL
- WebSocket: 1000 concurrent connections

## 📈 Monitoring

### Prometheus Metrics
```bash
# Scrape metrics
curl http://localhost:8000/metrics

# Available metrics:
- compliance_scans_total
- violations_detected_total{severity}
- scan_duration_seconds
```

### Health Checks
```bash
# Check system health
curl http://localhost:8000/health

# Get platform stats
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/stats
```

## 🔒 Security

- **JWT authentication** - Secure token-based auth
- **Password hashing** - bcrypt with salt
- **Encrypted credentials** - Fernet encryption for connector credentials
- **CORS protection** - Configurable origins
- **SQL injection prevention** - SQLAlchemy ORM
- **Input validation** - Pydantic models
- **Rate limiting** - (Add nginx rate limiting in production)

## 📝 License

MIT License - See LICENSE file

## 🤝 Support

For enterprise support:
- Email: support@nitilens.com
- Documentation: https://docs.nitilens.com
- GitHub Issues: https://github.com/your-org/nitilens/issues

## 🎯 Roadmap

- [ ] Advanced rule engine with ML
- [ ] Custom report builder
- [ ] SSO integration (SAML, OAuth)
- [ ] Mobile app
- [ ] Advanced analytics dashboard
- [ ] Audit log export
- [ ] API rate limiting
- [ ] Multi-region deployment

---

**Built with ❤️ for enterprise compliance teams**
