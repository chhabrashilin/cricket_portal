#!/bin/bash
# Development startup script

echo "🏏 Starting Cricket Portal (Development Mode)"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
fi

# Start infrastructure
echo "🚀 Starting infrastructure services..."
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services..."
sleep 10

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    exit 1
fi

# Setup Python environment
cd backend
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Initialize database
echo "🗄️  Setting up database..."
python -c "
from database import engine, Base
try:
    from shared.models import User, Session, Delivery, Pose, WeaknessSummary
    print('✅ Using shared models')
except ImportError:
    from models import User, Session, Delivery, Pose, WeaknessSummary
    print('✅ Using local models')
Base.metadata.create_all(bind=engine)
print('✅ Database ready')
"

# Seed if needed
echo "🌱 Seeding database..."
python seed.py 2>/dev/null || echo "⚠️  Database may already be seeded"

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Start API: cd backend && source venv/bin/activate && python main.py"
echo "  2. Start Worker: cd backend && source venv/bin/activate && celery -A celery_app worker --loglevel=info"
echo "  3. Start Frontend: npm install && npm run dev"
echo ""
echo "🌐 Services will be available at:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Frontend: http://localhost:3000"
echo "  - MinIO: http://localhost:9001"
echo ""

