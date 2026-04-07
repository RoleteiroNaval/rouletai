# 🎰 Bot Observador - Roleta Brasileira (Playtech)

Bot profissional para monitoramento automatizado da Roleta Brasileira no site Geralbet, com logging avançado, auto-recuperação e persistência de dados.

---

## 📋 **O QUE ESTE BOT FAZ**

✅ Observa a timeline de números da roleta em tempo real  
✅ Envia notificações via Telegram quando novo número é detectado  
✅ Gera estratégias automáticas baseadas em padrões  
✅ Registra tudo em logs rotativos (não perde histórico)  
✅ Salva números em banco de dados SQLite  
✅ Auto-recuperação em caso de erros/crashes  
✅ Métricas e health checks automáticos  

❌ **NÃO APOSTA** - apenas observa o DOM do jogo

---

## 🚀 **INSTALAÇÃO**

### **1. Pré-requisitos**
- Python 3.10 ou superior
- Windows 10/11, macOS ou Linux

### **2. Instalar dependências**

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### **3. Configurar variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:

```env
TELEGRAM_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

**Como obter:**
- `TELEGRAM_TOKEN`: Crie um bot no [@BotFather](https://t.me/BotFather)
- `TELEGRAM_CHAT_ID`: Use [@userinfobot](https://t.me/userinfobot) para descobrir seu ID

---

## ▶️ **COMO USAR**

```powershell
python main.py
```

**Fluxo:**
1. O navegador Chromium abre automaticamente
2. Faça login manualmente no site
3. Navegue até a Roleta Brasileira
4. Pressione ENTER quando a roleta estiver rodando
5. O bot começa a monitorar automaticamente

---

## 📊 **ESTRUTURA DO PROJETO**

```
telegram-bot-playwright2/
├── main.py                 # Ponto de entrada principal
├── scraper/
│   └── monitor.py          # Lógica de scraping (Playwright)
├── telegram_bot/
│   ├── bot.py              # Cliente Telegram
│   └── forwarder.py        # Forwarder (não usado no modo observação)
├── strategy/
│   └── engine.py           # Geração de estratégias
├── utils/
│   ├── logger.py           # Sistema de logging
│   ├── metrics.py          # Métricas e health checks
│   └── database.py         # Persistência SQLite
├── logs/                   # Logs rotativos (5MB cada, até 3 backups)
├── data/                   # Banco de dados SQLite
└── playwright_profile/     # Perfil persistente do navegador
```

---

## 🛡️ **RECURSOS DE PRODUÇÃO**

### **1. Sistema de Logging**
- **Rotação automática**: Arquivos de 5MB
- **Níveis**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Saída dupla**: Terminal + arquivo
- **Localização**: `logs/bot.log`

### **2. Auto-Recuperação**
- Detecta página travada/fechada
- Retry automático com backoff exponencial
- Reconexão automática em caso de erro
- Health check a cada 60 segundos

### **3. Métricas**
- Uptime do bot
- Total de números detectados
- Erros consecutivos
- Tempo desde último número
- Falhas no envio ao Telegram

**Relatório automático a cada 5 minutos:**

```
╔══════════════════════════════════════╗
║     MÉTRICAS DO BOT - RELATÓRIO      ║
╠══════════════════════════════════════╣
║ Uptime:              02h:15m:33s     ║
║ Números detectados:               42 ║
║ Erros totais:                      3 ║
║ Recuperações:                      1 ║
║ Falhas Telegram:                   0 ║
║ Último número há:                 12s ║
╚══════════════════════════════════════╝
```

### **4. Banco de Dados SQLite**
- Tabela `numbers`: Histórico completo de números
- Tabela `sessions`: Registro de execuções
- Tabela `errors`: Log de erros para análise

**Consultas úteis:**

```sql
-- Ver últimos 10 números
SELECT number, detected_at FROM numbers ORDER BY detected_at DESC LIMIT 10;

