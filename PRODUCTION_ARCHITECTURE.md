# Production Architecture - Cricket AI Coach Platform

## 🏗️ Monorepo Structure

```
cricket_portal/
├── api/                    # FastAPI REST API service
│   ├── src/
│   │   ├── auth/          # Authentication & authorization
│   │   ├── sessions/      # Session management
│   │   ├── deliveries/    # Delivery/Shot endpoints
│   │   ├── weakness/      # Weakness insights endpoints
│   │   ├── admin/         # Admin endpoints
│   │   └── common/       # Shared utilities, middleware
│   ├── Dockerfile
│   └── requirements.txt
│
├── worker/                 # Celery analysis worker
│   ├── src/
│   │   ├── queue/         # Queue management
│   │   ├── analysis/      # Analysis orchestration
│   │   ├── pose/          # Pose estimation
│   │   ├── delivery_segmentation/  # Delivery detection
│   │   └── weakness_engine/        # Insights generation
│   ├── Dockerfile
│   └── requirements.txt
│
├── shared/                 # Shared code between services
│   ├── types/             # Type definitions
│   ├── schemas/           # Pydantic schemas
│   └── utils/             # Common utilities
│
├── db/                     # Database migrations
│   └── migrations/        # Alembic migrations
│
├── infra/                  # Infrastructure as code
│   ├── docker-compose.yml
│   ├── env.example
│   └── scripts/           # Deployment scripts
│
└── frontend/              # Next.js frontend (existing)
    └── ...
```

## 🔐 Authentication & Authorization

### Roles
- **player**: Regular user, can upload videos and view own analysis
- **coach**: Can view players' sessions, provide feedback
- **admin**: Full system access, manage users, view all data

### User Profile Fields
- Basic: email, name, password_hash
- Cricket-specific: handedness, age, experience_level, play_style
- Role: player/coach/admin
- Metadata: created_at, updated_at, is_active

## 📊 Data Model

### Core Entities
1. **User**: Authentication, profile, role
2. **Session**: Video upload, metadata, processing status
3. **Delivery**: Individual ball/shot analysis
4. **PoseMetrics**: Frame-level pose data (optional)
5. **WeaknessSummary**: Aggregated insights

### Indexes
- User: email (unique), role
- Session: user_id, processing_status, created_at
- Delivery: session_id, timestamp_in_video
- WeaknessSummary: user_id, session_id

## 🔄 Analysis Pipeline

### Modules (All Stubbed but Realistic)

1. **Frame Extraction**
   - Extract frames from video
   - Motion detection
   - Keyframe identification

2. **Pose Estimation** (Stub)
   - Generate realistic skeleton data
   - Calculate cricket-specific metrics
   - Interface ready for MediaPipe/OpenPose

3. **Delivery Segmentation**
   - Detect delivery boundaries
   - Classify delivery type (short/good_length/full/yorker/bouncer)
   - Identify line (off/middle/leg/wide)

4. **Shot Classification**
   - Classify shot type (drive/pull/cut/sweep/defense/etc.)
   - Determine outcome (middled/edge/mishit/miss/wicket_risk)
   - Calculate timing metrics

5. **Metrics Calculation**
   - Line/length matrix
   - Timing consistency
   - Control % per shot type
   - Head stability score
   - Footwork stability

6. **Weakness Engine**
   - Pattern detection
   - Threshold-based weakness identification
   - Strength recognition
   - Drill recommendations

## 🎯 Weakness Categories & Mappings

### Categories
- `short_ball_pull`: Struggles with pull shots to short balls
- `full_ball_drive`: Issues with driving full deliveries
- `good_length_defense`: Defense technique problems
- `wide_outside_off`: Struggles with wide deliveries
- `spinning_ball_footwork`: Footwork vs spin
- `backlift_angle_inconsistent`: Inconsistent backlift
- `late_contact_point`: Late timing

### Weakness → Drill Mapping
Each weakness maps to specific drills and focus points.

## 🚀 API Endpoints

### Auth
- `POST /auth/register` - Register with role
- `POST /auth/login` - Get JWT tokens
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Current user info

### Sessions
- `POST /sessions` - Create session, upload video
- `GET /sessions` - List user's sessions
- `GET /sessions/:id` - Session details
- `GET /sessions/:id/weaknesses` - Weakness analysis
- `GET /sessions/:id/deliveries` - Delivery list

### Deliveries
- `GET /deliveries/:id` - Delivery details

### Admin
- `GET /admin/jobs` - Job status
- `GET /admin/sessions/recent` - Recent sessions

## 🧪 Testing Strategy

1. **Unit Tests**
   - Insights engine logic
   - Weakness detection algorithms
   - API endpoint handlers

2. **Integration Tests**
   - Full upload → analysis → weaknesses flow
   - Authentication flows
   - Database operations

3. **Pipeline Tests**
   - Analysis pipeline with stub data
   - Worker task execution
   - Error handling

## 📦 Deployment

### Docker Compose Services
- postgres: Database
- redis: Queue backend
- minio: S3-compatible storage
- api: FastAPI service
- worker: Celery worker

### Environment Configuration
- Centralized .env management
- Validation on startup
- Secrets management

## 🔍 Quality Standards

- Type hints everywhere
- Docstrings for all modules
- Structured logging
- Error handling with proper codes
- Request validation
- Rate limiting ready
- Monitoring hooks

