#!/bin/bash

# --- Script de Bootstrap para Linux (Ubuntu/Debian) ---
# Este script prepara o ambiente virtual, instala dependências e o Playwright.

set -e

echo "🚀 Iniciando preparação do ambiente..."

# 1. Atualizar sistema
echo "📦 Atualizando pacotes do sistema..."
sudo apt update && sudo apt install -y python3-venv python3-pip libevent-dev

# 2. Criar ambiente virtual
if [ ! -d ".venv" ]; then
    echo "🐍 Criando ambiente virtual (.venv)..."
    python3 -m venv .venv
else
    echo "✅ Ambiente virtual já existe."
fi

# 3. Ativar e Instalar dependências
echo "📥 Instalando dependências do Python..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Instalar navegadores do Playwright
echo "🎭 Instalando navegadores Playwright..."
playwright install chromium
playwright install-deps chromium

# 5. Preparar configuração
if [ ! -f "config/.env" ]; then
    echo "⚙️ Criando arquivo .env a partir do modelo..."
    cp config/.env.example config/.env
    echo "⚠️ AVISO: Configure suas chaves no arquivo config/.env antes de rodar!"
fi

# 6. Criar diretórios necessários
mkdir -p data logs playwright_profile

echo ""
echo "✅ Ambiente preparado com sucesso!"
echo "------------------------------------------------"
echo "Para iniciar o bot:"
echo "1. Ative o venv: source .venv/bin/activate"
echo "2. Configure o .env: nano config/.env"
echo "3. Execute: python main_playtech.py"
echo "------------------------------------------------"
