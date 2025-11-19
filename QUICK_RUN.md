# Quick Run Guide

## 🚀 Get Everything Running in 5 Minutes

### Prerequisites
- Docker and Docker Compose installed
- Python 3.9+ installed
- Node.js 18+ installed (for frontend)

### Step 1: Setup Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env if needed (defaults should work for local dev)
```

### Step 2: Start Infrastructure

```bash
# Start PostgreSQL, Redis, and MinIO
docker-compose up -d

# Wait for services to be ready (about 10 seconds)
docker-compose ps
```

### Step 3: Install Dependencies

```bash
# Backend dependencies
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cd ..
```

### Step 4: Initialize Database

```bash
cd backend

# Create tables
python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"

# Seed test data
python seed.py

cd ..
```

### Step 5: Start Services

**Option A: Use Run Scripts (Recommended)**

```bash
# On macOS/Linux:
chmod +x run.sh
./run.sh

# On Windows:
run.bat
```

**Option B: Manual Start**

**Terminal 1 - API Server:**
```bash
cd backend
python main.py
```

**Terminal 2 - Worker:**
```bash
cd backend
celery -A celery_app worker --loglevel=info
```

**Terminal 3 - Frontend (optional):**
```bash
npm install
npm run dev
```

### Step 6: Verify Everything Works

1. **Check API**: http://localhost:8000
   - Should return: `{"message": "Cricket Batting Analysis API", ...}`

2. **Check API Docs**: http://localhost:8000/docs
   - Should show Swagger UI

3. **Check Health**: http://localhost:8000/health
   - Should return: `{"status": "healthy", "database": "connected"}`

4. **Check MinIO**: http://localhost:9001
   - Login: `minioadmin` / `minioadmin`

5. **Check Frontend**: http://localhost:3000
   - Should show the cricket analyzer UI

### 🧪 Test the System

1. **Register a user:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "password123"
  }'
```

2. **Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

3. **Create a session (upload video):**
   - Use the frontend at http://localhost:3000
   - Or use the API with the access token from login

### 🐛 Troubleshooting

**Database connection error:**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres
```

**Redis connection error:**
```bash
# Check if Redis is running
docker-compose ps

# Test connection
docker exec -it cricket_redis redis-cli ping
```

**Worker not processing:**
```bash
# Check worker logs
# Look for "celery@hostname ready" message

# Check registered tasks
celery -A backend.celery_app inspect registered
```

**Port already in use:**
```bash
# Change port in .env
PORT=8001

# Or stop the service using the port
```

### 📝 Default Credentials

- **Database**: `cricket_user` / `cricket_pass`
- **MinIO**: `minioadmin` / `minioadmin`
- **Test User** (after seeding): `test@example.com` / `password123`

### 🛑 Stop Everything

```bash
# Stop API and Worker (Ctrl+C in terminals)

# Stop infrastructure
docker-compose down

# Or stop and remove volumes
docker-compose down -v
```

### 📚 Next Steps

- Read `PRODUCTION_ARCHITECTURE.md` for system overview
- Read `IMPLEMENTATION_GUIDE.md` for integration details
- Check `backend/BACKEND_README.md` for API documentation

