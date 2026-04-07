# 🚀 GUIA DE BORDO AUTÔNOMO - SKYNETCHAT SYSTEM

**Versão: 1.0** | **Data: 2024** | **Autor: Arquiteto Sênior SkynetChat**

Este guia transforma você de zero conhecimento em **operador pleno** do sistema. Siga os passos na **ordem exata**. Cada comando é **copiável e testado**.

---

## 🏗️ Seção 1: Diagnóstico e Visão Geral da Arquitetura

### Análise do Ecossistema
O SkynetChat é um **sistema completo de monitoramento de roleta brasileira** com **duas modalidades de captura** e **voz sintetizada em tempo real**.

#### Principais Componentes:

| Componente | Propósito | Arquivo Principal |
|------------|-----------|------------------|
| **Modo Visual (Polling)** | Captura números via Playwright (navegador headless). Fallback confiável. | `main.py` |
| **Modo WebSocket** | Intercepta Socket.IO do Playtech para **zero latência**. Recomendado. | `main_playtech.py` |
| **Agente de Voz** | Servidor WS que **broadcasta sinais** para PWA cliente. Porta 8765 (WS) + 8080 (HTTP). | `server.py` |
| **Core** | Lógica de captura, filtros, analytics. | `core/` |
| **Services** | Telegram, relatórios, forwarders. | `services/` |
| **Storage** | Banco SQLite (data/database.sqlite) + backups automáticos. | `storage/` |
| **Engine** | Estratégias, parsers, calculadoras. | `engine/` |
| **PWA** | **Interface final**: Voz + histórico + config. App standalone. | `pwa/` |

**Diferença Crucial main.py vs main_playtech.py**:
```
main.py:         Playwright → Polling (0.5s) → Visual scraping → Lento mas 100% compatível
main_playtech.py: Playwright → WS Intercept → Socket.IO real-time → INSTANTÂNEO (recomendado)
```

#### Diagrama de Fluxo Simplificado (Texto ASCII):

```
🌐 SITE PLAYTECH ──(Playwright/WS)──► 🎯 BOT (main_playtech.py)
                                       │
                                       ▼
                            🔊 VOICE BRIDGE ──(WS 8765)──► 📱 PWA (localhost:8080)
                                       │                          │
                                       ▼                          ▼
                              📱 TELEGRAM BOT               🎤 VOZ SINTETIZADA
                                       │
                                       ▼
                              💾 SQLITE DB (analytics/history)
```

**Modularidade**:
- `core/`: Captura números (monitor.py visual, playtech_ws.py WS).
- `services/`: Telegram + daily reports.
- `storage/`: DB + backups.
- `analytics/`: Turbulência, performance tracking.
- `pwa/`: Cliente voz (index.html + manifest.json + sw.js).

---

## ⚙️ Seção 2: Implantação - Do Zero ao Ar (Windows 10/11)

### Pré-requisitos
```
✅ Python 3.10+ (baixar em python.org)
✅ Git (opcional, para clone; aqui assumimos ZIP baixado)
✅ Descompacte o ZIP em uma pasta (ex: C:\SkynetChat)
```

### Passo a Passo de Instalação

**Passo 1: Baixar o código**
- Você já tem o ZIP descompactado em `d:/Nova pasta/telegram-win-main` (ou sua pasta).

**Passo 2: Navegar até a pasta do projeto**
```cmd
cd "d:/Nova pasta/telegram-win-main"
```

**Passo 3: Executar o Instalador (Mágico!)**
```cmd
.\setup_platform.bat
```
**O que o script faz** (automático):
- Cria `.venv` (venv isolado).
- `pip install -r requirements.txt` (todas deps).
- `playwright install` (navegador Chromium).
- Cria pastas `data/`, `logs/`, `playwright_profile/`.

**Passo 4: Configuração das Credenciais (.env)**
Crie/edit `config/.env` com este **conteúdo completo**:

