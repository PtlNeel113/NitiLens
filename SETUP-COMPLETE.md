# ✅ NitiLens Localhost Setup - Complete!

## 🎉 What's Been Prepared

Your NitiLens Enterprise Compliance Platform is ready to run on localhost!

---

## 📦 What You Have

### ✅ Complete Application
- **Backend API** - FastAPI with 100+ endpoints
- **Frontend UI** - React + TypeScript + Vite
- **Database Schema** - PostgreSQL with all tables
- **Background Workers** - Celery for async tasks
- **Real-time Alerts** - WebSocket support
- **ML Models** - Anomaly detection ready

### ✅ Enterprise Features
- Multi-policy compliance scanning
- Automated remediation engine
- Policy impact analysis
- Predictive risk detection
- Real-time alerts (Email, Slack, WebSocket)
- ERP/CRM connectors (PostgreSQL, MySQL, MongoDB, REST, CSV)
- Multi-language policy processing
- Multi-tenant architecture
- Role-based access control

### ✅ Startup Scripts
- **start-local.ps1** - Automated Windows startup
- **setup.sh** - Automated Linux/Mac startup
- Both handle full installation and configuration

### ✅ Documentation (16 Files)
1. **HOW-TO-RUN.md** - Main guide (start here!)
2. **QUICK-START-CARD.md** - Quick reference card
3. **START-HERE.md** - Quick start guide
4. **README-LOCALHOST.md** - Detailed localhost setup
5. **RUN-LOCALHOST.md** - Complete running guide
6. **COMMANDS-CHEATSHEET.md** - Command reference
7. **TROUBLESHOOTING.md** - Issue solutions
8. **QUICKSTART.md** - Feature walkthrough
9. **GOVERNANCE-FEATURES.md** - Feature docs
10. **GOVERNANCE-IMPLEMENTATION.md** - Implementation details
11. **IMPLEMENTATION-SUMMARY.md** - Summary
12. **DEPLOYMENT.md** - Production deployment
13. **README-ENTERPRISE.md** - Enterprise features
14. **FEATURES.md** - Feature list
15. **QUICK-REFERENCE-GOVERNANCE.md** - Governance reference
16. **README.md** - Main readme

---

## 🚀 How to Run (3 Simple Steps)

### Step 1: Prerequisites (One-time)
Install these if you haven't:
- Python 3.11+ → https://www.python.org/downloads/
- Node.js 18+ → https://nodejs.org/
- PostgreSQL 15+ → https://www.postgresql.org/download/
- Redis → https://redis.io/download/

### Step 2: Database Setup (30 seconds)
```sql
psql -U postgres
CREATE DATABASE nitilens_db;
CREATE USER nitilens WITH PASSWORD 'nitilens_password';
GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;
\q
```

Start Redis:
```bash
redis-server
```

### Step 3: Run the App (1 minute)
```powershell
# Windows
.\start-local.ps1

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

**That's it!** 🎊

---

## 🌐 Access URLs

Once running:

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |
| **Metrics** | http://localhost:8000/metrics |

---

## 🔐 Login Credentials

**Admin User:**
```
Email:    admin@nitilens.com
Password: admin123
```

**Demo User:**
```
Email:    demo@nitilens.com
Password: demo123
```

---

## 📊 What the Startup Script Does

```
┌─────────────────────────────────────────────────────────┐
│  1. ✅ Check Python & Node.js installed                 │
│  2. ✅ Create .env file from template                   │
│  3. ✅ Create Python virtual environment                │
│  4. ✅ Install Python dependencies (~5 min first time)  │
│  5. ✅ Install Node.js dependencies (~2 min first time) │
│  6. ✅ Initialize PostgreSQL database                   │
│  7. ✅ Seed default users (admin & demo)                │
│  8. ✅ Start backend API server (port 8000)             │
│  9. ✅ Start frontend dev server (port 5173)            │
│ 10. ✅ Open both in separate terminal windows           │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 First Steps After Login

```
1. Explore Dashboard
   └─ View system statistics and health metrics

2. Upload a Policy
   └─ Policies tab → Upload PDF → Rules extracted automatically

3. Add Data Connector
   └─ Connectors tab → Add Connector → Choose type → Configure

4. Run Compliance Scan
   └─ Compliance tab → Select policy & dataset → Scan

5. View Results
   ├─ Violations: All detected violations
   ├─ Remediation: Manage remediation cases
   ├─ Risk: Anomaly detection and risk scores
   └─ Policy Impact: Compare policy versions
```

---

