# 🏏 Cricket Batting Analyzer

A revolutionary AI-powered cricket batting analysis platform that uses machine learning and computer vision to identify weaknesses in batting technique and provide actionable recommendations.

## Features

- **Video Upload & Management**: Upload cricket batting videos in multiple formats
- **AI-Powered Analysis**: Advanced ML algorithms analyze:
  - Footwork and movement
  - Balance and stability
  - Head position
  - Swing path and technique
  - Timing and rhythm
  - Backlift position
  - Follow-through quality
- **Weakness Detection**: Identifies specific weaknesses with severity levels
- **Actionable Recommendations**: Provides personalized coaching recommendations
- **Visual Analytics**: Interactive charts and graphs showing performance metrics
- **Real-time Processing**: Fast video analysis using MediaPipe pose estimation

## Technology Stack

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **React Dropzone** - File uploads

### Backend
- **FastAPI** - Python web framework
- **MediaPipe** - Pose estimation and tracking
- **OpenCV** - Video processing
- **SQLAlchemy** - Database ORM
- **PostgreSQL/SQLite** - Database

### ML/AI
- **MediaPipe Pose** - Human pose detection
- **Custom ML Algorithms** - Cricket-specific analysis
- **Computer Vision** - Video feature extraction

## Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL (optional, SQLite used by default)

### Frontend Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

Backend will be available at `http://localhost:8000`

### Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite:///./cricket_portal.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/cricket_portal
```

## Usage

1. **Upload a Video**: Click or drag & drop a cricket batting video
2. **Select Video**: Choose a video from your list
3. **Analyze**: Click "Analyze Video" to run the AI analysis
4. **Review Results**: View detailed analysis including:
   - Overall score (0-100)
   - Identified weaknesses with severity levels
   - Strengths in your technique
   - Personalized recommendations
   - Visual charts and metrics

## Analysis Features

### Footwork Analysis
- Front foot movement
- Foot spacing and positioning
- Back foot stability

### Balance Analysis
- Center of mass tracking
- Stability metrics
- Weight distribution

### Head Position
- Head stability tracking
- Position relative to ball
- Movement patterns

### Swing Path
- Bat trajectory analysis
- Swing arc evaluation
- Follow-through quality

### Timing Analysis
- Swing consistency
- Rhythm and tempo
- Contact point optimization

## API Endpoints

- `POST /api/videos/upload` - Upload a video
- `GET /api/videos` - Get all videos
- `GET /api/videos/{id}` - Get specific video
- `POST /api/videos/{id}/analyze` - Analyze a video
- `GET /api/videos/{id}/analysis` - Get analysis results

## Project Structure

```
cricket_portal/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py           # Database configuration
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── ml_analyzer.py        # ML analysis engine
│   └── video_processor.py    # Video processing
├── src/
│   ├── app/                  # Next.js app directory
│   ├── components/           # React components
│   └── types/                # TypeScript types
├── uploads/                  # Uploaded videos (gitignored)
└── README.md
```

## Future Enhancements

- [ ] Ball tracking integration
- [ ] Multi-angle video analysis
- [ ] Comparison with professional players
- [ ] Progress tracking over time
- [ ] Mobile app
- [ ] Real-time analysis during recording
- [ ] Advanced bat tracking
- [ ] Shot type classification
- [ ] Performance benchmarking

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Acknowledgments

- MediaPipe for pose estimation
- FastAPI for the excellent Python framework
- Next.js team for the amazing React framework

---

**Revolutionize your cricket game with AI-powered insights!** 🏏🚀

