#!/bin/bash

# Skynet Platform Setup Script
# Run this to set up the complete platform

echo "🚀 Setting up Skynet Signal Intelligence Platform..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Run this script from the project root directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # Linux/Mac

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install -U pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
python -m pip install -r requirements.txt

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
python -m playwright install

# Setup frontend
if [ -d "frontend" ]; then
    echo "⚛️ Setting up frontend..."
    cd frontend

    if [ ! -d "node_modules" ]; then
        npm install
    fi

    cd ..
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs playwright_profile

echo "✅ Setup complete!"
echo ""
echo "🎯 To run the platform:"
echo "1. Backend API: python api/main.py"
echo "2. Frontend: cd frontend && npm start"
echo "3. Bot mode: python main.py"
echo ""
echo "📊 Access dashboard at: http://localhost:3000"
echo "🔗 API docs at: http://localhost:8000/docs"