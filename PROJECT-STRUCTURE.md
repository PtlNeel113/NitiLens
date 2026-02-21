# NitiLens Project Structure

## 📁 Complete Directory Structure

```
NitiLens/
│
├── 📂 backend/                          # Backend Application (Python/FastAPI)
│   ├── 📂 app/
│   │   ├── 📂 api/                      # API Route Handlers
│   │   │   ├── auth.py                  # Authentication endpoints
│   │   │   ├── compliance.py            # Compliance scanning endpoints
│   │   │   ├── connectors.py            # Data connector endpoints
│   │   │   ├── dashboard.py             # Dashboard metrics endpoints
│   │   │   ├── datasets.py              # Dataset management endpoints
│   │   │   ├── monitoring.py            # System monitoring endpoints
│   │   │   ├── policies.py              # Policy management endpoints
│   │   │   ├── policy_impact.py         # Policy impact analysis endpoints
│   │   │   ├── remediation.py           # Remediation workflow endpoints
│   │   │   ├── reviews.py               # Violation review endpoints
│   │   │   ├── risk.py                  # Risk assessment endpoints
│   │   │   ├── subscription.py          # Subscription management endpoints
│   │   │   └── __init__.py
│   │   │
│   │   ├── 📂 services/                 # Business Logic Layer
│   │   │   ├── alert_service.py         # Alert notification service
│   │   │   ├── anomaly_detector.py      # ML-based anomaly detection
│   │   │   ├── compliance_engine.py     # Compliance scanning engine
│   │   │   ├── policy_impact_analyzer.py # Policy change impact analysis
│   │   │   ├── remediation_engine.py    # Remediation workflow engine
│   │   │   ├── rule_engine.py           # Dynamic rule evaluation engine
│   │   │   ├── subscription_service.py  # Subscription management service
│   │   │   └── translation_service.py   # Multi-language translation
│   │   │
│   │   ├── 📂 models/                   # Database Models (SQLAlchemy)
│   │   │   ├── db_models.py             # All database models
│   │   │   ├── alert.py                 # Alert model
│   │   │   ├── connector.py             # Connector model
│   │   │   ├── organization.py          # Organization model
│   │   │   ├── policy.py                # Policy model
│   │   │   ├── review.py                # Review model
│   │   │   ├── rule.py                  # Rule model
│   │   │   ├── user.py                  # User model
│   │   │   ├── violation.py             # Violation model
│   │   │   └── __init__.py
│   │   │
│   │   ├── 📂 core/                     # Core Utilities
│   │   │   ├── pdf_parser.py            # PDF policy document parser
│   │   │   ├── rule_engine.py           # Legacy rule engine
│   │   │   ├── rule_extractor.py        # AI rule extraction
│   │   │   ├── scheduler.py             # Task scheduler
│   │   │   ├── scheduler_enhanced.py    # Enhanced scheduler
│   │   │   ├── violation_engine.py      # Legacy violation engine
│   │   │   └── __init__.py
│   │   │
│   │   ├── 📂 connectors/               # Data Source Connectors
│   │   │   ├── base.py                  # Base connector class
│   │   │   ├── csv_connector.py         # CSV file connector
│   │   │   ├── mongodb.py               # MongoDB connector
│   │   │   ├── mysql.py                 # MySQL connector
│   │   │   ├── postgresql.py            # PostgreSQL connector
│   │   │   ├── rest_api.py              # REST API connector
│   │   │   └── __init__.py
│   │   │
│   │   ├── 📂 middleware/               # Middleware Components
│   │   │   ├── performance_middleware.py # Performance monitoring
│   │   │   └── subscription_middleware.py # Subscription enforcement
│   │   │
│   │   ├── 📂 storage/                  # JSON Storage (Legacy)
│   │   │   ├── policies.json
│   │   │   ├── reviews.json
│   │   │   ├── rules.json
│   │   │   └── violations.json
│   │   │
│   │   ├── auth.py                      # Authentication utilities
│   │   ├── database.py                  # Database configuration
│   │   ├── main.py                      # FastAPI application entry
│   │   ├── websocket.py                 # WebSocket handler
│   │   ├── worker.py                    # Celery worker
│   │   └── __init__.py
│   │
│   ├── 📂 alembic/                      # Database Migrations
│   │   ├── 📂 versions/                 # Migration versions
│   │   ├── env.py                       # Alembic environment
│   │   └── script.py.mako               # Migration template
│   │
│   ├── 📂 tests/                        # Backend Tests
│   │   ├── test_api.py
│   │   ├── test_services.py
│   │   └── test_models.py
│   │
│   ├── .env                             # Environment variables
│   ├── .env.example                     # Environment template
│   ├── alembic.ini                      # Alembic configuration
│   ├── init_db.py                       # Database initialization
│   ├── seed_plans.py                    # Seed subscription plans
│   ├── requirements.txt                 # Python dependencies
│   ├── cloudbuild.yaml                  # GCP Cloud Build config
│   └── Dockerfile                       # Backend Docker image
│
├── 📂 src/                              # Frontend Application (React/TypeScript)
│   └── 📂 app/
│       ├── 📂 pages/                    # React Pages
│       │   ├── Dashboard.tsx            # Main dashboard
│       │   ├── Policies.tsx             # Policy management
│       │   ├── Violations.tsx           # Violation list
│       │   ├── Reviews.tsx              # Review queue
│       │   ├── Remediation.tsx          # Remediation cases
│       │   ├── Risk.tsx                 # Risk analytics
│       │   ├── PolicyImpact.tsx         # Policy impact analysis
│       │   ├── Connectors.tsx           # Data connectors
│       │   ├── Monitoring.tsx           # System monitoring
│       │   ├── Subscription.tsx         # Subscription management
│       │   ├── EnterpriseControlCenter.tsx # Enterprise features
│       │   └── Login.tsx                # Login page
│       │
│       ├── 📂 components/               # React Components
│       │   ├── Navbar.tsx               # Navigation bar
│       │   ├── Sidebar.tsx              # Sidebar navigation
│       │   ├── FeatureLock.tsx          # Subscription feature lock
│       │   ├── ViolationCard.tsx        # Violation display card
│       │   ├── PolicyCard.tsx           # Policy display card
│       │   └── ...
│       │
│       ├── 📂 services/                 # API Services
│       │   ├── api.ts                   # Base API service
│       │   ├── api-enterprise.ts        # Enterprise API service
│       │   └── auth.ts                  # Authentication service
│       │
│       ├── 📂 types/                    # TypeScript Types
│       │   ├── index.ts
│       │   └── api.ts
│       │
│       ├── 📂 utils/                    # Utility Functions
│       │   └── helpers.ts
│       │
│       ├── App.tsx                      # Main App component
│       └── main.tsx                     # React entry point
│
├── 📂 docs/                             # Documentation
│   ├── 📂 setup/                        # Setup Guides
│   │   ├── QUICK-START.md               # Quick start guide
│   │   ├── SETUP-COMPLETE.md            # Complete setup guide
│   │   ├── HOW-TO-RUN.md                # How to run guide
│   │   ├── RUN-LOCALHOST.md             # Localhost setup
│   │   ├── COMMANDS-CHEATSHEET.md       # Command reference
│   │   ├── TROUBLESHOOTING.md           # Troubleshooting guide
│   │   ├── START-HERE.md                # Getting started
│   │   ├── QUICK-START-CARD.md          # Quick reference card
│   │   └── README-LOCALHOST.md          # Localhost README
│   │
│   ├── 📂 features/                     # Feature Documentation
│   │   ├── README-ENTERPRISE.md         # Enterprise features
│   │   ├── FEATURES.md                  # Feature list
│   │   ├── SUBSCRIPTION-SYSTEM-COMPLETE.md # Subscription system
│   │   ├── GOVERNANCE-FEATURES.md       # Governance features
│   │   └── GOVERNANCE-IMPLEMENTATION.md # Governance implementation
│   │
│   ├── 📂 deployment/                   # Deployment Guides
│   │   ├── DEPLOYMENT.md                # Deployment guide
│   │   ├── DEPLOYMENT-CHECKLIST.md      # Deployment checklist
│   │   ├── DOCKERFILE-SETUP-COMPLETE.md # Docker setup
│   │   └── GET-CONTAINER-URLS.md        # Container URL guide
│   │
│   ├── 📂 database/                     # Database Documentation
│   │   └── DATABASE-INFO.md             # Database information
│   │
│   ├── 📂 enterprise-upgrade/           # Enterprise Upgrade Docs
│   │   └── PRODUCTION-GRADE-UPGRADE.md  # Production upgrade guide
│   │
│   ├── 📂 implementation/               # Implementation Notes
│   │   ├── IMPLEMENTATION-SUMMARY.md    # Implementation summary
│   │   ├── DASHBOARD-INTEGRATION-COMPLETE.md # Dashboard integration
│   │   ├── DASHBOARD-VISUAL-GUIDE.md    # Dashboard visual guide
│   │   ├── TYPESCRIPT-FIXES.md          # TypeScript fixes
│   │   ├── UI-RESTRUCTURE-COMPLETE.md   # UI restructure
│   │   ├── BEFORE-AFTER-COMPARISON.md   # Before/after comparison
│   │   └── GIT-PUSH-SUMMARY.md          # Git push summary
│   │
│   ├── ARCHITECTURE.md                  # System architecture
│   ├── BUSINESS_MODEL.md                # Business model
│   └── GCP-DEPLOYMENT.md                # GCP deployment guide
│
├── 📂 tests/                            # Integration Tests
│   ├── e2e_compliance_flow.py           # E2E compliance test
│   ├── benchmark_scan_engine.py         # Performance benchmark
│   └── generate_transactions.py         # Test data generator
│
├── 📂 data/                             # Sample Datasets
│   └── 📂 datasets/
│       └── 📂 ibm_aml/
│           ├── README.md
│           └── sample_transactions.csv
│
├── 📂 scripts/                          # Utility Scripts
│   ├── setup.sh                         # Linux/Mac setup script
│   ├── setup-windows.ps1                # Windows setup script
│   ├── start-local.ps1                  # Local startup script
│   ├── start-docker.ps1                 # Docker startup script
│   ├── deploy-gcp.sh                    # GCP deployment script
│   ├── deploy-gcp.ps1                   # GCP deployment (PowerShell)
│   ├── show-container-urls.sh           # Show container URLs
│   └── show-container-urls.ps1          # Show container URLs (PowerShell)
│
├── 📂 .vscode/                          # VS Code Configuration
│   └── settings.json
│
├── 📂 .git/                             # Git Repository
│
├── 📄 Configuration Files
│   ├── .gitignore                       # Git ignore rules
│   ├── .gitattributes                   # Git attributes
│   ├── package.json                     # Node.js dependencies
│   ├── package-lock.json                # Locked dependencies
│   ├── tsconfig.json                    # TypeScript config
│   ├── tsconfig.node.json               # TypeScript Node config
│   ├── vite.config.ts                   # Vite configuration
│   ├── postcss.config.mjs               # PostCSS configuration
│   ├── tailwind.config.js               # TailwindCSS configuration
│   ├── docker-compose.yml               # Docker Compose config
│   ├── Dockerfile.frontend              # Frontend Docker image
│   ├── nginx.conf                       # Nginx configuration
│   ├── nginx-frontend.conf              # Frontend Nginx config
│   ├── cloudbuild-frontend.yaml         # Frontend Cloud Build
│   └── index.html                       # HTML entry point
│
├── 📄 Documentation Files
│   ├── README.md                        # Main README
│   ├── PROJECT-STRUCTURE.md             # This file
│   ├── QUICKSTART.md                    # Quick start
│   ├── WORK-COMPLETE-SUMMARY.md         # Work summary
│   └── QUICK-REFERENCE-GOVERNANCE.md    # Governance reference
│
└── 📄 License & Legal
    └── LICENSE                          # MIT License
```

