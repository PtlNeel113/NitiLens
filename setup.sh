#!/bin/bash

# NitiLens Enterprise Setup Script
# Automated installation and configuration

set -e

echo "🚀 NitiLens Enterprise SaaS Platform Setup"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Windows (Git Bash/WSL)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "${YELLOW}⚠️  Detected Windows environment${NC}"
    echo "Please ensure you have:"
    echo "  - Docker Desktop installed and running"
    echo "  - Git Bash or WSL for running this script"
    echo ""
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists docker; then
    echo "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command_exists docker-compose; then
    echo "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

if ! command_exists python3 && ! command_exists python; then
    echo "${RED}❌ Python is not installed${NC}"
    echo "Please install Python 3.11+: https://www.python.org/downloads/"
    exit 1
fi

if ! command_exists node; then
    echo "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js 18+: https://nodejs.org/"
    exit 1
fi

echo "${GREEN}✅ All prerequisites met${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating environment configuration..."
    cp backend/.env.example backend/.env
    
    # Generate random JWT secret
    JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || echo "change-this-secret-key-in-production")
    
    # Update .env with generated secret
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-super-secret-jwt-key-change-in-production/$JWT_SECRET/" backend/.env
    else
        sed -i "s/your-super-secret-jwt-key-change-in-production/$JWT_SECRET/" backend/.env
    fi
    
    echo "${GREEN}✅ Environment file created${NC}"
else
    echo "${YELLOW}ℹ️  Using existing .env file${NC}"
fi

echo ""

# Ask user for installation method
echo "Choose installation method:"
echo "1) Docker (Recommended - Full stack with one command)"
echo "2) Local Development (Manual setup for development)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "🐳 Starting Docker installation..."
        echo ""
        
        # Build and start containers
        echo "📦 Building containers..."
        docker-compose build
        
        echo ""
        echo "🚀 Starting services..."
        docker-compose up -d
        
        echo ""
        echo "⏳ Waiting for services to be ready..."
        sleep 10
        
        # Check if services are running
        if docker-compose ps | grep -q "Up"; then
            echo "${GREEN}✅ All services started successfully!${NC}"
            echo ""
            echo "📊 Service URLs:"
            echo "   Frontend:  http://localhost:3000"
            echo "   Backend:   http://localhost:8000"
            echo "   API Docs:  http://localhost:8000/docs"
            echo "   Health:    http://localhost:8000/health"
            echo ""
            echo "📝 Default credentials:"
            echo "   Admin: admin@nitilens.com / admin123"
            echo "   Demo:  demo@nitilens.com / demo123"
            echo ""
            echo "🛠️  Useful commands:"
            echo "   View logs:     docker-compose logs -f"
            echo "   Stop services: docker-compose down"
            echo "   Restart:       docker-compose restart"
        else
            echo "${RED}❌ Some services failed to start${NC}"
            echo "Check logs with: docker-compose logs"
            exit 1
        fi
        ;;
        
    2)
        echo ""
        echo "🔧 Setting up local development environment..."
        echo ""
        
        # Install Python dependencies
        echo "📦 Installing Python dependencies..."
        cd backend
        python3 -m pip install -r requirements.txt || python -m pip install -r requirements.txt
        cd ..
        echo "${GREEN}✅ Python dependencies installed${NC}"
        
        # Install Node dependencies
        echo ""
        echo "📦 Installing Node.js dependencies..."
        npm install
        echo "${GREEN}✅ Node.js dependencies installed${NC}"
        
        # Setup PostgreSQL
        echo ""
        echo "🐘 PostgreSQL Setup"
        echo "Please ensure PostgreSQL is running and create database:"
        echo "  CREATE DATABASE nitilens_db;"
        echo "  CREATE USER nitilens WITH PASSWORD 'nitilens_password';"
        echo "  GRANT ALL PRIVILEGES ON DATABASE nitilens_db TO nitilens;"
        echo ""
        read -p "Press Enter when PostgreSQL is ready..."
        
        # Setup Redis
        echo ""
        echo "📮 Redis Setup"
        echo "Please ensure Redis is running on localhost:6379"
        echo ""
        read -p "Press Enter when Redis is ready..."
        
        # Initialize database
        echo ""
        echo "🗄️  Initializing database..."
        cd backend
        python3 init_db.py || python init_db.py
        cd ..
        echo "${GREEN}✅ Database initialized${NC}"
        
        echo ""
        echo "${GREEN}✅ Local setup complete!${NC}"
        echo ""
        echo "🚀 To start the application:"
        echo ""
        echo "Terminal 1 (Backend):"
        echo "  cd backend"
        echo "  uvicorn app.main:app --reload --port 8000"
        echo ""
        echo "Terminal 2 (Frontend):"
        echo "  npm run dev"
        echo ""
        echo "Terminal 3 (Worker - Optional):"
        echo "  cd backend"
        echo "  celery -A app.worker worker --loglevel=info"
        echo ""
        echo "📊 Access URLs:"
        echo "   Frontend:  http://localhost:5173"
        echo "   Backend:   http://localhost:8000"
        echo "   API Docs:  http://localhost:8000/docs"
        echo ""
        echo "📝 Default credentials:"
        echo "   Admin: admin@nitilens.com / admin123"
        echo "   Demo:  demo@nitilens.com / demo123"
        ;;
        
    *)
        echo "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "🎉 Setup complete! Welcome to NitiLens Enterprise!"
echo ""
