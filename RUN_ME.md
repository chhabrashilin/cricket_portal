# 🚀 RUN ME - Simple Instructions

## Windows Users

### 1. Start Docker Services
```powershell
docker-compose up -d
```

### 2. Setup Python Backend
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
```

### 3. Start API (Keep this terminal open)
```powershell
python main.py
```

### 4. Open NEW Terminal - Start Worker
```powershell
cd backend
venv\Scripts\activate
celery -A celery_app worker --loglevel=info
```

### 5. Open NEW Terminal - Start Frontend (Optional)
```powershell
npm install
npm run dev
```

## Mac/Linux Users

### 1. Start Docker Services
```bash
docker-compose up -d
```

### 2. Setup Python Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
```

### 3. Start API (Terminal 1)
```bash
python main.py
```

### 4. Start Worker (Terminal 2)
```bash
cd backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

### 5. Start Frontend (Terminal 3 - Optional)
```bash
npm install
npm run dev
```

## ✅ Check It's Working

1. Open: http://localhost:8000/docs
2. You should see the API documentation
3. Try the `/health` endpoint - should return healthy

## 🧪 Quick Test

**Register a user:**
- Go to http://localhost:8000/docs
- Find `POST /auth/register`
- Click "Try it out"
- Use this JSON:
```json
{
  "email": "test@example.com",
  "name": "Test User",
  "password": "password123"
}
```
- Click "Execute"

**Login:**
- Find `POST /auth/login`
- Use:
  - username: `test@example.com`
  - password: `password123`
- You'll get an access token!

## 🐛 Troubleshooting

**"Module not found"**
- Make sure you activated venv: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
- Make sure you're in the `backend` directory

**"Database connection error"**
- Wait 10 seconds after starting docker-compose
- Check: `docker ps` - should show postgres, redis, minio running

**"Port 8000 already in use"**
- Change PORT in `.env` file to 8001
- Or stop whatever is using port 8000

**"Celery not found"**
- Make sure you installed requirements: `pip install -r requirements.txt`
- Make sure venv is activated

## 📝 That's It!

Your system should now be running:
- ✅ API: http://localhost:8000
- ✅ API Docs: http://localhost:8000/docs  
- ✅ Frontend: http://localhost:3000 (if started)
- ✅ MinIO: http://localhost:9001 (minioadmin/minioadmin)

