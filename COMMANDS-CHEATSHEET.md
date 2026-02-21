# ⚡ Quick Commands Cheatsheet

## 🚀 One-Command Start

### Windows
```powershell
.\start-local.ps1
```

### Linux/Mac
```bash
./setup.sh
```

---

## 📦 First Time Setup

### 1. Database Setup
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE nitilens_db;
CREATE USER nitilens WITH PASSWORD 'nitilens_password';
GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;
\q
```

### 2. Start Redis
```bash
redis-server
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python init_db.py
```

### 4. Frontend Setup
```bash
npm install
```

---

## 🏃 Daily Startup

### Terminal 1: Backend
```bash
cd backend
# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
npm run dev
```

### Terminal 3: Worker (Optional)
```bash
cd backend
# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
celery -A app.worker worker --loglevel=info
```

---

## 🔍 Health Checks

```bash
# Check backend
curl http://localhost:8000/health

# Check Redis
redis-cli ping

# Check PostgreSQL
psql -U nitilens -d nitilens_db -c "SELECT 1"

# Check frontend
curl http://localhost:5173
```

---

## 🛠️ Useful Commands

### Database

```bash
# Reset database
cd backend
python init_db.py

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Connect to database
psql -U nitilens -d nitilens_db
```

### Dependencies

```bash
# Update Python packages
cd backend
pip install --upgrade -r requirements.txt

# Update Node packages
npm update

# Add new Python package
pip install package-name
pip freeze > requirements.txt

# Add new Node package
npm install package-name
```

### Logs & Debugging

```bash
# View backend logs (in uvicorn terminal)
# Logs appear automatically

# View Celery logs (in worker terminal)
# Logs appear automatically

# View PostgreSQL logs
# Windows: C:\Program Files\PostgreSQL\15\data\log\
# Linux: /var/log/postgresql/
# Mac: /usr/local/var/log/postgres.log

# View Redis logs
redis-cli monitor
```

### Cleanup

```bash
# Stop all services
# Press Ctrl+C in each terminal

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Clear Node cache
rm -rf node_modules package-lock.json
npm install

# Clear Redis data
redis-cli FLUSHALL

# Drop database
psql -U postgres -c "DROP DATABASE nitilens_db"
```

---

## 🐳 Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend

# Rebuild specific service
docker-compose up --build backend

# Remove all containers and volumes
docker-compose down -v
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
npm test

# Run specific test
pytest tests/test_compliance.py

# Coverage report
pytest --cov=app tests/
```

---

## 📊 Monitoring

```bash
# View metrics
curl http://localhost:8000/metrics

# Check API health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs

# Monitor Redis
redis-cli INFO

# Monitor PostgreSQL
psql -U nitilens -d nitilens_db -c "SELECT * FROM pg_stat_activity"
```

---

## 🔧 Port Management

```bash
# Find process using port
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Kill process
# Windows
taskkill /PID <PID> /F

# Linux/Mac
kill -9 <PID>

# Use different ports
uvicorn app.main:app --reload --port 8001
npm run dev -- --port 5174
```

---

## 🔐 User Management

```bash
# Create new user (Python shell)
cd backend
python

>>> from app.database import SessionLocal
>>> from app.models.db_models import User
>>> from app.auth import get_password_hash
>>> db = SessionLocal()
>>> user = User(
...     email="user@example.com",
...     hashed_password=get_password_hash("password"),
...     full_name="New User",
...     org_id="<org_id>",
...     role="REVIEWER"
... )
>>> db.add(user)
>>> db.commit()
>>> exit()
```

---

## 🎯 Quick Access URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |
| Metrics | http://localhost:8000/metrics |

---

## 🔑 Default Credentials

**Admin:**
- Email: `admin@nitilens.com`
- Password: `admin123`

**Demo:**
- Email: `demo@nitilens.com`
- Password: `demo123`

---

## 💡 Pro Tips

```bash
# Run backend in background (Linux/Mac)
nohup uvicorn app.main:app --port 8000 > backend.log 2>&1 &

# Run frontend in background (Linux/Mac)
nohup npm run dev > frontend.log 2>&1 &

# Watch logs in real-time
tail -f backend.log
tail -f frontend.log

# Create alias for quick start (add to .bashrc or .zshrc)
alias nitilens-start="cd ~/nitilens && ./start-local.ps1"

# Environment variables shortcut
export DATABASE_URL="postgresql://nitilens:nitilens_password@localhost:5432/nitilens_db"
export REDIS_URL="redis://localhost:6379/0"
```

---

**Keep this cheatsheet handy for quick reference!** 📌
