# Cricket Batting Analysis Backend

Production-grade backend for cricket batting video analysis with ML-powered weakness detection.

## Architecture

### Components

1. **API Service** (`backend/main.py`)
   - FastAPI REST API
   - Authentication & authorization
   - Session & delivery management
   - Weakness reporting

2. **Analysis Worker** (`worker/`)
   - Celery-based async worker
   - Video processing pipeline
   - Pose estimation
   - Delivery classification
   - Weakness aggregation

3. **Storage** (`backend/storage.py`)
   - S3-compatible storage (MinIO for dev, AWS S3 for prod)
   - Video upload/download
   - Presigned URLs

4. **Database** (PostgreSQL)
   - User management
   - Session tracking
   - Delivery/Shot records
   - Pose data
   - Weakness summaries

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- MinIO (for local S3) or AWS S3

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Infrastructure (Docker)

```bash
# Start PostgreSQL, Redis, and MinIO
docker-compose up -d

# Wait for services to be healthy
docker-compose ps
```

### 3. Configure Environment

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://cricket_user:cricket_pass@localhost:5432/cricket_portal

# Redis
REDIS_URL=redis://localhost:6379/0

# Storage (MinIO for dev)
USE_S3=false
S3_ENDPOINT_URL=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
S3_BUCKET_NAME=cricket-videos

# JWT
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Debug
DEBUG=true
```

### 4. Initialize Database

```bash
# Create tables
python -c "from backend.database import engine, Base; from backend.models import *; Base.metadata.create_all(bind=engine)"

# Seed test data
python backend/seed.py
```

### 5. Start Services

**Terminal 1 - API Server:**
```bash
cd backend
python main.py
# Or: uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
celery -A backend.celery_app worker --loglevel=info
# Or from worker directory:
celery -A worker.worker worker --loglevel=info
```

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login (returns JWT tokens)
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

### Sessions

- `POST /sessions` - Create session and upload video
- `GET /sessions` - List user's sessions
- `GET /sessions/{id}` - Get session details
- `GET /sessions/{id}/deliveries` - Get deliveries for session
- `GET /sessions/{id}/weaknesses` - Get weakness analysis
- `GET /sessions/{id}/video` - Get presigned video URL

## Analysis Pipeline

The analysis pipeline consists of:

1. **Frame Extraction** (`analysis/extract_frames.py`)
   - Extract frames from video
   - Detect motion segments (deliveries)

2. **Pose Estimation** (`analysis/pose_estimation.py`)
   - MediaPipe pose detection
   - Extract keypoints and metrics

3. **Delivery Classification** (`analysis/classify_delivery.py`)
   - Classify delivery type (short, full, yorker, etc.)
   - Classify shot type (drive, pull, cut, etc.)
   - Determine outcome (middled, edge, mishit, etc.)

4. **Weakness Aggregation** (`analysis/aggregate_weaknesses.py`)
   - Analyze delivery patterns
   - Identify weaknesses and strengths
   - Generate recommendations

## Data Model

### User
- Authentication info
- Profile (handedness, skill level, role)

### Session
- Video metadata
- Processing status
- Context (location, surface, bowler type)

### Delivery
- Timestamp in video
- Delivery type, line, shot type
- Outcome and rating
- Speed estimates

### Pose
- Frame-level pose data
- Keypoints and derived metrics

### WeaknessSummary
- Natural language summary
- Tagged weaknesses
- Metric breakdown
- Recommendations

## Development

### Running Tests

```bash
# Unit tests (when added)
pytest tests/

# Integration tests
pytest tests/integration/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

### Monitoring

- **Celery Flower** (optional): `celery -A backend.celery_app flower`
- **API Docs**: `http://localhost:8000/docs`
- **MinIO Console**: `http://localhost:9001`

## Production Deployment

1. Use PostgreSQL (not SQLite)
2. Use AWS S3 (not MinIO)
3. Set strong `SECRET_KEY`
4. Configure proper CORS origins
5. Use environment variables for all secrets
6. Set up proper logging
7. Use process manager (systemd, supervisor, etc.)
8. Set up monitoring and alerts

## Troubleshooting

### Worker not processing jobs
- Check Redis connection
- Check worker logs: `celery -A backend.celery_app worker --loglevel=debug`
- Verify task is registered: `celery -A backend.celery_app inspect registered`

### Video upload fails
- Check MinIO/S3 connection
- Verify bucket exists
- Check file size limits

### Analysis fails
- Check video format (MP4 recommended)
- Verify MediaPipe installation
- Check worker logs for errors

## Next Steps

- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Implement rate limiting
- [ ] Add request validation middleware
- [ ] Implement proper logging with structured logs
- [ ] Add metrics and monitoring
- [ ] Implement real ball tracking
- [ ] Add advanced ML models
- [ ] Implement video thumbnail generation
- [ ] Add batch processing support

