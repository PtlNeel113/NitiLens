# 🚀 Running NitiLens on Localhost

Complete guide to run the NitiLens Enterprise Compliance Platform on your local machine.

## 📋 Prerequisites Checklist

Before you begin, install these required tools:

- [ ] **Python 3.11+** → [Download](https://www.python.org/downloads/)
- [ ] **Node.js 18+** → [Download](https://nodejs.org/)
- [ ] **PostgreSQL 15+** → [Download](https://www.postgresql.org/download/)
- [ ] **Redis** → [Download](https://redis.io/download/)

### Verify Installation

```bash
python --version    # Should show 3.11 or higher
node --version      # Should show 18 or higher
psql --version      # Should show 15 or higher
redis-cli --version # Should show Redis version
```

## 🎯 Quick Start (Automated)

### Windows Users

```powershell
.\start-local.ps1
```

### Linux/Mac Users

```bash
chmod +x setup.sh
./setup.sh
```

The script will automatically:
1. Check prerequisites
2. Install Python dependencies
3. Install Node.js dependencies
4. Initialize the database
5. Start backend and frontend servers

**That's it!** Skip to the [Access Application](#-access-application) section.

---

## 🔧 Manual Setup (Step-by-Step)

If you prefer manual control or the automated script fails:

### Step 1: Setup PostgreSQL Database

Start PostgreSQL and create the database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Run these commands in psql:
CREATE DATABASE nitilens_db;
CREATE USER nitilens WITH PASSWORD 'nitilens_password';
GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;
\q
```

### Step 2: Start Redis Server

```bash
# Windows (if installed via Chocolatey or MSI)
redis-server

# Linux
sudo systemctl start redis
sudo systemctl enable redis

# Mac (via Homebrew)
brew services start redis

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### Step 3: Configure Environment Variables

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with your settings:

```env
# Database
DATABASE_URL=postgresql://nitilens:nitilens_password@localhost:5432/nitilens_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret (generate a secure random string)
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Optional: Email notifications
EMAIL_API_KEY=your-sendgrid-api-key
EMAIL_FROM=noreply@nitilens.com

# Optional: Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Environment
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Step 4: Install Backend Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Note:** This may take 5-10 minutes on first install due to ML libraries (scikit-learn, torch, transformers).

### Step 5: Install Frontend Dependencies

```bash
# From project root
npm install
```

### Step 6: Initialize Database

```bash
cd backend

# Make sure virtual environment is activated
python init_db.py
```

You should see:
```
🔧 Initializing database...
📊 Creating tables...
✅ Tables created successfully
🌱 Seeding default data...
✅ Default data seeded successfully

📝 Default credentials:
   Admin: admin@nitilens.com / admin123
   Demo:  demo@nitilens.com / demo123

✅ Database initialization complete!
```

### Step 7: Start Backend Server

```bash
cd backend

# Activate virtual environment if not already active
# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Start backend
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
🚀 NitiLens Enterprise Platform started
📊 Environment: development
📚 API Documentation: http://localhost:8000/docs
```

### Step 8: Start Frontend Server

Open a **new terminal** window:

```bash
# From project root
npm run dev
```

You should see:
```
VITE v6.3.5  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

## 🌐 Access Application

Once both servers are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main application UI |
| **Backend API** | http://localhost:8000 | REST API server |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | System health status |
| **Metrics** | http://localhost:8000/metrics | Prometheus metrics |

## 🔐 Login Credentials

### Admin User (Full Access)
- **Email:** `admin@nitilens.com`
- **Password:** `admin123`
- **Role:** Super Admin

### Demo User (Limited Access)
- **Email:** `demo@nitilens.com`
- **Password:** `demo123`
- **Role:** Compliance Admin

---

## ✨ Available Features

Once logged in, you can access:

### 1. Policy Management
- Upload compliance policies (PDF)
- Multi-language support
- Version control
- Policy comparison

### 2. Data Connectors
- PostgreSQL
- MySQL
- MongoDB
- REST API
- CSV Upload

### 3. Compliance Scanning
- Multi-policy scanning
- Rule-based detection
- Anomaly detection
- Risk scoring

### 4. Remediation Engine
- Auto-assignment
- Case management
- Escalation tracking
- Comment threads

### 5. Risk Analytics
- Anomaly detection
- Risk heatmaps
- Trend analysis
- Predictive scoring

### 6. Policy Impact Analysis
- Version comparison
- Impact reports
- Threshold changes
- Risk delta calculation

### 7. Real-time Alerts
- WebSocket notifications
- Email alerts
- Slack integration

---

## 🔄 Optional: Background Worker

For async tasks (email, Slack, scheduled scans):

Open a **third terminal** window:

```bash
cd backend

# Activate virtual environment
# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Start Celery worker
celery -A app.worker worker --loglevel=info
```

---

## 🛠️ Development Workflow

### Making Code Changes

**Backend changes:**
- Edit files in `backend/app/`
- Server auto-reloads (thanks to `--reload` flag)
- Check terminal for errors

**Frontend changes:**
- Edit files in `src/`
- Vite auto-reloads
- Check browser console for errors

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
npm test
```

### Database Migrations

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Viewing Logs

**Backend logs:** Check the terminal where `uvicorn` is running

**Frontend logs:** 
- Terminal where `npm run dev` is running
- Browser console (F12 → Console)

**Database logs:** Check PostgreSQL logs

**Redis logs:** Check Redis server output

---

## 🐛 Troubleshooting

### Backend won't start

1. **Check PostgreSQL is running:**
   ```bash
   psql -U postgres -c "SELECT 1"
   ```

2. **Check Redis is running:**
   ```bash
   redis-cli ping
   ```

3. **Verify DATABASE_URL in .env**

4. **Check for port conflicts:**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

### Frontend won't start

1. **Clear node_modules:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Check for port conflicts:**
   ```bash
   # Windows
   netstat -ano | findstr :5173
   
   # Linux/Mac
   lsof -i :5173
   ```

### Database connection errors

1. **Verify PostgreSQL is running**
2. **Check credentials in .env**
3. **Ensure database exists:**
   ```bash
   psql -U postgres -l | grep nitilens_db
   ```

### Module not found errors

1. **Activate virtual environment:**
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

For more troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🔒 Security Notes

For local development:
- Default credentials are fine
- JWT_SECRET can be simple
- HTTPS not required

For production:
- Change all default passwords
- Use strong JWT_SECRET
- Enable HTTPS
- Configure firewall rules
- See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📚 Next Steps

1. **Upload a Policy**
   - Go to Policies tab
   - Click "Upload Policy"
   - Select a PDF compliance document

2. **Add a Data Source**
   - Go to Connectors tab
   - Click "Add Connector"
   - Configure your data source

3. **Run a Scan**
   - Go to Compliance tab
   - Select policy and dataset
   - Click "Scan"

4. **View Results**
   - Check Violations tab
   - Review Remediation cases
   - Analyze Risk metrics

---

## 🆘 Getting Help

- **Documentation:** Check other .md files in project root
- **API Docs:** http://localhost:8000/docs
- **Logs:** Check terminal windows for errors
- **Issues:** Create GitHub issue with error details

---

## 🎉 Success!

If you see:
- ✅ Frontend at http://localhost:5173
- ✅ Backend at http://localhost:8000
- ✅ Can login with admin credentials
- ✅ Dashboard loads without errors

**You're all set! Happy compliance monitoring!** 🚀