---

## 📋 File Categories

### Backend Core Files
- `backend/app/main.py` - FastAPI application entry point
- `backend/app/database.py` - Database configuration and session management
- `backend/app/auth.py` - Authentication and JWT utilities
- `backend/app/websocket.py` - WebSocket connection handler
- `backend/app/worker.py` - Celery background worker

### API Layer (`backend/app/api/`)
All API route handlers following RESTful conventions:
- Authentication & authorization
- CRUD operations for resources
- Business logic delegation to services
- Request/response validation

### Service Layer (`backend/app/services/`)
Business logic implementation:
- `compliance_engine.py` - Core compliance scanning logic
- `rule_engine.py` - Dynamic rule evaluation
- `remediation_engine.py` - Remediation workflow management
- `subscription_service.py` - Subscription and billing logic
- `anomaly_detector.py` - ML-based anomaly detection

### Data Layer (`backend/app/models/`)
SQLAlchemy ORM models:
- 17 database tables
- Relationships and constraints
- Enums and custom types
- Audit trail models

### Frontend Core Files
- `src/app/main.tsx` - React application entry
- `src/app/App.tsx` - Main app component with routing
- `src/app/services/api.ts` - API client configuration
- `vite.config.ts` - Build configuration

### Frontend Pages (`src/app/pages/`)
React page components:
- Dashboard, Policies, Violations, Reviews
- Remediation, Risk, PolicyImpact
- Connectors, Monitoring, Subscription
- EnterpriseControlCenter, Login