## 🔧 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Browser (localhost:5173)               │
│              React + TypeScript + Vite                  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────┐
│           FastAPI Backend (localhost:8000)              │
│  • REST API (100+ endpoints)                            │
│  • WebSocket for real-time alerts                       │
│  • JWT Authentication                                   │
│  • Multi-tenant isolation                               │
│  • Background task scheduler                            │
└─────┬──────────────┬──────────────┬─────────────────────┘
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│PostgreSQL│  │  Redis   │  │Celery Worker │
│  :5432   │  │  :6379   │  │ (Background) │
│          │  │          │  │              │
│ • Users  │  │ • Cache  │  │ • Email      │
│ • Policies│ │ • Sessions│ │ • Alerts     │
│ • Rules  │  │ • Queues │  │ • Scans      │
│ • Violations│ │        │  │              │
└──────────┘  └──────────┘  └──────────────┘
```

---

## 📚 Documentation Quick Reference

**Getting Started:**
- Start with **HOW-TO-RUN.md** (this is the main guide)
- Quick reference: **QUICK-START-CARD.md**
- Detailed setup: **README-LOCALHOST.md**

**Commands:**
- **COMMANDS-CHEATSHEET.md** - All commands in one place

**Troubleshooting:**
- **TROUBLESHOOTING.md** - Common issues and fixes

**Features:**
- **GOVERNANCE-FEATURES.md** - Feature documentation
- **QUICKSTART.md** - Feature walkthrough

**Production:**
- **DEPLOYMENT.md** - Production deployment guide

---

## ✨ Available Features

### Core Compliance
- ✅ Multi-policy support with versioning
- ✅ PDF policy upload and rule extraction
- ✅ Multi-language policy processing
- ✅ Rule-based violation detection
- ✅ Compliance scanning engine

### Automated Remediation
- ✅ Auto-case creation on violation
- ✅ Smart assignment based on severity
- ✅ Escalation tracking
- ✅ Comment threads
- ✅ Due date management

### Policy Impact Analysis
- ✅ Version comparison
- ✅ Threshold change detection
- ✅ Impact reports
- ✅ Risk delta calculation
- ✅ Automatic re-scanning

### Predictive Risk
- ✅ ML-based anomaly detection
- ✅ Isolation Forest algorithm
- ✅ Combined risk scoring
- ✅ Risk heatmaps
- ✅ Trend analysis

### Real-time Alerts
- ✅ WebSocket notifications
- ✅ Email alerts (SendGrid)
- ✅ Slack integration
- ✅ Severity-based routing

### Data Connectors
- ✅ PostgreSQL connector
- ✅ MySQL connector
- ✅ MongoDB connector
- ✅ REST API connector
- ✅ CSV upload

### Enterprise Features
- ✅ Multi-tenant architecture
- ✅ Role-based access control
- ✅ Subscription plans
- ✅ Usage limits
- ✅ Production monitoring
- ✅ Health checks
- ✅ Prometheus metrics

---

## 🎓 Learning Path

```
Day 1: Setup & Basics
├─ Run the application
├─ Explore the dashboard
├─ Upload a sample policy
└─ Review extracted rules

Day 2: Data Integration
├─ Add a data connector
├─ Test connection
├─ Import sample data
└─ Run first scan

Day 3: Compliance Workflow
├─ Review violations
├─ Manage remediation cases
├─ Assign to team members
└─ Track resolution

Day 4: Advanced Features
├─ Policy impact analysis
├─ Anomaly detection
├─ Risk scoring
└─ Alert configuration

Day 5: Production Ready
├─ Configure email/Slack
├─ Setup scheduled scans
├─ Review monitoring
└─ Plan deployment
```

---

## 🐛 Common Issues (Quick Fixes)

### Database Error
```bash
# Check PostgreSQL running
psql -U postgres -c "SELECT 1"

# Reinitialize if needed
cd backend && python init_db.py
```

### Redis Error
```bash
# Check Redis running
redis-cli ping

# Start if not running
redis-server
```

### Port In Use
```bash
# Find and kill process
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -i :8000
```

### Module Not Found
```bash
# Activate venv and reinstall
cd backend
# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

---

## 🎯 Success Checklist

Before you start, verify:

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL 15+ installed and running
- [ ] Redis installed and running
- [ ] Database `nitilens_db` created
- [ ] User `nitilens` created with permissions

After running script, verify:

- [ ] Backend started without errors (port 8000)
- [ ] Frontend started without errors (port 5173)
- [ ] Can access http://localhost:5173
- [ ] Can login with admin@nitilens.com / admin123
- [ ] Dashboard loads successfully
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Health check returns "healthy"

**All checked? Perfect! You're ready to go! 🚀**

---

## 💡 Pro Tips

1. **Keep terminals open** - Backend and frontend run in separate windows
2. **Check logs first** - Most errors show clear messages in terminals
3. **Use API docs** - http://localhost:8000/docs for testing endpoints
4. **Activate venv** - Always activate before running Python commands
5. **Clear cache** - If weird errors, clear Python/Node caches
6. **Restart services** - Ctrl+C and restart if things get stuck
7. **Read docs** - Check documentation for detailed guides

---

## 🆘 Need Help?

1. **Check TROUBLESHOOTING.md** - Common issues and solutions
2. **Review terminal logs** - Error messages show in terminal windows
3. **Test health endpoint** - http://localhost:8000/health
4. **Check API docs** - http://localhost:8000/docs
5. **Verify prerequisites** - Ensure all tools installed correctly
6. **Try manual setup** - If script fails, follow manual steps
7. **Create GitHub issue** - Include error details and logs

---

## 🎊 You're All Set!

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     🎉 NITILENS ENTERPRISE PLATFORM READY! 🎉           ║
║                                                          ║
║  Everything is configured and ready to run!             ║
║                                                          ║
║  Next Step: Run .\start-local.ps1 (Windows)            ║
║             or ./setup.sh (Linux/Mac)                   ║
║                                                          ║
║  Then open: http://localhost:5173                       ║
║  Login: admin@nitilens.com / admin123                   ║
║                                                          ║
║  Happy Compliance Monitoring! 🚀                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

**Start with HOW-TO-RUN.md for step-by-step instructions!**
