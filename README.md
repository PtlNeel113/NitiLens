# NitiLens - Enterprise RegTech Compliance Platform

<div align="center">

![NitiLens Logo](https://img.shields.io/badge/NitiLens-RegTech-blue?style=for-the-badge)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql)](https://postgresql.org)

**AI-Powered Compliance & Regulatory Technology Platform**

[Quick Start](#quick-start) • [Features](#features) • [Documentation](#documentation) • [Demo](#demo)

</div>

---

## 🎯 Overview

NitiLens is an enterprise-grade RegTech platform that automates compliance monitoring, policy management, and regulatory reporting. Built with AI-powered rule extraction, real-time violation detection, and comprehensive audit trails.

### Key Capabilities

- 🤖 **AI Rule Extraction** - Automatically extract compliance rules from policy documents
- 🔍 **Real-Time Scanning** - Continuous compliance monitoring across data sources
- 📊 **Risk Scoring** - Dynamic risk assessment with explainable AI
- 🔄 **Remediation Workflow** - Automated case management and resolution tracking
- 📈 **Analytics Dashboard** - Real-time compliance metrics and trends
- 🌐 **Multi-Tenant SaaS** - Enterprise-ready with subscription management
- 🔐 **Audit Trail** - Complete compliance audit logging

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **PostgreSQL** 15+
- **Redis** 6+

### Installation (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/PtlNeel113/NitiLens
cd NitiLens

# 2. Install dependencies
npm install
cd backend && pip install -r requirements.txt

# 3. Setup database
createdb nitilens_db
cd backend
alembic upgrade head
python seed_plans.py

# 4. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# 5. Start services
# Terminal 1: Backend
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
npm run dev
```

### Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

**Default Login**: `admin@nitilens.com` / `admin123`

📖 **Detailed Setup**: See [Setup Guide](docs/setup/QUICK-START.md)

---

## ✨ Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Policy Management** | Upload, version, and manage compliance policies |
| **Rule Engine** | Dynamic rule evaluation with 13+ operators |
| **Violation Detection** | Real-time compliance violation scanning |
| **Review Workflow** | Human-in-the-loop review with audit logging |
| **Remediation Engine** | Automated case creation and tracking |
| **Risk Scoring** | AI-powered risk assessment (0-100 scale) |

### Enterprise Features

| Feature | Description |
|---------|-------------|
| **Multi-Tenant** | Complete organization isolation |
| **Subscription Plans** | Basic, Pro, Enterprise tiers |
| **Anomaly Detection** | ML-based transaction anomaly detection |
| **Policy Impact Analysis** | Track policy changes and impact |
| **Regulatory Mapping** | Map policies to regulatory frameworks |
| **Multi-Language** | Translation support for global compliance |
| **ERP Connectors** | PostgreSQL, MySQL, MongoDB, REST API, CSV |
| **Real-Time Alerts** | Email, Slack, WebSocket notifications |

### Technical Features

- **Scan History Tracking** - Complete audit trail of all scans
- **Recurrence Detection** - Identify recurring violations
- **Explainable AI** - Detailed explanations for every violation
- **Performance Monitoring** - System metrics and health tracking
- **Role-Based Access** - Super Admin, Compliance Admin, Reviewer, Viewer
- **API-First Design** - RESTful API with OpenAPI documentation

📖 **Full Feature List**: See [Features Documentation](docs/features/FEATURES.md)

---

## 📊 Architecture

### Technology Stack

**Frontend**
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- Recharts (data visualization)

**Backend**
- FastAPI (Python web framework)
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)
- Celery (async tasks)

**Database**
- PostgreSQL 15+ (primary database)
- Redis 6+ (caching, WebSocket, Celery)

**AI/ML**
- Transformers (NLP)
- scikit-learn (anomaly detection)
- LangDetect (language detection)

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  Dashboard │ Policies │ Violations │ Reviews │ Analytics    │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API
┌─────────────────────────┴───────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   API    │  │ Services │  │  Models  │  │Middleware│   │
│  │  Layer   │  │  Layer   │  │  Layer   │  │  Layer   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │    Redis     │  │  Connectors  │     │
│  │  (Primary)   │  │  (Cache)     │  │  (External)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

📖 **Detailed Architecture**: See [Architecture Documentation](docs/ARCHITECTURE.md)

---

## 📚 Documentation

### Getting Started
- [Quick Start Guide](docs/setup/QUICK-START.md)
- [Setup Complete Guide](docs/setup/SETUP-COMPLETE.md)
- [How to Run](docs/setup/HOW-TO-RUN.md)
- [Commands Cheatsheet](docs/setup/COMMANDS-CHEATSHEET.md)
- [Troubleshooting](docs/setup/TROUBLESHOOTING.md)

### Features & Implementation
- [Enterprise Features](docs/features/README-ENTERPRISE.md)
- [Subscription System](docs/features/SUBSCRIPTION-SYSTEM-COMPLETE.md)
- [Governance Features](docs/features/GOVERNANCE-FEATURES.md)
- [Implementation Summary](docs/implementation/IMPLEMENTATION-SUMMARY.md)

### Database
- [Database Information](docs/database/DATABASE-INFO.md)
- [Migration Guide](docs/database/DATABASE-MIGRATION-GUIDE.md)

### Deployment
- [GCP Deployment](docs/GCP-DEPLOYMENT.md)
- [Deployment Checklist](docs/deployment/DEPLOYMENT-CHECKLIST.md)
- [Docker Setup](docs/deployment/DOCKERFILE-SETUP-COMPLETE.md)

### Enterprise Upgrade
- [Production Grade Upgrade](docs/enterprise-upgrade/PRODUCTION-GRADE-UPGRADE.md)
- [Enterprise Upgrade Complete](docs/enterprise-upgrade/ENTERPRISE-UPGRADE-COMPLETE.md)
- [Developer Quick Reference](docs/enterprise-upgrade/DEVELOPER-QUICK-REFERENCE.md)
- [Verification Checklist](docs/enterprise-upgrade/VERIFICATION-CHECKLIST.md)

### Architecture & Business
- [System Architecture](docs/ARCHITECTURE.md)
- [Business Model](docs/BUSINESS_MODEL.md)

---

## 🎬 Demo

### Screenshots

**Dashboard**
![Dashboard](docs/images/dashboard.png)

**Violation Review**
![Review Queue](docs/images/review-queue.png)

**Risk Analytics**
![Risk Analytics](docs/images/risk-analytics.png)

### Live Demo

🔗 **Coming Soon**: Live demo environment

---

## 🗂️ Project Structure

```
NitiLens/
├── backend/                    # Backend application
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   ├── services/          # Business logic layer
│   │   ├── models/            # Database models
│   │   ├── core/              # Core utilities
│   │   ├── connectors/        # Data source connectors
│   │   └── middleware/        # Auth & subscription middleware
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   └── requirements.txt       # Python dependencies
├── src/                       # Frontend application
│   └── app/
│       ├── pages/             # React pages
│       ├── components/        # React components
│       └── services/          # API services
├── docs/                      # Documentation
│   ├── setup/                 # Setup guides
│   ├── features/              # Feature documentation
│   ├── deployment/            # Deployment guides
│   ├── database/              # Database documentation
│   ├── enterprise-upgrade/    # Enterprise upgrade docs
│   └── implementation/        # Implementation notes
├── tests/                     # Integration tests
├── data/                      # Sample datasets
└── scripts/                   # Utility scripts
```

---

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
npm run test

# E2E tests
npm run test:e2e
```

### Test Coverage

- Unit tests for services
- Integration tests for API endpoints
- E2E tests for critical workflows
- Performance benchmarks

---

## 🚢 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Cloud Deployment

**Google Cloud Platform**
```bash
# Deploy to GCP
./deploy-gcp.sh
```

**AWS / Azure**
See [Deployment Guide](docs/deployment/DEPLOYMENT.md)

---

## 🔐 Security

- JWT-based authentication
- Role-based access control (RBAC)
- SQL injection prevention
- XSS protection
- CORS configuration
- Secure password hashing (bcrypt)
- Environment variable management

---

## 📈 Performance

- **Scan Speed**: 50+ records/second
- **Dashboard Load**: < 500ms
- **API Response**: < 100ms (avg)
- **Database Queries**: Optimized with indexes
- **Connection Pooling**: 10 base + 20 overflow

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Project Lead**: Neel Patel  
**GitHub**: [@PtlNeel113](https://github.com/PtlNeel113)

---

## 🙏 Acknowledgments

- IBM AML Dataset (Kaggle)
- FastAPI Framework
- React Community
- PostgreSQL Team

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/PtlNeel113/NitiLens/issues)
- **Email**: support@nitilens.com

---

## 🗺️ Roadmap

### Q1 2026
- [ ] Advanced ML models for anomaly detection
- [ ] Real-time collaboration features
- [ ] Mobile app (iOS/Android)

### Q2 2026
- [ ] Blockchain audit trail
- [ ] Advanced reporting engine
- [ ] Third-party integrations (Salesforce, SAP)

### Q3 2026
- [ ] AI-powered policy recommendations
- [ ] Automated regulatory filing
- [ ] Global compliance frameworks

---

<div align="center">

**Built with ❤️ for Compliance Professionals**

[⬆ Back to Top](#nitilens---enterprise-regtech-compliance-platform)

</div>
