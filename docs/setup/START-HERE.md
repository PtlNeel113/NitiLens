# 🚀 Quick Start Guide - Run NitiLens Locally

## Prerequisites

Before starting, ensure you have:

1. **Python 3.11+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
4. **Redis** - [Download](https://redis.io/download/)

## Option 1: Automated Startup (Recommended)

### Windows

Simply run the startup script:

```powershell
.\start-local.ps1
```

This script will:
- ✅ Check prerequisites
- ✅ Install all dependencies
- ✅ Initialize the database
- ✅ Start backend and frontend servers

### Linux/Mac

```bash
chmod +x setup.sh
./setup.sh
```

## Option 2: Manual Setup

### Step 1: Setup PostgreSQL

Create the database and user:

```sql
CREATE DATABASE nitilens_db;
CREATE USER nitilens WITH PASSWORD 'nitilens_password';
GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;
```

### Step 2: Start Redis

```bash
# Windows (if installed via Chocolatey)
redis-server

# Linux/Mac
redis-server
```

### Step 3: Configure Environment

```bash
cd backend
cp .env.example .env
# Edit .env with your database and Redis URLs
```

### Step 4: Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

**Frontend:**
```bash
npm install
```

### Step 5: Initialize Database

```bash
cd backend
python init_db.py
```

### Step 6: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
# Activate venv first (see Step 4)
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

## Access the Application

Once started, access:

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Default Login Credentials

### Admin User
- Email: `admin@nitilens.com`
- Password: `admin123`

### Demo User
- Email: `demo@nitilens.com`
- Password: `demo123`

## Features Available

✅ Multi-policy compliance scanning  
✅ Automated remediation engine  
✅ Policy impact analysis  
✅ Predictive risk detection  
✅ Real-time alerts (Email, Slack, WebSocket)  
✅ ERP/CRM connectors  
✅ Multi-language policy processing  

## Troubleshooting

### Database Connection Error

Check that:
1. PostgreSQL is running
2. Database `nitilens_db` exists
3. User `nitilens` has correct permissions
4. `DATABASE_URL` in `.env` is correct

### Redis Connection Error

Check that:
1. Redis is running on port 6379
2. `REDIS_URL` in `.env` is correct

### Port Already in Use

If port 8000 or 5173 is in use:

**Backend:**
```bash
uvicorn app.main:app --reload --port 8001
```

**Frontend:**
Update `vite.config.ts` or use:
```bash
npm run dev -- --port 5174
```

### Import Errors

Ensure virtual environment is activated:
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

## Docker Alternative

For a containerized setup:

```bash
docker-compose up --build
```

Access at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Next Steps

1. **Upload a Policy:** Go to Policies → Upload PDF
2. **Connect Data Source:** Go to Connectors → Add Connector
3. **Run Compliance Scan:** Go to Compliance → Scan Dataset
4. **View Results:** Check Violations, Remediation, Risk tabs

## Documentation

- `QUICKSTART.md` - Detailed getting started guide
- `GOVERNANCE-FEATURES.md` - Feature documentation
- `DEPLOYMENT.md` - Production deployment
- `README-ENTERPRISE.md` - Enterprise features

## Support

For issues or questions:
- Check the API docs: http://localhost:8000/docs
- Review logs in the terminal windows
- Check `TROUBLESHOOTING.md` (if available)

---

**Happy Compliance Monitoring! 🎉**
