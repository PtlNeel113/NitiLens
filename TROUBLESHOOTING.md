# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. Database Connection Failed

**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solutions:**

1. **Check PostgreSQL is running:**
   ```bash
   # Windows
   Get-Service postgresql*
   
   # Linux/Mac
   sudo systemctl status postgresql
   ```

2. **Verify database exists:**
   ```sql
   psql -U postgres
   \l  -- List all databases
   ```

3. **Create database if missing:**
   ```sql
   CREATE DATABASE nitilens_db;
   CREATE USER nitilens WITH PASSWORD 'nitilens_password';
   GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;
   ```

4. **Check DATABASE_URL in backend/.env:**
   ```
   DATABASE_URL=postgresql://nitilens:nitilens_password@localhost:5432/nitilens_db
   ```

### 2. Redis Connection Failed

**Error:** `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solutions:**

1. **Check Redis is running:**
   ```bash
   # Windows
   redis-cli ping
   
   # Linux/Mac
   redis-cli ping
   # Should return: PONG
   ```

2. **Start Redis:**
   ```bash
   # Windows (if installed)
   redis-server
   
   # Linux
   sudo systemctl start redis
   
   # Mac
   brew services start redis
   ```

3. **Check REDIS_URL in backend/.env:**
   ```
   REDIS_URL=redis://localhost:6379/0
   ```

### 3. Port Already in Use

**Error:** `OSError: [Errno 48] Address already in use`

**Solutions:**

1. **Find process using the port:**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

2. **Kill the process:**
   ```bash
   # Windows
   taskkill /PID <PID> /F
   
   # Linux/Mac
   kill -9 <PID>
   ```

3. **Use different port:**
   ```bash
   # Backend
   uvicorn app.main:app --reload --port 8001
   
   # Frontend
   npm run dev -- --port 5174
   ```

### 4. Module Not Found Errors

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solutions:**

1. **Activate virtual environment:**
   ```bash
   # Windows
   cd backend
   .\venv\Scripts\activate
   
   # Linux/Mac
   cd backend
   source venv/bin/activate
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check Python version:**
   ```bash
   python --version
   # Should be 3.11 or higher
   ```

### 5. Frontend Build Errors

**Error:** `Cannot find module` or `npm ERR!`

**Solutions:**

1. **Clear node_modules and reinstall:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Clear npm cache:**
   ```bash
   npm cache clean --force
   npm install
   ```

3. **Check Node version:**
   ```bash
   node --version
   # Should be 18 or higher
   ```

### 6. CORS Errors

**Error:** `Access to fetch blocked by CORS policy`

**Solutions:**

1. **Check CORS_ORIGINS in backend/.env:**
   ```
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

2. **Restart backend server** after changing .env

3. **Clear browser cache** and reload

### 7. Authentication Errors

**Error:** `401 Unauthorized` or `Invalid credentials`

**Solutions:**

1. **Verify database is initialized:**
   ```bash
   cd backend
   python init_db.py
   ```

2. **Use correct credentials:**
   - Admin: `admin@nitilens.com` / `admin123`
   - Demo: `demo@nitilens.com` / `demo123`

3. **Check JWT_SECRET in backend/.env** is set

### 8. File Upload Errors

**Error:** `413 Request Entity Too Large`

**Solutions:**

1. **Check file size limits** in backend configuration

2. **For large PDFs**, split into smaller files

3. **Increase upload limit** in `app/main.py`:
   ```python
   app.add_middleware(
       ...,
       max_upload_size=50 * 1024 * 1024  # 50MB
   )
   ```

### 9. Slow Performance

**Solutions:**

1. **Check database indexes:**
   ```sql
   -- Run in PostgreSQL
   SELECT * FROM pg_indexes WHERE tablename = 'violations';
   ```

2. **Monitor Redis memory:**
   ```bash
   redis-cli info memory
   ```

3. **Enable database connection pooling** (already configured)

4. **Use pagination** for large datasets

### 10. Worker/Celery Not Starting

**Error:** `celery.exceptions.ImproperlyConfigured`

**Solutions:**

1. **Check Celery broker URL:**
   ```
   CELERY_BROKER_URL=redis://localhost:6379/1
   ```

2. **Start worker manually:**
   ```bash
   cd backend
   celery -A app.worker worker --loglevel=info
   ```

3. **Check Redis is running** (worker requires Redis)

## Environment-Specific Issues

### Windows

1. **PowerShell Execution Policy:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Long path issues:**
   Enable long paths in Windows:
   ```
   Computer Configuration > Administrative Templates > System > Filesystem > Enable Win32 long paths
   ```

### Linux/Mac

1. **Permission denied:**
   ```bash
   chmod +x setup.sh
   chmod +x start-local.sh
   ```

2. **Python not found:**
   ```bash
   # Use python3 explicitly
   python3 -m venv venv
   ```

## Checking Service Health

### Backend Health Check

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

### Frontend Health Check

Open browser to: http://localhost:5173

Should see the NitiLens login page.

### Database Connection Test

```bash
cd backend
python -c "from app.database import engine; print(engine.connect())"
```

### Redis Connection Test

```bash
redis-cli ping
# Should return: PONG
```

## Logs and Debugging

### View Backend Logs

Backend logs appear in the terminal where you ran:
```bash
uvicorn app.main:app --reload --port 8000
```

### View Frontend Logs

Frontend logs appear in:
1. Terminal where you ran `npm run dev`
2. Browser console (F12 → Console tab)

### Enable Debug Mode

In `backend/.env`:
```
DEBUG=true
ENVIRONMENT=development
```

### Database Query Logging

In `backend/app/database.py`:
```python
engine = create_engine(DATABASE_URL, echo=True)  # Add echo=True
```

## Getting Help

If issues persist:

1. **Check API documentation:** http://localhost:8000/docs
2. **Review error logs** in terminal windows
3. **Check GitHub issues:** [Project Repository]
4. **Verify all prerequisites** are installed correctly

## Reset Everything

If all else fails, complete reset:

```bash
# Stop all services
# Ctrl+C in all terminal windows

# Remove virtual environment
rm -rf backend/venv

# Remove node_modules
rm -rf node_modules

# Drop and recreate database
psql -U postgres
DROP DATABASE nitilens_db;
CREATE DATABASE nitilens_db;
\q

# Restart from setup
.\start-local.ps1  # Windows
./setup.sh         # Linux/Mac
```

---

**Still having issues? Check the documentation or create an issue on GitHub.**
