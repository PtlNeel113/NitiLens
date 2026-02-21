# 🏠 Running NitiLens on Localhost - Complete Guide

## 🎯 What You'll Get

A fully functional enterprise compliance platform running locally with:
- ✅ Multi-policy compliance scanning
- ✅ Automated remediation engine
- ✅ Policy impact analysis
- ✅ Predictive risk detection with ML
- ✅ Real-time alerts (WebSocket, Email, Slack)
- ✅ Multi-tenant architecture
- ✅ ERP/CRM connectors
- ✅ Multi-language policy processing

---

## ⚡ Super Quick Start (2 Minutes)

### Prerequisites
Install these first:
1. Python 3.11+ → https://www.python.org/downloads/
2. Node.js 18+ → https://nodejs.org/
3. PostgreSQL 15+ → https://www.postgresql.org/download/
4. Redis → https://redis.io/download/

### Setup Database (30 seconds)
```sql
psql -U postgres
CREATE DATABASE nitilens_db;
CREATE USER nitilens WITH PASSWORD 'nitilens_password';
GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;
\q
```

### Start Redis (10 seconds)
```bash
redis-server
```

### Run the App (1 minute)
```powershell
# Windows
.\start-local.ps1

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

**Done!** Open http://localhost:5173 and login with:
- Email: `admin@nitilens.com`
- Password: `admin123`

---

## 📖 What the Script Does

The `start-local.ps1` script automatically:

1. ✅ Checks Python and Node.js are installed
2. ✅ Creates `.env` file from template
3. ✅ Creates Python virtual environment
4. ✅ Installs all Python dependencies (~5 min first time)
5. ✅ Installs all Node.js dependencies (~2 min first time)
6. ✅ Initializes PostgreSQL database with schema
7. ✅ Seeds default admin and demo users
8. ✅ Starts backend API server (port 8000)
9. ✅ Starts frontend dev server (port 5173)
10. ✅ Opens both in separate terminal windows

---

## 🖥️ What You'll See

### Terminal 1: Backend API
```
🔧 Backend API Server
===================

INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
🚀 NitiLens Enterprise Platform started
📊 Environment: development
📚 API Documentation: http://localhost:8000/docs
```

### Terminal 2: Frontend
```
🎨 Frontend Development Server
============================

VITE v6.3.5  ready in 1234 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### Main Terminal: Success Message
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 NitiLens Enterprise Platform is running!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Access URLs:
   Frontend:       http://localhost:5173
   Backend API:    http://localhost:8000
   API Docs:       http://localhost:8000/docs
   Health Check:   http://localhost:8000/health
   Metrics:        http://localhost:8000/metrics

📝 Default Login Credentials:
   Admin User:
     Email:    admin@nitilens.com
     Password: admin123

   Demo User:
     Email:    demo@nitilens.com
     Password: demo123
```

---

## 🎮 Using the Application

### 1. Login
- Open http://localhost:5173
- Enter credentials (admin@nitilens.com / admin123)
- Click "Login"

### 2. Upload a Policy
- Click "Policies" in sidebar
- Click "Upload Policy" button
- Select a PDF compliance document
- System extracts rules automatically

### 3. Connect Data Source
- Click "Connectors" in sidebar
- Click "Add Connector"
- Choose connector type (PostgreSQL, MySQL, MongoDB, REST API, CSV)
- Enter connection details
- Test connection

### 4. Run Compliance Scan
- Click "Compliance" in sidebar
- Select policy from dropdown
- Select dataset from dropdown
- Click "Scan Dataset"
- Wait for scan to complete

### 5. View Results
- **Violations Tab:** See all detected violations
- **Remediation Tab:** Manage remediation cases
- **Risk Tab:** View anomaly detection and risk scores
- **Policy Impact Tab:** Compare policy versions

---

## 🔧 Manual Setup (If Script Fails)

### Step 1: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py
```

### Step 2: Frontend Setup
```bash
# From project root
npm install
```

### Step 3: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
# Activate venv first
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

---

## 🐛 Common Issues & Fixes

### Issue: "Database connection failed"
**Fix:**
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Verify database exists
psql -U postgres -l | grep nitilens_db