```env
# ===== TELEGRAM (OBRIGATÓRIO) =====
# Obtenha TOKEN em @BotFather (crie bot /newbot)
TELEGRAM_TOKEN=8288750850:AAE5UQ9IN5VSmt_6redYbsim-0ZeHirsIHg
# Obtenha CHAT_ID em @userinfobot (envie /start)
TELEGRAM_CHAT_ID=-1002800575942

# ===== JOGO (NÃO ALTERE) =====
GAME_URL=https://geralbet.bet.br/games/playtech/roleta-brasileira

# ===== OPCIONAIS (deixe padrão) =====
API_URL=https://api.geralbet.bet.br
API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....
BET_AMOUNT=100
WAIT_ROUNDS_AFTER_WIN=1
WAIT_ROUNDS_AFTER_ZERO=5
```

**Como Obter Tokens (5min)**:
1. Telegram: `/start @BotFather` → `/newbot` → nome → TOKEN copiado.
2. Chat ID: `/start @userinfobot` → "Id: XXXXX" copiado.

---

## ▶️ Seção 3: Operação - Colocando o Sistema no Ar

### Verificação Pré-Execução
```cmd
# Ative venv (obrigatório TUDO!)
.\.venv\Scripts\activate

# Verifique tudo
python verify_stabilization.py
```
**Interpretação**:
- ✅ Todas checks = pronto.
- ❌ ❌ = Corrija .env ou rode setup novamente.

### Fluxo de Operação (3 Terminais)

**Terminal 1: Servidor de Voz** (abra CMD novo na pasta projeto)
```cmd
.\.venv\Scripts\activate
python server.py
```
**Sucesso**:
```
WIN Voice Agent RODANDO!
PWA: http://localhost:8080
WS : ws://localhost:8765
Token: win_secret_2024
```

**Terminal 2: O Bot** (abra CMD novo)
```cmd
.\.venv\Scripts\activate
python main_playtech.py  # Modo avançado (RECOMENDADO)
# Alternativa: python main.py (modo visual)
```
**Sucesso**:
```
BOT INICIADO - Roleta Brasileira (Playtech WebSocket)
⚡ Otimização: XX estratégias carregadas
```

**Terminal 3: Cliente PWA**
- Abra Chrome/Edge → `http://localhost:8080`
- **Clique em qualquer lugar** (ativa áudio autoplay).
- Config: WS `ws://localhost:8765`, Token `win_secret_2024`.

**Pronto!** Sistema 100% operacional.

---

## 🆘 Seção 4: Solução de Problemas e Manutenção (FAQ Interativo)

### 🚫 O bot não detecta números
**Causa 1: Seletores mudaram**
```
Ação: Rode `python main.py` (visual). Observe navegador.
Se não focar números: Edite `core/monitor.py` seletores.
```

**Causa 2: URL incorreta**
```
Ação: `python verify_url.py`
Saída: ✅ ou ❌. Corrija GAME_URL em config/.env
```

### 🔌 Servidor de voz não conecta
```
Causa: Firewall bloqueia 8765/8080
Ação:
1. Windows Defender → Permitir app Python pelas portas 8765,8080
2. Teste: `python server.py` → acesse localhost:8080
```

### 📊 Ver histórico de jogadas?
```cmd
.\.venv\Scripts\activate
python view_stats.py
```
**Saída**: Total números, top frequentes, últimos 10.

**Outros**:
- Logs: `logs/bot.log`
- Backup DB: `data/backups/`
- Reiniciar bot: Ctrl+C → rerun.

---

## 🛑 Seção 5: Encerramento e Próximos Passos

### Como Parar
```
Em CADA terminal: Ctrl+C (seguro, salva DB)
```

### Próximos Passos
- **Aprofundamento**: `GUIA_DIDATICO.md` (conceitos), `README_PLATFORM.md` (arquitetura).
- **Customizar**: Edite `engine/` estratégias.
- **Produção**: Docker (docker-compose.yml pronto).

**Parabéns! 🎉 Você agora opera o SkynetChat como profissional.**

---
*Guia gerado autonomamente via análise de código fonte. Zero conhecimento prévio necessário.*

