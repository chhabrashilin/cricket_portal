# 🚀 READY TO RUN - Complete Instructions

## ✅ Quick Start (Copy & Paste)

### 1. Start Docker Services
```bash
docker-compose up -d
```

### 2. Setup Backend (Windows PowerShell)
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python main.py
```

### 3. Start Worker (New PowerShell Window)
```powershell
cd backend
venv\Scripts\activate
celery -A celery_app worker --loglevel=info
```

### 4. Start Frontend (New PowerShell Window - Optional)
```powershell
npm install
npm run dev
```

## 📋 Detailed Steps

### Step 1: Infrastructure Setup

**Open PowerShell/Terminal and run:**
```bash
docker-compose up -d
```

**Wait 10 seconds, then verify:**
```bash
docker ps
```

You should see 3 containers running:
- `cricket_postgres`
- `cricket_redis`  
- `cricket_minio`

### Step 2: Backend Setup

**In PowerShell, run these commands one by one:**

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py
```

**You should see:**
```
✅ Database tables created successfully
✅ Database seeded successfully
```

### Step 3: Start API Server

**In the SAME PowerShell window (keep it open):**
```powershell
python main.py
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

✅ **API is running!** Open: http://localhost:8000/docs

### Step 4: Start Worker

**Open a NEW PowerShell window:**

```powershell
cd backend
venv\Scripts\activate
celery -A celery_app worker --loglevel=info
```

**You should see:**
```
celery@YourComputerName ready.
```

✅ **Worker is ready!**

### Step 5: Start Frontend (Optional)

**Open a NEW PowerShell window:**

```powershell
npm install
npm run dev
```

✅ **Frontend is running!** Open: http://localhost:3000

## ✅ Verify Everything

1. **API**: http://localhost:8000
   - Should show: `{"message": "Cricket Batting Analysis API", ...}`

2. **API Docs**: http://localhost:8000/docs
   - Should show Swagger UI

3. **Health Check**: http://localhost:8000/health
   - Should return: `{"status": "healthy", "database": "connected"}`

4. **Frontend**: http://localhost:3000
   - Should show cricket analyzer UI

## 🧪 Test It Works

**Go to**: http://localhost:8000/docs

1. Find `POST /auth/register`
2. Click "Try it out"
3. Paste this JSON:
```json
{
  "email": "test@example.com",
  "name": "Test User",
  "password": "password123"
}
```
4. Click "Execute"
5. You should get a 201 response with user data!

## 🐛 Troubleshooting

### "docker-compose not found"
- Install Docker Desktop
- Make sure Docker is running

### "python not found"
- Install Python 3.9+ from python.org
- Make sure Python is in your PATH

### "Module not found" when running main.py
- Make sure you activated venv: `venv\Scripts\activate`
- Make sure you're in the `backend` directory
- Run: `pip install -r requirements.txt` again

### "Database connection error"
- Wait 15 seconds after `docker-compose up -d`
- Check: `docker ps` - should show postgres running
- Check logs: `docker logs cricket_postgres`

### "Port 8000 already in use"
- Find what's using it: `netstat -ano | findstr :8000` (Windows)
- Kill the process or change PORT in `.env`

### "Celery worker not starting"
- Make sure Redis is running: `docker ps | findstr redis`
- Check: `docker logs cricket_redis`

## 📊 What You Should See

**Terminal 1 (API):**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Terminal 2 (Worker):**
```
celery@hostname v5.3.4 (singularity)
...
[tasks]
  . analyze_session
```

**Terminal 3 (Frontend - if started):**
```
  ▲ Next.js 14.0.4
  - Local:        http://localhost:3000
```

## 🎯 You're Done!

Your system is now running:
- ✅ API Server: http://localhost:8000
- ✅ API Documentation: http://localhost:8000/docs
- ✅ Worker: Processing jobs in background
- ✅ Frontend: http://localhost:3000 (if started)
- ✅ Database: Running in Docker
- ✅ Storage: MinIO running in Docker

## 📝 Next: Use the System

1. **Register/Login** via API docs or frontend
2. **Upload a video** via frontend
3. **Watch the worker** process it
4. **View analysis results** with weaknesses and recommendations

---

**Need more help?** Check:
- `HOW_TO_RUN.md` - Detailed instructions
- `QUICK_RUN.md` - Complete setup guide
- `backend/BACKEND_README.md` - API documentation

