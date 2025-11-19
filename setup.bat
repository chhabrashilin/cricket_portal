@echo off
REM Setup script for Cricket Batting Analyzer on Windows

echo 🏏 Setting up Cricket Batting Analyzer...

REM Frontend setup
echo 📦 Installing frontend dependencies...
call npm install

REM Backend setup
echo 🐍 Setting up Python backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python packages...
pip install -r requirements.txt

REM Create upload directories
echo Creating upload directories...
if not exist "..\uploads\videos" mkdir "..\uploads\videos"
if not exist "..\uploads\processed" mkdir "..\uploads\processed"

cd ..

echo ✅ Setup complete!
echo.
echo To start the application:
echo 1. Backend: cd backend ^&^& venv\Scripts\activate ^&^& python main.py
echo 2. Frontend: npm run dev
echo.
echo See QUICKSTART.md for detailed instructions.

pause

