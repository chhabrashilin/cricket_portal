# 🚀 Run the System Now

## Quick Start (Choose Your Platform)

### Windows

1. **Open PowerShell or Command Prompt**

2. **Start Infrastructure:**
   ```powershell
   docker-compose up -d
   ```

3. **Setup Backend:**
   ```powershell
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Initialize Database:**
   ```powershell
   python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"
   python seed.py
   ```

5. **Start API (Terminal 1):**
   ```powershell
   python main.py
   ```

6. **Start Worker (Terminal 2):**
   ```powershell
   celery -A celery_app worker --loglevel=info
   ```

7. **Start Frontend (Terminal 3):**
   ```powershell
   cd ..
   npm install
   npm run dev
   ```

### macOS/Linux

1. **Run the setup script:**
   ```bash
   chmod +x start-dev.sh
   ./start-dev.sh
   ```

2. **Or manually:**

   ```bash
   # Start infrastructure
   docker-compose up -d
   
   # Setup backend
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Initialize database
   python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"
   python seed.py
   
   # Start API (Terminal 1)
   python main.py
   
   # Start Worker (Terminal 2)
   celery -A celery_app worker --loglevel=info
   
   # Start Frontend (Terminal 3)
   cd ..
   npm install
   npm run dev
   ```

## ✅ Verify It's Working

1. **API Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status": "healthy", "database": "connected"}`

2. **API Docs:**
   Open: http://localhost:8000/docs

3. **Frontend:**
   Open: http://localhost:3000

4. **MinIO Console:**
   Open: http://localhost:9001
   Login: `minioadmin` / `minioadmin`

## 🧪 Quick Test

**Register a user:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "player@test.com", "name": "Test Player", "password": "test123"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=player@test.com&password=test123"
```

## 🐛 Common Issues

**"Module not found" errors:**
- Make sure you're in the `backend` directory
- Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)

**Database connection error:**
- Check Docker is running: `docker ps`
- Check PostgreSQL is up: `docker-compose ps`
- Wait 10 seconds after starting docker-compose

**Port already in use:**
- Change PORT in `.env` file
- Or stop the service using the port

**Worker not starting:**
- Make sure Redis is running: `docker-compose ps`
- Check Redis: `docker exec -it cricket_redis redis-cli ping`

## 📝 Default Settings

- **Database**: `postgresql://cricket_user:cricket_pass@localhost:5432/cricket_portal`
- **Redis**: `redis://localhost:6379/0`
- **MinIO**: `http://localhost:9000` (minioadmin/minioadmin)
- **API Port**: `8000`
- **Frontend Port**: `3000`

## 🛑 Stop Everything

```bash
# Stop API and Worker (Ctrl+C in terminals)

# Stop infrastructure
docker-compose down
```

## 📚 Need Help?

- Check `QUICK_RUN.md` for detailed instructions
- Check `backend/BACKEND_README.md` for API docs
- Check `PRODUCTION_ARCHITECTURE.md` for system overview

