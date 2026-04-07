#!/bin/bash

# Skynet Platform Setup Script (Windows)
# Run this to set up the complete platform

echo "🚀 Setting up Skynet Signal Intelligence Platform..."

# Check if we're in the right directory
if not exist "main.py" (
    echo "❌ Error: Run this script from the project root directory"
    exit /b 1
)

# Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo "📦 Creating virtual environment..."
    python -m venv .venv
)

# Activate virtual environment
echo "🔧 Activating virtual environment..."
call .venv\Scripts\activate.bat

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
if exist "frontend" (
    echo "⚛️ Setting up frontend..."
    cd frontend

    if not exist "node_modules" (
        npm install
    )

    cd ..
)

# Create necessary directories
echo "📁 Creating directories..."
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "playwright_profile" mkdir playwright_profile

echo "✅ Setup complete!"
echo.
echo "🎯 To run the platform:"
echo "1. Backend API: python api/main.py"
echo "2. Frontend: cd frontend && npm start"
echo "3. Bot mode: python main.py"
echo.
echo "📊 Access dashboard at: http://localhost:3000"
echo "🔗 API docs at: http://localhost:8000/docs"