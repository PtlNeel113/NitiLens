# Quick start with Docker
Write-Host "🚀 Starting NitiLens with Docker..." -ForegroundColor Cyan

# Check if Docker is running
try {
    docker ps | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Create .env if needed
if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "✅ Created .env file" -ForegroundColor Green
}

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "✅ Services started!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Access URLs:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📝 Login:" -ForegroundColor Cyan
Write-Host "   Email: admin@nitilens.com" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "View logs: docker-compose logs -f" -ForegroundColor Yellow