---

## 🔑 Key Directories

### `/backend/app/api/`
**Purpose**: API route handlers  
**Pattern**: One file per resource  
**Responsibility**: Request handling, validation, response formatting

### `/backend/app/services/`
**Purpose**: Business logic layer  
**Pattern**: Service classes with methods  
**Responsibility**: Core business logic, no HTTP concerns

### `/backend/app/models/`
**Purpose**: Database models  
**Pattern**: SQLAlchemy ORM models  
**Responsibility**: Data structure, relationships, constraints

### `/backend/alembic/versions/`
**Purpose**: Database migrations  
**Pattern**: Timestamped migration files  
**Responsibility**: Schema changes, data migrations

### `/src/app/pages/`
**Purpose**: React page components  
**Pattern**: One file per page  
**Responsibility**: Page layout, data fetching, state management

### `/src/app/components/`
**Purpose**: Reusable React components  
**Pattern**: Atomic design principles  
**Responsibility**: UI components, no business logic

### `/docs/`
**Purpose**: Project documentation  
**Pattern**: Organized by category  
**Responsibility**: Setup, features, deployment, implementation guides

---

## 📦 Dependencies

### Backend (`backend/requirements.txt`)
- **Web Framework**: FastAPI, Uvicorn
- **Database**: SQLAlchemy, psycopg2-binary, Alembic
- **Authentication**: python-jose, passlib, bcrypt
- **ML/AI**: transformers, torch, scikit-learn
- **Async**: Celery, Redis, aiofiles
- **Connectors**: pymongo, pymysql, httpx

