# Quick Start Guide

Get your Cricket Batting Analyzer up and running in minutes!

## Prerequisites

- **Node.js 18+** and npm
- **Python 3.9+**
- **Git** (optional)

## Step 1: Clone/Download the Project

If you have the project files, you're ready to go!

## Step 2: Install Frontend Dependencies

```bash
# In the project root directory
npm install
```

## Step 3: Install Backend Dependencies

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

# Install Python packages
pip install -r requirements.txt
```

## Step 4: Start the Backend Server

```bash
# Make sure you're in the backend directory with venv activated
python main.py
```

The backend will start on `http://localhost:8000`

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 5: Start the Frontend (New Terminal)

Open a new terminal window and:

```bash
# Navigate to project root (if not already there)
cd cricket_portal

# Start Next.js dev server
npm run dev
```

The frontend will start on `http://localhost:3000`

## Step 6: Use the Application

1. Open your browser and go to `http://localhost:3000`
2. Upload a cricket batting video (MP4, AVI, MOV, etc.)
3. Select the video from the list
4. Click "Analyze Video" to run the AI analysis
5. View detailed results including:
   - Overall score
   - Identified weaknesses
   - Strengths
   - Personalized recommendations
   - Visual charts and metrics

## Troubleshooting

### Backend won't start
- Make sure Python 3.9+ is installed: `python --version`
- Ensure virtual environment is activated
- Check that all dependencies are installed: `pip list`

### Frontend won't start
- Make sure Node.js 18+ is installed: `node --version`
- Ensure dependencies are installed: `npm install`
- Check for port conflicts (3000 or 8000 already in use)

### Video upload fails
- Check that backend is running on port 8000
- Ensure `uploads/videos` directory exists (created automatically)
- Verify video file format is supported

### Analysis fails
- Ensure MediaPipe is installed: `pip show mediapipe`
- Check that video contains visible person/batter
- Verify video quality is sufficient for pose detection

### CORS errors
- Make sure backend CORS is configured for `http://localhost:3000`
- Check that both servers are running

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API at `http://localhost:8000/docs` (FastAPI auto-generated docs)
- Check out the code structure to understand how it works
- Upload different videos to see various analysis results

## Tips for Best Results

1. **Video Quality**: Use clear, well-lit videos
2. **Camera Angle**: Side-on view works best for analysis
3. **Full Body**: Ensure the entire batter is visible in the frame
4. **Stable Camera**: Avoid shaky footage for better pose detection
5. **Multiple Shots**: Upload several videos to track improvement over time

Enjoy analyzing your cricket batting technique! 🏏