# Check DATABASE_URL in backend/.env
cat backend/.env | grep DATABASE_URL
```

### Issue: "Redis connection failed"
**Fix:**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Start Redis if not running
redis-server
```

### Issue: "Port 8000 already in use"
**Fix:**
```bash
# Find and kill process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :8000
kill -9 <PID>
```

### Issue: "Module not found"
**Fix:**
```bash
cd backend
# Make sure venv is activated
# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "npm install fails"
**Fix:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Port 5173)                  │
│                  React + TypeScript + Vite              │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                │
│  • REST API                                             │
│  • WebSocket for real-time alerts                      │
│  • JWT Authentication                                   │
│  • Multi-tenant isolation                               │
└─────┬──────────────┬──────────────┬─────────────────────┘
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│PostgreSQL│  │  Redis   │  │Celery Worker │
│(Port 5432)│  │(Port 6379)│  │(Background)  │
└──────────┘  └──────────┘  └──────────────┘
```

---

## 🔐 Security Notes

### Development (Localhost)
- ✅ Default credentials are fine
- ✅ Simple JWT_SECRET is okay
- ✅ HTTP (not HTTPS) is fine
- ✅ Debug mode enabled

### Production
- ⚠️ Change all default passwords
- ⚠️ Use strong JWT_SECRET (32+ chars)
- ⚠️ Enable HTTPS
- ⚠️ Disable debug mode
- ⚠️ Configure firewall
- ⚠️ Use environment variables
- ⚠️ See DEPLOYMENT.md

---

## 📚 Additional Resources

| Document | Description |
|----------|-------------|
| `START-HERE.md` | Quick start guide |
| `RUN-LOCALHOST.md` | Detailed localhost setup |
| `COMMANDS-CHEATSHEET.md` | Quick command reference |
| `TROUBLESHOOTING.md` | Common issues and solutions |
| `QUICKSTART.md` | Feature walkthrough |
| `GOVERNANCE-FEATURES.md` | Feature documentation |
| `DEPLOYMENT.md` | Production deployment |
| `README-ENTERPRISE.md` | Enterprise features |

---

## 🎯 Next Steps After Setup

1. **Explore the Dashboard**
   - View system statistics
   - Check health metrics
   - Review recent activity

2. **Upload Your First Policy**
   - Prepare a compliance PDF
   - Upload via Policies tab
   - Review extracted rules

3. **Connect Your Data**
   - Choose connector type
   - Configure connection
   - Test connectivity

4. **Run Your First Scan**
   - Select policy and dataset
   - Start scan
   - Review violations

5. **Manage Remediation**
   - Review auto-created cases
   - Assign to team members
   - Track resolution

6. **Analyze Risk**
   - View anomaly detection
   - Check risk heatmaps
   - Monitor trends

---

## 🆘 Getting Help

### Check Logs
- Backend: Terminal where uvicorn is running
- Frontend: Terminal where npm run dev is running
- Browser: F12 → Console tab

### API Documentation
- Interactive docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "2.0.0"
}
```

### Still Stuck?
1. Check TROUBLESHOOTING.md
2. Review error messages in terminals
3. Verify all prerequisites are installed
4. Try the manual setup steps
5. Create a GitHub issue with error details

---

## 🎉 Success Checklist

- [ ] PostgreSQL running and database created
- [ ] Redis running and responding to ping
- [ ] Backend started without errors
- [ ] Frontend started without errors
- [ ] Can access http://localhost:5173
- [ ] Can login with admin credentials
- [ ] Dashboard loads successfully
- [ ] API docs accessible at http://localhost:8000/docs

**All checked? You're ready to go! 🚀**

---

## 💡 Pro Tips

1. **Keep terminals open** - Don't close the backend/frontend terminal windows
2. **Check logs first** - Most issues show clear error messages in logs
3. **Use API docs** - http://localhost:8000/docs for testing endpoints
4. **Enable debug mode** - Set `DEBUG=true` in backend/.env for detailed logs
5. **Use virtual environment** - Always activate venv before running Python commands
6. **Clear cache** - If weird errors occur, clear Python/Node caches
7. **Restart services** - Ctrl+C and restart if things get stuck

---

**Happy Compliance Monitoring! 🎊**

For questions or issues, check the documentation or create a GitHub issue.
