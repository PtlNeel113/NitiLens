# Start NitiLens Enterprise Platform Locally
Write-Host "🚀 NitiLens Enterprise Platform - Local Startup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

$hasPython = Get-Command python -ErrorAction SilentlyContinue
$hasNode = Get-Command node -ErrorAction SilentlyContinue

if (-not $hasPython) {
    Write-Host "❌ Python is not installed" -ForegroundColor Red
    Write-Host "Please install Python 3.11+: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

if (-not $hasNode) {
    Write-Host "❌ Node.js is not installed" -ForegroundColor Red
    Write-Host "Please install Node.js 18+: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Python and Node.js found" -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "� Creating .env file from template...C" -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host "⚠️  Please configure DATABASE_URL and REDIS_URL in backend\.env" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}

Write-Host ""

# Install Python dependencies
if (-not (Test-Path "backend\venv")) {
    Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Yellow
    Set-Location backend
    python -m venv venv
    Set-Location ..
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

Write-Host ""
Write-Host "� Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "   (This may take a few minutes on first run)" -ForegroundColor Gray

Set-Location backend
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
}
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..
Write-Host "✅ Python dependencies installed" -ForegroundColor Green

# Install Node dependencies
Write-Host ""
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
    Write-Host "   (This may take a few minutes on first run)" -ForegroundColor Gray
    npm install --silent
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Node.js dependencies" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Node.js dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔍 Checking database and Redis..." -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  IMPORTANT: Ensure the following services are running:" -ForegroundColor Yellow
Write-Host "   1. PostgreSQL on localhost:5432" -ForegroundColor White
Write-Host "      Database: nitilens_db" -ForegroundColor White
Write-Host "      User: nitilens" -ForegroundColor White
Write-Host "      Password: nitilens_password" -ForegroundColor White
Write-Host ""
Write-Host "   2. Redis on localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "   Quick setup commands:" -ForegroundColor Cyan
Write-Host "   PostgreSQL: CREATE DATABASE nitilens_db;" -ForegroundColor Gray
Write-Host "               CREATE USER nitilens WITH PASSWORD 'nitilens_password';" -ForegroundColor Gray
Write-Host "               GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;" -ForegroundColor Gray
Write-Host ""

$continue = Read-Host "Are PostgreSQL and Redis running? (y/n)"
if ($continue -ne "y") {
    Write-Host "❌ Please start PostgreSQL and Redis, then run this script again" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow
Set-Location backend
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
}
python init_db.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Database initialization failed" -ForegroundColor Red
    Write-Host "   Please check your DATABASE_URL in backend\.env" -ForegroundColor Yellow
    Set-Location ..
    exit 1
}

Set-Location ..
Write-Host "✅ Database initialized successfully" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Cyan
Write-Host ""

# Start backend in new window
Write-Host "🔧 Starting Backend API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$PWD\backend'; " + `
    "if (Test-Path venv\Scripts\Activate.ps1) { & .\venv\Scripts\Activate.ps1 }; " + `
    "Write-Host '🔧 Backend API Server' -ForegroundColor Cyan; " + `
    "Write-Host '===================' -ForegroundColor Cyan; " + `
    "Write-Host ''; " + `
    "uvicorn app.main:app --reload --port 8000"

# Wait for backend to start
Start-Sleep -Seconds 5

# Start frontend in new window
Write-Host "🎨 Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$PWD'; " + `
    "Write-Host '🎨 Frontend Development Server' -ForegroundColor Cyan; " + `
    "Write-Host '============================' -ForegroundColor Cyan; " + `
    "Write-Host ''; " + `
    "npm run dev"

Write-Host ""
Write-Host "✅ Services are starting in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🎉 NitiLens Enterprise Platform is running!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Access URLs:" -ForegroundColor Cyan
Write-Host "   Frontend:       http://localhost:5173" -ForegroundColor White
Write-Host "   Backend API:    http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:       http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Health Check:   http://localhost:8000/health" -ForegroundColor White
Write-Host "   Metrics:        http://localhost:8000/metrics" -ForegroundColor White
Write-Host ""
Write-Host "📝 Default Login Credentials:" -ForegroundColor Cyan
Write-Host "   Admin User:" -ForegroundColor Yellow
Write-Host "     Email:    admin@nitilens.com" -ForegroundColor White
Write-Host "     Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "   Demo User:" -ForegroundColor Yellow
Write-Host "     Email:    demo@nitilens.com" -ForegroundColor White
Write-Host "     Password: demo123" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Features Available:" -ForegroundColor Cyan
Write-Host "   ✓ Multi-policy compliance scanning" -ForegroundColor Green
Write-Host "   ✓ Automated remediation engine" -ForegroundColor Green
Write-Host "   ✓ Policy impact analysis" -ForegroundColor Green
Write-Host "   ✓ Predictive risk detection" -ForegroundColor Green
Write-Host "   ✓ Real-time alerts (Email, Slack, WebSocket)" -ForegroundColor Green
Write-Host "   ✓ ERP/CRM connectors" -ForegroundColor Green
Write-Host "   ✓ Multi-language policy processing" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "   • Backend and Frontend are running in separate windows" -ForegroundColor Gray
Write-Host "   • Check those windows for logs and errors" -ForegroundColor Gray
Write-Host "   • Press Ctrl+C in each window to stop services" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   • QUICKSTART.md - Getting started guide" -ForegroundColor Gray
Write-Host "   • GOVERNANCE-FEATURES.md - Feature documentation" -ForegroundColor Gray
Write-Host "   • DEPLOYMENT.md - Production deployment guide" -ForegroundColor Gray
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
