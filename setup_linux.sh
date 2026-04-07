#!/bin/bash

echo "🚀 Iniciando Configuração do Ambiente Linux..."

# Update and install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git curl

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps

# Create necessary directories
mkdir -p data logs playwright_profile

echo "✅ Configuração concluída! Use 'source .venv/bin/activate && python main.py' para rodar."
echo "💡 Ou use Docker: 'docker-compose up -d --build'"
