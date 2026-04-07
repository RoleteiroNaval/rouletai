# Guia de Deploy e Migração (Ubuntu Linux)

Este documento descreve como migrar e rodar este bot em um ambiente Linux.

## 📋 Pré-requisitos
- Python 3.10 ou superior
- Pip (instalador de pacotes do Python)

## 🚀 Instalação Rápida

O projeto inclui um script de automação (`bootstrap_linux.sh`). Siga os passos:

1. **Dê permissão de execução ao script:**
   ```bash
   chmod +x bootstrap_linux.sh
   ```

2. **Execute o instalador:**
   ```bash
   ./bootstrap_linux.sh
   ```

## ⚙️ Configuração
Edite o arquivo `config/.env` com suas credenciais:
```env
TELEGRAM_TOKEN=...
TELEGRAM_CHAT_ID=...
GAME_URL=...
HEADLESS=False  # Mantenha False se quiser ver o navegador
```

## 🛠️ Execução

Sempre ative o ambiente virtual antes de rodar:
```bash
source .venv/bin/activate
```

### Modo WebSocket (Recomendado)
```bash
python main_playtech.py
```

### Modo Visual (Headless detectado no settings)
```bash
python main.py
```

## 🧭 Operação Manual (Modo Visual)
Se `HEADLESS=False` no `.env`, o bot abrirá uma janela do Navegador.
1. O bot pausará e mostrará instruções no terminal.
2. Faça login manualmente no site.
3. Entre na roleta recomendada.
4. **Pressione ENTER** no terminal quando a roleta estiver visível.

## 💾 Backup e Persistência
- **Banco de Dados**: Fica em `data/database.sqlite`.
- **Perfil do Navegador**: Fica em `playwright_profile/` (mantém seu login salvo).
- **Backups**: Gerados automaticamente em `data/backups/`.

---
*Bot desenvolvido para resiliência e portabilidade.*
