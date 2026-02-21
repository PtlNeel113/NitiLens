# NitiLens Quick Start Guide

## Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL 15+
- Redis 6+

## Quick Setup (5 minutes)

### 1. Clone & Install
```bash
# Clone repository
git clone https://github.com/PtlNeel113/NitiLens
cd NitiLens

# Install dependencies
npm install
cd backend && pip install -r requirements.txt
```

### 2. Setup Database
```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE nitilens_db;
CREATE USER nitilens WITH PASSWORD 'nitilens_password';
GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;
\q

# Run migrations
cd backend
alembic upgrade head
python seed_plans.py
```

### 3. Configure Environment
```bash
# Copy environment file
cp backend/.env.example backend/.env

# Edit backend/.env with your settings
```

### 4. Start Services
```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Start frontend
npm run dev
```

### 5. Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Default Credentials
```
Email: admin@nitilens.com
Password: admin123
```

## Next Steps
- Read [Complete Setup Guide](./SETUP-COMPLETE.md)
- Review [Architecture Documentation](../ARCHITECTURE.md)
- Check [API Documentation](http://localhost:8000/docs)

## Troubleshooting
See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
