#!/bin/bash
# Run script for the complete cricket portal system

set -e

echo "🏏 Starting Cricket Portal System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please update with your configuration."
fi

# Start infrastructure services
echo "📦 Starting infrastructure services (PostgreSQL, Redis, MinIO)..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are up
echo "🔍 Checking service health..."
docker-compose ps

# Initialize database
echo "🗄️  Initializing database..."
cd backend
python -c "
from database import engine, Base
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import shared models, fallback to local
try:
    from shared.models import User, Session, Delivery, Pose, WeaknessSummary
    print('✅ Using shared models')
except ImportError:
    from models import User, Session, Delivery, Pose, WeaknessSummary
    print('✅ Using local models')

Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"

# Seed database
echo "🌱 Seeding database..."
python seed.py || echo "⚠️  Seed script failed (may already be seeded)"

cd ..

# Start API server in background
echo "🚀 Starting API server..."
cd backend
python main.py &
API_PID=$!
cd ..

# Wait a bit for API to start
sleep 3

# Start worker in background
echo "⚙️  Starting analysis worker..."
cd backend
celery -A celery_app worker --loglevel=info &
WORKER_PID=$!
cd ..

echo ""
echo "✅ System started!"
echo ""
echo "📊 Services:"
echo "  - API Server: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "🛑 To stop:"
echo "  - Press Ctrl+C"
echo "  - Or run: pkill -f 'python main.py' && pkill -f 'celery'"
echo ""

# Wait for user interrupt
wait

