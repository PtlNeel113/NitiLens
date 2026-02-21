# NitiLens Enterprise Setup Script for Windows
# PowerShell script for automated installation

Write-Host "🚀 NitiLens Enterprise SaaS Platform Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

$hasDocker = Get-Command docker -ErrorAction SilentlyContinue
$hasPython = Get-Command python -ErrorAction SilentlyContinue
$hasNode = Get-Command node -ErrorAction SilentlyContinue

if (-not $hasDocker) {
    Write-Host "❌ Docker is not installed" -ForegroundColor Red
    Write-Host "Please install Docker Desktop: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
    exit 1
}

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

Write-Host "✅ All prerequisites met" -ForegroundColor Green
Write-Host ""

# Create .env file if it doesn't exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "📝 Creating environment configuration..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    
    # Generate random JWT secret
    $bytes = New-Object byte[] 32
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $JWT_SECRET = [Convert]::ToBase64String($bytes)
    
    # Update .env with generated secret
    (Get-Content "backend\.env") -replace 'your-super-secret-jwt-key-change-in-production', $JWT_SECRET | Set-Content "backend\.env"
    
    Write-Host "✅ Environment file created" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Using existing .env file" -ForegroundColor Cyan
}

Write-Host ""

# Ask user for installation method
Write-Host "Choose installation method:" -ForegroundColor Cyan
Write-Host "1) Docker (Recommended - Full stack with one command)" -ForegroundColor White
Write-Host "2) Local Development (Manual setup for development)" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Enter choice [1-2]"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🐳 Starting Docker installation..." -ForegroundColor Cyan
        Write-Host ""
        
        # Check if Docker is running
        try {
            docker ps | Out-Null
        } catch {
            Write-Host "❌ Docker is not running" -ForegroundColor Red
            Write-Host "Please start Docker Desktop and try again" -ForegroundColor Yellow
            exit 1
        }
        
        # Build and start containers
        Write-Host "📦 Building containers..." -ForegroundColor Yellow
        docker-compose build
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Docker build failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "🚀 Starting services..." -ForegroundColor Yellow
        docker-compose up -d
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Docker start failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15
        
        # Check if services are running
        $running = docker-compose ps --services --filter "status=running"
        
        if ($running) {
            Write-Host "✅ All services started successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "📊 Service URLs:" -ForegroundColor Cyan
            Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor White
            Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
            Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor White
            Write-Host "   Health:    http://localhost:8000/health" -ForegroundColor White
            Write-Host ""
            Write-Host "📝 Default credentials:" -ForegroundColor Cyan
            Write-Host "   Admin: admin@nitilens.com / admin123" -ForegroundColor White
            Write-Host "   Demo:  demo@nitilens.com / demo123" -ForegroundColor White
            Write-Host ""
            Write-Host "🛠️  Useful commands:" -ForegroundColor Cyan
            Write-Host "   View logs:     docker-compose logs -f" -ForegroundColor White
            Write-Host "   Stop services: docker-compose down" -ForegroundColor White
            Write-Host "   Restart:       docker-compose restart" -ForegroundColor White
        } else {
            Write-Host "❌ Some services failed to start" -ForegroundColor Red
            Write-Host "Check logs with: docker-compose logs" -ForegroundColor Yellow
            exit 1
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "🔧 Setting up local development environment..." -ForegroundColor Cyan
        Write-Host ""
        
        # Install Python dependencies
        Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
        Set-Location backend
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Python dependencies installation failed" -ForegroundColor Red
            Set-Location ..
            exit 1
        }
        
        Set-Location ..
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
        
        # Install Node dependencies
        Write-Host ""
        Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
        npm install
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Node.js dependencies installation failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
        
        # Setup instructions
        Write-Host ""
        Write-Host "🐘 PostgreSQL Setup" -ForegroundColor Cyan
        Write-Host "Please ensure PostgreSQL is running and create database:" -ForegroundColor Yellow
        Write-Host "  CREATE DATABASE nitilens_db;" -ForegroundColor White
        Write-Host "  CREATE USER nitilens WITH PASSWORD 'nitilens_password';" -ForegroundColor White
        Write-Host "  GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter when PostgreSQL is ready..."
        
        Write-Host ""
        Write-Host "📮 Redis Setup" -ForegroundColor Cyan
        Write-Host "Please ensure Redis is running on localhost:6379" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter when Redis is ready..."
        
        # Initialize database
        Write-Host ""
        Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow
        Set-Location backend
        python init_db.py
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Database initialization failed" -ForegroundColor Red
            Set-Location ..
            exit 1
        }
        
        Set-Location ..
        Write-Host "✅ Database initialized" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "✅ Local setup complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🚀 To start the application:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Terminal 1 (Backend):" -ForegroundColor Yellow
        Write-Host "  cd backend" -ForegroundColor White
        Write-Host "  uvicorn app.main:app --reload --port 8000" -ForegroundColor White
        Write-Host ""
        Write-Host "Terminal 2 (Frontend):" -ForegroundColor Yellow
        Write-Host "  npm run dev" -ForegroundColor White
        Write-Host ""
        Write-Host "Terminal 3 (Worker - Optional):" -ForegroundColor Yellow
        Write-Host "  cd backend" -ForegroundColor White
        Write-Host "  celery -A app.worker worker --loglevel=info" -ForegroundColor White
        Write-Host ""
        Write-Host "📊 Access URLs:" -ForegroundColor Cyan
        Write-Host "   Frontend:  http://localhost:5173" -ForegroundColor White
        Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
        Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor White
        Write-Host ""
        Write-Host "📝 Default credentials:" -ForegroundColor Cyan
        Write-Host "   Admin: admin@nitilens.com / admin123" -ForegroundColor White
        Write-Host "   Demo:  demo@nitilens.com / demo123" -ForegroundColor White
    }
    
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎉 Setup complete! Welcome to NitiLens Enterprise!" -ForegroundColor Green
Write-Host ""