-- Números mais frequentes
SELECT number, COUNT(*) as vezes 
FROM numbers 
GROUP BY number 
ORDER BY vezes DESC 
LIMIT 5;

-- Estatísticas da última sessão
SELECT * FROM sessions ORDER BY started_at DESC LIMIT 1;
```

---

## 🐛 **DEBUGGING**

### **Problema: Terminal travado sem output**

**Causa provável:**
- Aguardando `input()` (pressione ENTER)
- Seletores mudaram (site atualizou estrutura)
- Página crashou

**Solução:**
1. Verifique os logs: `cat logs/bot.log`
2. Procure por warnings de "Timeline não encontrada"
3. Se necessário, atualize os seletores em `monitor.py`:

```python
TIMELINE_SELECTOR = ".roulette-history_line"      # Container (Estável)
NUMBER_SELECTOR = "[data-automation-locator='field.lastHistoryItem'] .history-item-value__text"  # Texto do número
```

### **Problema: Erro "ModuleNotFoundError: No module named 'playwright'"**

**Solução:**
```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### **Problema: Bot não detecta números**

**Diagnóstico:**
1. Abra o DevTools no navegador (F12)
2. Inspecione a timeline de números
3. Verifique se os seletores ainda existem
4. Veja os logs: `logs/bot.log`

---

## 📈 **CONCEITOS TÉCNICOS EXPLICADOS**

### **1. Polling vs WebSocket**

**Polling (usado neste bot):**
```python
while True:
    numero = monitor.watch()  # Pergunta: "tem número novo?"
    time.sleep(0.5)
```

**Vantagens:**
- Simples de implementar
- Funciona em qualquer site
- Não depende de API pública

**Desvantagens:**
- Consome mais CPU
- Latência de até 500ms

**WebSocket (ideal, mas não disponível aqui):**
- Notificação instantânea quando algo muda
- Requer que o site exponha WebSocket público

### **2. Playwright vs Selenium**

**Playwright (usado):**
- Mais rápido
- Suporte a contextos persistentes (mantém login)
- API moderna (async/await)

**Selenium:**
- Mais antigo
- Maior comunidade

### **3. Persistent Context**

```python
self.context = self.playwright.chromium.launch_persistent_context(
    user_data_dir="playwright_profile"
)
```

**Benefício:** Mantém cookies, login, histórico entre execuções.

---

## 🔧 **CUSTOMIZAÇÃO**

### **Mudar intervalo de polling**

```python
# main.py, linha 88
time.sleep(0.5)  # 500ms → mude para 0.2 (mais rápido) ou 1.0 (mais lento)
```

### **Desabilitar estratégias**

```python
# main.py, linha 66-71
# Comente estas linhas:
# estrategia = gerar_mensagem_por_numero(int(numero))
# if estrategia:
#     ...
```

### **Executar em modo headless (sem navegador visível)**

```python
# scraper/monitor.py, linha 38
headless=True  # Mude de False para True
```

---

## 📝 **LOGS IMPORTANTES**

| Nível | Quando | Ação |
|-------|--------|------|
| INFO | Número detectado | Normal |
| WARNING | Timeline não encontrada | Verifique se está na página certa |
| ERROR | Erro ao enviar Telegram | Verifique token/internet |
| CRITICAL | Crash do sistema | Veja traceback completo no log |

---

## 🚫 **LIMITAÇÕES**

- **Não aposta automaticamente** (e nem deve, por segurança)
- **Depende da estrutura do DOM** (se o site mudar, seletores quebram)
- **Não funciona sem intervenção humana** (login manual necessário)
- **Não captura WebSocket interno** (apenas leitura DOM)

---

## 📧 **SUPORTE**

Se encontrar bugs ou tiver dúvidas, verifique:
1. `logs/bot.log` - logs detalhados
2. `data/roulette.db` - banco de dados histórico
3. Terminal - output em tempo real

---

## 📄 **LICENÇA**

Este bot é apenas para fins educacionais. **Uso responsável.**
