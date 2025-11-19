@echo off
REM Run script for Windows

echo 🏏 Starting Cricket Portal System...

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from .env.example...
    copy .env.example .env
    echo ✅ Created .env file. Please update with your configuration.
)

REM Start infrastructure services
echo 📦 Starting infrastructure services...
docker-compose up -d

REM Wait for services
echo ⏳ Waiting for services to be ready...
timeout /t 5 /nobreak >nul

REM Initialize database
echo 🗄️  Initializing database...
cd backend
python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine); print('✅ Database tables created')"

REM Seed database
echo 🌱 Seeding database...
python seed.py

cd ..

REM Start API server
echo 🚀 Starting API server...
start "Cricket API" cmd /k "cd backend && python main.py"

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start worker
echo ⚙️  Starting analysis worker...
start "Cricket Worker" cmd /k "cd backend && celery -A celery_app worker --loglevel=info"

echo.
echo ✅ System started!
echo.
echo 📊 Services:
echo   - API Server: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - MinIO Console: http://localhost:9001
echo.
echo Press any key to exit...
pause >nul

