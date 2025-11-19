# 🏏 START HERE - Run the Cricket Portal

## ⚡ Quick Start (3 Steps)

### Step 1: Start Infrastructure
```bash
docker-compose up -d
```

Wait 10 seconds for services to start.

### Step 2: Setup Backend

**Windows:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"
python seed.py
```

**Mac/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"
python seed.py
```

### Step 3: Start Services

**Terminal 1 - API:**
```bash
cd backend
# Activate venv if not already
python main.py
```

**Terminal 2 - Worker:**
```bash
cd backend
# Activate venv if not already
celery -A celery_app worker --loglevel=info
```

**Terminal 3 - Frontend (optional):**
```bash
npm install
npm run dev
```

## ✅ Verify It Works

1. **API**: http://localhost:8000
2. **API Docs**: http://localhost:8000/docs
3. **Frontend**: http://localhost:3000
4. **Health Check**: http://localhost:8000/health

## 🧪 Test It

**Register:**
```bash
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d "{\"email\":\"test@test.com\",\"name\":\"Test\",\"password\":\"test123\"}"
```

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=test@test.com&password=test123"
```

## 🐛 Problems?

**Database error?**
- Check Docker: `docker ps`
- Wait 10 seconds after `docker-compose up -d`

**Import errors?**
- Make sure you're in the `backend` directory
- Activate venv: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)

**Port in use?**
- Change PORT in `.env` file
- Or stop the service using port 8000

## 📚 More Help

- `RUN_NOW.md` - Detailed run instructions
- `QUICK_RUN.md` - Complete setup guide
- `backend/BACKEND_README.md` - API documentation

