# Implementation Guide - Production System

## Overview

This guide explains what has been built and how to complete the production system.

## ✅ What's Been Built

### 1. Shared Foundation (`shared/`)

#### Models (`shared/models/`)
- **Base Model**: Common fields (id, created_at, updated_at)
- **User Model**: Role-based (player/coach/admin), extended profile
- **Session Model**: Video sessions with processing status
- **Delivery Model**: Individual ball/shot analysis
- **Pose Model**: Frame-level pose data
- **WeaknessSummary Model**: Aggregated insights

#### Types (`shared/types/`)
- Comprehensive enums for all cricket-specific types
- User roles, delivery types, shot types, outcomes, etc.
- Weakness categories

#### Insights Engine (`shared/insights/`)
- **weakness_mapping.py**: Complete drill and focus point mappings
- **detector.py**: Threshold-based weakness detection
- **aggregator.py**: Comprehensive metric calculation and insights generation

### 2. Key Features

#### Role-Based Access Control
```python
user.is_player()  # Check if player
user.is_coach()   # Check if coach
user.is_admin()   # Check if admin
user.can_view_session(session_user_id)  # Permission check
```

#### Weakness Detection
- 10 predefined weakness categories
- Threshold-based detection
- Evidence collection
- Severity calculation
- Personalized recommendations

#### Insights Generation
- Line/length matrix
- Timing consistency
- Control percentage
- Head/footwork stability
- Strength identification
- Natural language summaries

## 🔧 How to Complete the System

### Step 1: Update Existing Backend to Use Shared Models

**Files to update**:
- `backend/models.py` → Remove, use `shared.models`
- `backend/routers/auth.py` → Import from `shared.models`
- `backend/routers/sessions.py` → Import from `shared.models`
- `backend/database.py` → Import Base from `shared.models.base`

**Example**:
```python
# OLD
from models import User

# NEW
from shared.models import User
from shared.types.enums import UserRole
```

### Step 2: Integrate Insights Engine into Worker

**File**: `worker/src/analysis/pipeline.py`

```python
from shared.insights.aggregator import InsightsAggregator

class AnalysisPipeline:
    def __init__(self):
        self.insights_aggregator = InsightsAggregator()
    
    def analyze(self, video_url, session_id, db):
        # ... existing analysis ...
        
        # Generate insights
        deliveries_data = [self._delivery_to_dict(d) for d in deliveries]
        pose_metrics = [self._pose_to_dict(p) for p in poses]
        
        insights = self.insights_aggregator.aggregate(
            deliveries_data,
            pose_metrics
        )
        
        # Create WeaknessSummary
        weakness_summary = WeaknessSummary(
            user_id=session.user_id,
            session_id=session_id,
            summary_text=insights["summary_text"],
            strengths_text=insights["strengths_text"],
            key_weakness_tags=insights["key_weakness_tags"],
            metric_breakdown=insights["metric_breakdown"],
            recommendations=insights["recommendations"]
        )
```

### Step 3: Add Role-Based Authorization

**File**: `api/src/common/auth.py`

```python
from shared.models import User
from shared.types.enums import UserRole
from fastapi import HTTPException, status

def require_role(*allowed_roles: UserRole):
    """Decorator to require specific roles"""
    def decorator(func):
        async def wrapper(current_user: User = Depends(get_current_user), *args, **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(current_user=current_user, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@router.get("/admin/sessions")
@require_role(UserRole.ADMIN, UserRole.COACH)
async def list_all_sessions(current_user: User):
    ...
```

### Step 4: Set Up Alembic Migrations

**Create**: `db/alembic.ini` and `db/migrations/`

```bash
cd db
alembic init migrations
```

**Update**: `db/migrations/env.py` to use shared models

```python
from shared.models.base import Base
from shared.models import User, Session, Delivery, Pose, WeaknessSummary

target_metadata = Base.metadata
```

**Create initial migration**:
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Step 5: Create Frontend Integration Layer

**File**: `frontend/lib/api/client.ts`

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

**File**: `frontend/lib/api/types.ts`

```typescript
export enum UserRole {
  PLAYER = 'player',
  COACH = 'coach',
  ADMIN = 'admin',
}

export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  handedness: string;
  age?: number;
  experience_level: string;
  play_style?: string;
}

export interface Session {
  id: number;
  user_id: number;
  title: string;
  processing_status: string;
  // ... other fields
}
```

### Step 6: Enhanced Docker Compose

**File**: `infra/docker-compose.yml`

```yaml
services:
  api:
    build:
      context: ..
      dockerfile: api/Dockerfile
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
  
  worker:
    build:
      context: ..
      dockerfile: worker/Dockerfile
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
```

## 📊 Testing Strategy

### Unit Tests

**File**: `tests/unit/test_insights.py`

```python
def test_weakness_detection():
    detector = WeaknessDetector()
    metric_breakdown = {
        "combinations": {
            "short_pull": {
                "attempts": 10,
                "middled": 3,  # 30% - below threshold
                "edges": 4,
                "mishits": 3
            }
        }
    }
    weaknesses = detector.detect_weaknesses(metric_breakdown, [])
    assert len(weaknesses) > 0
    assert weaknesses[0]["tag"] == "short_ball_pull"
```

### Integration Tests

**File**: `tests/integration/test_upload_flow.py`

```python
async def test_upload_to_insights_flow():
    # 1. Upload video
    session = await create_session(video_file)
    
    # 2. Wait for analysis
    await wait_for_analysis(session.id)
    
    # 3. Get weaknesses
    weaknesses = await get_weaknesses(session.id)
    
    # 4. Verify structure
    assert "weaknesses" in weaknesses
    assert "recommendations" in weaknesses
```

## 🎯 Next Immediate Steps

1. **Update backend imports** to use shared models (30 min)
2. **Integrate insights engine** into worker (1 hour)
3. **Add role-based auth** to API (1 hour)
4. **Set up Alembic** migrations (1 hour)
5. **Create frontend API client** (1 hour)
6. **Enhance docker-compose** (30 min)

## 📚 Key Files Reference

- **Models**: `shared/models/`
- **Insights**: `shared/insights/`
- **Enums**: `shared/types/enums.py`
- **Weakness Mapping**: `shared/insights/weakness_mapping.py`
- **Detector**: `shared/insights/detector.py`
- **Aggregator**: `shared/insights/aggregator.py`

## 🔍 Architecture Benefits

1. **Modular**: Easy to swap ML models
2. **Testable**: Insights engine is pure Python
3. **Extensible**: Add new weakness categories easily
4. **Maintainable**: Clear separation of concerns
5. **Scalable**: Role-based access ready for teams/academies

The foundation is solid. The remaining work is integration and deployment infrastructure.

