# Architecture Overview

## System Architecture

The Cricket Batting Analyzer is built as a full-stack application with a clear separation between frontend and backend.

```
┌─────────────────┐
│   Next.js UI    │  ← React frontend with TypeScript
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP/REST API
         ▼
┌─────────────────┐
│   FastAPI       │  ← Python backend with ML processing
│  (Port 8000)    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│ SQLite │ │ MediaPipe    │
│   DB   │ │ Pose Est.    │
└────────┘ └──────────────┘
```

## Key Components

### Frontend (Next.js)

**Location**: `src/`

- **Pages**: `src/app/page.tsx` - Main application page
- **Components**:
  - `VideoUpload.tsx` - Drag & drop video upload
  - `VideoList.tsx` - List of uploaded videos
  - `AnalysisResults.tsx` - Display analysis with charts
- **Types**: `src/types/index.ts` - TypeScript type definitions

**Technologies**:
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Recharts (data visualization)
- React Dropzone (file uploads)

### Backend (FastAPI)

**Location**: `backend/`

**Core Files**:
- `main.py` - FastAPI application and API endpoints
- `database.py` - Database configuration (SQLAlchemy)
- `models.py` - Database models (Video, Analysis)
- `schemas.py` - Pydantic schemas for request/response validation
- `ml_analyzer.py` - **Core ML analysis engine**
- `video_processor.py` - Video processing and feature extraction

**Technologies**:
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- MediaPipe (pose estimation)
- OpenCV (video processing)
- NumPy, Pandas (data processing)

## ML Analysis Pipeline

### 1. Video Upload & Storage
```
User uploads video → Saved to uploads/videos/ → Database record created
```

### 2. Video Processing
```
Video file → OpenCV reads frames → MediaPipe pose detection → 
Extract landmarks → Normalize coordinates → Store pose data
```

### 3. Feature Extraction
The `CricketBattingAnalyzer` extracts:
- **Head positions** - Stability and alignment
- **Shoulder angles** - Posture and alignment
- **Hip positions** - Balance and weight distribution
- **Ankle positions** - Footwork analysis
- **Wrist positions** - Swing path tracking
- **Center of mass** - Balance metrics
- **Keyframes** - Start, backlift, contact, follow-through

### 4. Analysis Components

#### Footwork Analysis
- Front foot movement distance
- Foot spacing (shoulder-width check)
- Back foot stability

#### Balance Analysis
- Center of mass variance
- Weight distribution
- Stability metrics

#### Head Position Analysis
- Head movement variance
- Position relative to body
- Stability tracking

#### Swing Path Analysis
- Bat trajectory (via wrist tracking)
- Swing arc evaluation
- Follow-through completeness

#### Timing Analysis
- Swing speed consistency
- Rhythm evaluation
- Movement smoothness

#### Backlift Analysis
- Initial bat position
- Backlift angle
- Preparation quality

#### Follow-Through Analysis
- Completion of swing
- Commitment to shot
- Bat speed maintenance

### 5. Weakness Detection

**Scoring System**:
- Each aspect scored 0-100
- Weighted overall score calculation
- Threshold-based weakness identification:
  - Score < 50: High severity
  - Score 50-60: Medium severity
  - Score 60-70: Low severity

**Weakness Categories**:
- Footwork issues
- Balance problems
- Head position errors
- Swing path deviations
- Timing inconsistencies
- Backlift problems
- Follow-through issues

### 6. Recommendation Generation

AI-generated recommendations based on:
- Identified weaknesses
- Severity levels
- Category-specific coaching tips
- Progressive improvement suggestions

## Data Flow

```
1. User uploads video
   ↓
2. Video saved, DB record created
   ↓
3. User clicks "Analyze"
   ↓
4. Backend processes video:
   - Extract frames
   - Run MediaPipe pose detection
   - Extract features
   ↓
5. ML Analyzer processes features:
   - Calculate metrics
   - Run analysis algorithms
   - Identify weaknesses/strengths
   - Generate recommendations
   ↓
6. Analysis saved to database
   ↓
7. Results returned to frontend
   ↓
8. Frontend displays:
   - Overall score
   - Weaknesses with severity
   - Strengths
   - Recommendations
   - Visual charts
```

## Database Schema

### Videos Table
- `id` - Primary key
- `filename` - Original filename
- `file_path` - Storage path
- `user_id` - Optional user association
- `analysis_status` - pending/processing/completed/failed
- `created_at` - Timestamp

### Analyses Table
- `id` - Primary key
- `video_id` - Foreign key to videos
- `overall_score` - 0-100 score
- `weaknesses` - JSON array of weakness objects
- `strengths` - JSON array of strength objects
- `recommendations` - JSON array of strings
- `detailed_metrics` - JSON object with full analysis data
- `created_at` - Timestamp

## API Endpoints

### Video Management
- `POST /api/videos/upload` - Upload video
- `GET /api/videos` - List all videos
- `GET /api/videos/{id}` - Get specific video
- `GET /api/videos/{id}/video` - Serve video file

### Analysis
- `POST /api/videos/{id}/analyze` - Run analysis
- `GET /api/videos/{id}/analysis` - Get analysis results

## Performance Considerations

### Video Processing
- Frame sampling: Processes ~10 frames/second (configurable)
- Efficient pose detection: MediaPipe optimized for real-time
- Async processing: Non-blocking video uploads

### Scalability
- Database: Can switch from SQLite to PostgreSQL
- Storage: Can integrate S3/cloud storage
- Processing: Can add Celery for async task queue
- Caching: Can add Redis for frequently accessed data

## Security Considerations

- File type validation
- File size limits (can be added)
- CORS configuration
- Input validation via Pydantic
- SQL injection protection (SQLAlchemy ORM)

## Future Enhancements

### Advanced ML Features
- Ball tracking integration
- Bat detection and tracking
- Shot type classification
- Comparison with professional players
- Multi-angle analysis

### Infrastructure
- User authentication
- Cloud storage integration
- Real-time analysis during recording
- Mobile app
- Progress tracking over time

### Analysis Improvements
- Machine learning model training
- Custom model for cricket-specific movements
- Deep learning for advanced pattern recognition
- Ensemble methods for improved accuracy

## Development Workflow

1. **Backend Development**
   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```

2. **Frontend Development**
   ```bash
   npm run dev
   ```

3. **Testing**
   - Backend: FastAPI auto-docs at `/docs`
   - Frontend: Browser dev tools
   - Integration: Test full flow

4. **Deployment**
   - Backend: Deploy to cloud (AWS, GCP, Azure)
   - Frontend: Deploy to Vercel/Netlify
   - Database: Use managed PostgreSQL
   - Storage: Use cloud storage (S3, etc.)

