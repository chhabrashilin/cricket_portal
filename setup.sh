#!/bin/bash
# Setup script for Cricket Batting Analyzer

echo "🏏 Setting up Cricket Batting Analyzer..."

# Frontend setup
echo "📦 Installing frontend dependencies..."
npm install

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Create upload directories
echo "Creating upload directories..."
mkdir -p ../uploads/videos
mkdir -p ../uploads/processed

cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: cd backend && source venv/bin/activate && python main.py"
echo "2. Frontend: npm run dev"
echo ""
echo "See QUICKSTART.md for detailed instructions."

