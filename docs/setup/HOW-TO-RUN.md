# 🎯 How to Run NitiLens on Localhost

## ⚡ TL;DR - Fastest Way

```bash
# 1. Setup database (30 sec)
psql -U postgres -c "CREATE DATABASE nitilens_db; CREATE USER nitilens WITH PASSWORD 'nitilens_password'; GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;"

# 2. Start Redis (10 sec)
redis-server &

# 3. Run the app (1 min)
.\start-local.ps1    # Windows
./setup.sh           # Linux/Mac

# 4. Open browser
# http://localhost:5173
# Login: admin@nitilens.com / admin123
```

**Total time: ~2 minutes** ⏱️

---

## 📋 Prerequisites (Install First)

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.11+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| PostgreSQL | 15+ | https://www.postgresql.org/download/ |
| Redis | Latest | https://redis.io/download/ |

**Verify installation:**
```bash
python --version    # Should show 3.11+
node --version      # Should show 18+
psql --version      # Should show 15+
redis-cli --version # Should show Redis version
```

---

## 🚀 Method 1: Automated (Recommended)

### Windows

1. **Open PowerShell** in project directory
2. **Run:**
   ```powershell
   .\start-local.ps1
   ```
3. **Follow prompts** to confirm PostgreSQL and Redis are running
4. **Wait** for installation and startup (~5 min first time)
5. **Done!** Browser opens automatically

### Linux/Mac

1. **Open Terminal** in project directory
2. **Run:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. **Follow prompts** to confirm PostgreSQL and Redis are running
4. **Wait** for installation and startup (~5 min first time)
5. **Done!** Browser opens automatically

---

## 🔧 Method 2: Manual (If Script Fails)

### Step 1: Database Setup
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE nitilens_db;
CREATE USER nitilens WITH PASSWORD 'nitilens_password';
GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;
\q
```

### Step 2: Start Redis
```bash
# Start Redis server
redis-server

# Verify it's running (in new terminal)
redis-cli ping
# Should return: PONG
```

### Step 3: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Initialize database
python init_db.py
```

### Step 4: Frontend Setup
```bash
# From project root
npm install
```

### Step 5: Start Backend
```bash
cd backend

# Activate virtual environment (if not already)
# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Start server
uvicorn app.main:app --reload --port 8000
```

**Keep this terminal open!**

### Step 6: Start Frontend
```bash
# Open NEW terminal in project root
npm run dev
```

**Keep this terminal open too!**

---

## 🌐 Access the Application

Once running, open your browser to:

**Main Application:**
http://localhost:5173

**API Documentation:**
http://localhost:8000/docs

**Health Check:**
http://localhost:8000/health

---

## 🔐 Login

Use these credentials:

**Admin User (Full Access):**
- Email: `admin@nitilens.com`
- Password: `admin123`

**Demo User (Limited Access):**
- Email: `demo@nitilens.com`
- Password: `demo123`

---

## ✅ Verify Everything Works

### 1. Check Backend
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

### 2. Check Frontend
Open http://localhost:5173 - should see login page

### 3. Check Database
```bash
psql -U nitilens -d nitilens_db -c "SELECT COUNT(*) FROM users;"
```

Should show 2 users (admin and demo)

### 4. Check Redis
```bash
redis-cli ping
```

Should return: `PONG`

---

## 🎮 First Steps After Login

### 1. Explore Dashboard
- View system statistics
- Check recent activity
- Review health metrics

### 2. Upload a Policy
- Click **Policies** in sidebar
- Click **Upload Policy** button
- Select a PDF compliance document
- Wait for rule extraction

### 3. Add Data Connector
- Click **Connectors** in sidebar
- Click **Add Connector** button
- Choose type (PostgreSQL, MySQL, MongoDB, REST API, CSV)
- Enter connection details
- Test connection

### 4. Run Compliance Scan
- Click **Compliance** in sidebar
- Select policy from dropdown
- Select dataset from dropdown
- Click **Scan Dataset**
- Wait for results

### 5. View Results
- **Violations Tab:** All detected violations
- **Remediation Tab:** Manage remediation cases
- **Risk Tab:** Anomaly detection and risk scores
- **Policy Impact Tab:** Compare policy versions

---

## 🐛 Troubleshooting

### Backend won't start

**Error:** Database connection failed

**Fix:**
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Check database exists
psql -U postgres -l | grep nitilens_db

# Verify DATABASE_URL in backend/.env
cat backend/.env | grep DATABASE_URL
```

---

**Error:** Redis connection failed

**Fix:**
```bash
# Check Redis is running
redis-cli ping

# Start Redis if not running
redis-server
```

---

**Error:** Port 8000 already in use

**Fix:**
```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :8000
kill -9 <PID>
```

---

### Frontend won't start

**Error:** Port 5173 already in use

**Fix:**
```bash
# Use different port
npm run dev -- --port 5174
```

---

**Error:** Module not found

**Fix:**
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

### Can't login

**Fix:**
```bash
# Reinitialize database
cd backend
python init_db.py
```

---

## 🛑 Stopping the Application

1. **Press Ctrl+C** in backend terminal
2. **Press Ctrl+C** in frontend terminal
3. **Stop Redis** (optional):
   ```bash
   redis-cli shutdown
   ```

---

## 🔄 Restarting the Application

### Quick Restart (after first setup)

**Terminal 1:**
```bash
cd backend
# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2:**
```bash
npm run dev
```

### Full Restart (with script)

```bash
.\start-local.ps1    # Windows
./setup.sh           # Linux/Mac
```

---

## 📚 Documentation Guide

| Document | When to Use |
|----------|-------------|
| **QUICK-START-CARD.md** | Quick reference card |
| **START-HERE.md** | First time setup |
| **README-LOCALHOST.md** | Detailed localhost guide |
| **COMMANDS-CHEATSHEET.md** | Command reference |
| **TROUBLESHOOTING.md** | When things break |
| **GOVERNANCE-FEATURES.md** | Feature documentation |
| **DEPLOYMENT.md** | Production deployment |

---

## 💡 Pro Tips

1. **Keep terminals open** - Don't close backend/frontend windows
2. **Check logs first** - Errors show in terminal windows
3. **Use API docs** - http://localhost:8000/docs for testing
4. **Activate venv** - Always activate before Python commands
5. **Clear cache** - If weird errors, clear Python/Node caches
6. **Restart services** - Ctrl+C and restart if stuck

---

## 🎯 Success Checklist

- [ ] PostgreSQL running
- [ ] Redis running
- [ ] Database created and initialized
- [ ] Backend started (port 8000)
- [ ] Frontend started (port 5173)
- [ ] Can access http://localhost:5173
- [ ] Can login with admin credentials
- [ ] Dashboard loads without errors
- [ ] API docs accessible

**All checked? You're ready! 🎉**

---

## 🆘 Still Need Help?

1. **Check logs** in terminal windows
2. **Review TROUBLESHOOTING.md**
3. **Test health endpoint:** http://localhost:8000/health
4. **Check API docs:** http://localhost:8000/docs
5. **Verify prerequisites** are installed correctly
6. **Try manual setup** if script fails
7. **Create GitHub issue** with error details

---

## 🎊 You're All Set!

The NitiLens Enterprise Compliance Platform is now running on your localhost.

**Next:** Start exploring features, upload policies, connect data sources, and run compliance scans!

**Happy Compliance Monitoring! 🚀**
