# 🏏 How to Run the Cricket Portal

## Prerequisites
- ✅ Docker Desktop installed and running
- ✅ Python 3.9+ installed
- ✅ Node.js 18+ installed (for frontend)

## Step-by-Step Instructions

### Step 1: Start Infrastructure (Docker)

Open a terminal and run:
```bash
docker-compose up -d
```

Wait 10-15 seconds for services to start. Verify with:
```bash
docker ps
```
You should see: `cricket_postgres`, `cricket_redis`, `cricket_minio`

### Step 2: Setup Backend

**Windows:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
```

**Mac/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
```

This will:
- Create Python virtual environment
- Install all dependencies
- Create database tables
- Seed test data

### Step 3: Start API Server

**Keep the terminal from Step 2 open**, and run:
```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ API is running at: http://localhost:8000

### Step 4: Start Worker (New Terminal)

Open a **NEW terminal**:

**Windows:**
```powershell
cd backend
venv\Scripts\activate
celery -A celery_app worker --loglevel=info
```

**Mac/Linux:**
```bash
cd backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

You should see:
```
celery@hostname ready
```

✅ Worker is ready to process videos

### Step 5: Start Frontend (Optional - New Terminal)

Open a **NEW terminal**:
```bash
npm install
npm run dev
```

✅ Frontend is running at: http://localhost:3000

## ✅ Verify Everything Works

1. **API Health**: http://localhost:8000/health
   - Should return: `{"status": "healthy", "database": "connected"}`

2. **API Docs**: http://localhost:8000/docs
   - Should show Swagger UI with all endpoints

3. **Frontend**: http://localhost:3000
   - Should show the cricket analyzer interface

4. **MinIO Console**: http://localhost:9001
   - Login: `minioadmin` / `minioadmin`

## 🧪 Test the API

### Option 1: Use API Docs (Easiest)
1. Go to http://localhost:8000/docs
2. Find `POST /auth/register`
3. Click "Try it out"
4. Use this JSON:
```json
{
  "email": "player@test.com",
  "name": "Test Player",
  "password": "test123"
}
```
5. Click "Execute"
6. You should get a user response!

### Option 2: Use curl
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"player@test.com","name":"Test Player","password":"test123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=player@test.com&password=test123"
```

## 🐛 Common Issues & Fixes

### "docker-compose: command not found"
- Install Docker Desktop
- Make sure Docker is running

### "Module not found" errors
- ✅ Make sure you're in the `backend` directory
- ✅ Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
- ✅ Run: `pip install -r requirements.txt`

### "Database connection error"
- ✅ Wait 10-15 seconds after `docker-compose up -d`
- ✅ Check Docker is running: `docker ps`
- ✅ Check PostgreSQL: `docker logs cricket_postgres`

### "Port 8000 already in use"
- Change PORT in `.env` file to 8001
- Or stop the service using port 8000

### "Celery not found"
- ✅ Make sure venv is activated
- ✅ Run: `pip install -r requirements.txt`

### "Redis connection error"
- ✅ Check Redis is running: `docker ps | grep redis`
- ✅ Test: `docker exec -it cricket_redis redis-cli ping` (should return PONG)

## 📊 What's Running

After following all steps, you should have:

| Service | URL | Status |
|---------|-----|--------|
| API Server | http://localhost:8000 | ✅ Running |
| API Docs | http://localhost:8000/docs | ✅ Available |
| Worker | Background process | ✅ Processing jobs |
| Frontend | http://localhost:3000 | ✅ Running (if started) |
| PostgreSQL | localhost:5432 | ✅ Running in Docker |
| Redis | localhost:6379 | ✅ Running in Docker |
| MinIO | localhost:9000 | ✅ Running in Docker |
| MinIO Console | http://localhost:9001 | ✅ Available |

## 🛑 Stop Everything

1. **Stop API**: Press `Ctrl+C` in API terminal
2. **Stop Worker**: Press `Ctrl+C` in Worker terminal
3. **Stop Frontend**: Press `Ctrl+C` in Frontend terminal (if running)
4. **Stop Infrastructure**: 
   ```bash
   docker-compose down
   ```

## 📝 Default Credentials

- **Database**: `cricket_user` / `cricket_pass`
- **MinIO**: `minioadmin` / `minioadmin`
- **Test User** (after seeding): `test@example.com` / `password123`

## 🎯 Next Steps

1. ✅ System is running!
2. Upload a video via the frontend
3. Watch the worker process it
4. View the analysis results

## 📚 More Help

- `RUN_ME.md` - Even simpler instructions
- `QUICK_RUN.md` - Detailed setup guide
- `backend/BACKEND_README.md` - API documentation

---

**You're all set! 🚀**