### Frontend (`package.json`)
- **Framework**: React 18, TypeScript
- **Build**: Vite
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **HTTP**: Axios
- **Routing**: React Router

---

## 🎯 Code Organization Principles

### 1. Separation of Concerns
- API layer handles HTTP
- Service layer handles business logic
- Model layer handles data

### 2. Single Responsibility
- Each file has one clear purpose
- Each function does one thing well

### 3. Dependency Injection
- Services injected via FastAPI Depends
- Database sessions managed properly

### 4. Clean Architecture
```
API → Services → Models → Database
```

### 5. Type Safety
- Python type hints throughout
- TypeScript for frontend
- Pydantic for validation

---

## 🔄 Data Flow

### Request Flow
```
Client Request
    ↓
API Route Handler (api/)
    ↓
Service Layer (services/)
    ↓
Model Layer (models/)
    ↓
Database (PostgreSQL)
```

### Response Flow
```
Database Query Result
    ↓
Model Objects
    ↓
Service Processing
    ↓
API Response Formatting
    ↓
Client Response
```

---

## 📝 Naming Conventions

### Files
- **Python**: `snake_case.py`
- **TypeScript**: `PascalCase.tsx` (components), `camelCase.ts` (utilities)
- **Documentation**: `UPPERCASE-WITH-DASHES.md`

### Code
- **Classes**: `PascalCase`
- **Functions**: `snake_case` (Python), `camelCase` (TypeScript)
- **Constants**: `UPPER_SNAKE_CASE`
- **Variables**: `snake_case` (Python), `camelCase` (TypeScript)

### Database
- **Tables**: `snake_case` (plural)
- **Columns**: `snake_case`
- **Indexes**: `idx_table_column`
- **Foreign Keys**: `fk_table_column`

---

## 🚀 Getting Started

1. **Read**: [README.md](README.md)
2. **Setup**: [docs/setup/QUICK-START.md](docs/setup/QUICK-START.md)
3. **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. **Features**: [docs/features/FEATURES.md](docs/features/FEATURES.md)
5. **Deploy**: [docs/deployment/DEPLOYMENT.md](docs/deployment/DEPLOYMENT.md)

---

## 📞 Support

For questions about project structure:
- Check this document
- Review [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- See [DEVELOPER-QUICK-REFERENCE.md](docs/enterprise-upgrade/DEVELOPER-QUICK-REFERENCE.md)

---

**Last Updated**: 2026-02-21  
**Version**: 2.0 (Enterprise)
