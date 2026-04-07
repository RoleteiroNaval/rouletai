# 🎓 GUIA DIDÁTICO: CONCEITOS DE DESENVOLVIMENTO

Este documento explica os conceitos técnicos usados neste projeto de forma didática.

---

## 📚 **ÍNDICE**

1. [Web Scraping com Playwright](#web-scraping)
2. [Polling vs WebSocket](#polling-vs-websocket)
3. [Logging Profissional](#logging)
4. [Tratamento de Erros e Retry](#tratamento-de-erros)
5. [Persistência de Dados (SQLite)](#persistência)
6. [Métricas e Health Checks](#métricas)
7. [Arquitetura do Projeto](#arquitetura)

---

## <a name="web-scraping"></a> 🌐 **1. WEB SCRAPING COM PLAYWRIGHT**

### **O que é Web Scraping?**
"Raspar" dados de sites. Imagine que você quer saber o preço de um produto, mas o site não tem API. Você pode usar scraping para ler o HTML e extrair o preço.

### **Por que Playwright?**

| Playwright | Selenium | BeautifulSoup |
|------------|----------|---------------|
| ✅ Rápido | ⚠️ Mais lento | ❌ Não executa JS |
| ✅ Headless | ✅ Headless | ❌ Só HTML estático |
| ✅ Async | ⚠️ Sync apenas | ✅ Simples |
| ✅ Contexto persistente | ❌ Cookies manuais | - |

### **Como funciona no nosso projeto:**

```python
# 1. Inicia o navegador
self.playwright = sync_playwright().start()

# 2. Abre contexto persistente (mantém login)
self.context = self.playwright.chromium.launch_persistent_context(
    user_data_dir="playwright_profile",  # ← Salva cookies/sessão aqui
    headless=False                       # ← Mostra o navegador
)

# 3. Usa a página
self.page = self.context.pages[0]

# 4. Seleciona elementos do DOM
timeline = self.page.query_selector(".roulette-history_line")
numeros = timeline.query_selector_all("[class*='history-item-value__text']")
valor = numeros[0].inner_text().strip()
```

**Por que "persistente"?**
Sem persistência, toda vez que você rodar o bot, teria que fazer login de novo. Com `user_data_dir`, o navegador lembra de você.

---

## <a name="polling-vs-websocket"></a> ⏱️ **2. POLLING VS WEBSOCKET**

### **Polling (o que usamos)**

```python
while True:
    numero = monitor.watch()  # Pergunta: "tem número novo?"
    time.sleep(0.5)           # Espera 500ms
```

**Analogia:** Você pergunta pro seu amigo a cada 5 segundos: "Já chegou o ônibus?". Ele responde "não... não... não... SIM!".

**Vantagens:**
- Simples de implementar
- Funciona em qualquer site
- Não depende de API

**Desvantagens:**
- Desperdiça CPU (pergunta mesmo sem mudança)
- Latência (pode perder eventos entre um `sleep` e outro)

### **WebSocket (ideal, mas não disponível)**

```python
# Hipotético (não funciona neste site)
websocket.on("numero_novo", lambda numero: print(numero))
```

**Analogia:** Seu amigo te avisa automaticamente quando o ônibus chegar. Você não precisa ficar perguntando.

**Vantagens:**
- Notificação instantânea
- Zero latência
- Economiza CPU

**Desvantagens:**
- Precisa que o site exponha WebSocket público
- Mais complexo de implementar

**Por que não usamos WebSocket aqui?**
O site da roleta usa WebSocket **internamente** (entre servidor e cliente), mas não expõe uma API pública para você se conectar. Você teria que fazer engenharia reversa (interceptar o tráfego), o que é complexo e pode violar termos de serviço.

---

## <a name="logging"></a> 📝 **3. LOGGING PROFISSIONAL**

### **Por que não usar `print()`?**

| `print()` | `logging` |
|-----------|-----------|
| ❌ Perde tudo quando crashar | ✅ Salva em arquivo |
| ❌ Não tem níveis (tudo igual) | ✅ INFO, WARNING, ERROR |
| ❌ Difícil de debugar depois | ✅ Busca por data/horário |
| ❌ Poluído em produção | ✅ Filtra por nível |

### **Como funciona:**

```python
logger.debug("Detalhes técnicos (só em desenvolvimento)")
logger.info("Informação normal (operações)")
logger.warning("Algo estranho, mas não crítico")
logger.error("Erro recuperável")
logger.critical("Sistema vai crashar!")
```

**Exemplo real do nosso projeto:**

```python
logger.info(f"Número detectado: {numero}")  # ← Vai pro terminal E pro arquivo
```

**Rotação de logs:**
```python
RotatingFileHandler(
    'logs/bot.log',
    maxBytes=5*1024*1024,  # 5MB
    backupCount=3          # Mantém 3 arquivos antigos
)
```

Quando `bot.log` atingir 5MB:
1. `bot.log` → `bot.log.1`
2. `bot.log.1` → `bot.log.2`
3. `bot.log.2` → `bot.log.3`
4. `bot.log.3` → deletado
5. Cria novo `bot.log` vazio

**Por que é importante:**
Em produção, você não está olhando o terminal 24/7. Se o bot crashar às 3h da manhã, você olha o log no dia seguinte e vê exatamente o que aconteceu.

---

## <a name="tratamento-de-erros"></a> 🛡️ **4. TRATAMENTO DE ERROS E RETRY**

### **Problema:** Sites são instáveis

- React re-renderiza a página → elementos somem temporariamente
- Internet cai por 2 segundos
- Site demora a responder

Se você não tratar erros, o bot crasharia toda hora.

### **Solução 1: Try/Except**

```python
try:
    timeline = self.page.query_selector(".timeline")
    if not timeline:
        return None  # ← Não crasha, apenas retorna vazio
except Error:
    return None  # ← Playwright lançou erro, ignora
```

### **Solução 2: Retry com Backoff Exponencial**

```python
for attempt in range(MAX_RETRIES):
    try:
        # Tenta executar
        return resultado
    except Error:
        wait_time = RETRY_DELAY * (2 ** attempt)  # 2s, 4s, 8s...
        time.sleep(wait_time)
```

**Por que exponencial?**
Se o erro é temporário (ex: React re-renderizando), 2 segundos podem resolver. Se é algo pior (site caiu), esperar 8 segundos dá mais chance de recuperação.

### **Solução 3: Health Check**

```python
def is_page_alive(self):
    try:
        self.page.evaluate("() => document.title")  # ← Testa se a página responde
        return True
    except:
        return False
```

Se a página não responder, tenta recarregar:

```python
if not self.is_page_alive():
    self.page.reload()
```

---

## <a name="persistência"></a> 💾 **5. PERSISTÊNCIA DE DADOS (SQLite)**

### **Por que salvar dados?**

Imagine que o bot detectou 100 números, depois crashou. Sem banco de dados, você perdeu tudo.

### **SQLite vs MySQL vs MongoDB**

| SQLite | MySQL | MongoDB |
|--------|-------|---------|
| ✅ Arquivo local | ⚠️ Servidor externo | ⚠️ Servidor externo |
| ✅ Zero configuração | ❌ Instalar servidor | ❌ Instalar servidor |
| ✅ Perfeito para projetos pequenos | ✅ Para produção grande | ✅ Para dados não estruturados |

Para nosso bot, SQLite é **perfeito** porque:
- Não precisa instalar nada
- Um único arquivo `roulette.db`
- Fácil de fazer backup (copia o arquivo)

### **Schema do banco:**

```sql
CREATE TABLE numbers (
    id INTEGER PRIMARY KEY,
    number INTEGER,                    -- Número detectado (0-36)
    detected_at TIMESTAMP,             -- Quando foi detectado
    telegram_sent BOOLEAN,             -- Enviou pro Telegram?
    strategy_text TEXT                 -- Estratégia gerada
);
```

### **Como usar:**

```python
db = Database()
db.save_number(17, telegram_sent=True, strategy="Aposte no preto")

# Depois, consulta
last_numbers = db.get_last_numbers(10)
```

**Vantagens:**
- Sobrevive a crashes
- Permite análise posterior (ex: "qual número saiu mais?")
- Rastreabilidade completa (forense)

---

## <a name="métricas"></a> 📊 **6. MÉTRICAS E HEALTH CHECKS**

### **O que são métricas?**
Números que te dizem **como o sistema está se comportando**.

**Métricas do nosso bot:**
- **Uptime**: Há quanto tempo está rodando sem crashar?
- **Numbers detected**: Quantos números detectou?
- **Errors count**: Quantos erros aconteceram?
- **Time since last number**: Faz quanto tempo que não detecta nada?

### **Por que são importantes?**

**Cenário 1:** Sistema aparenta estar funcionando, mas não detecta números há 10 minutos.
→ Health check alerta: "Algo errado! Última detecção foi há 600s".

**Cenário 2:** Muitos erros consecutivos.
→ Sistema tenta recarregar a página automaticamente.

### **Implementação:**

```python
@dataclass
class Metrics:
    start_time: float
    numbers_detected: int = 0
    errors_count: int = 0
    last_number_time: float = 0
    
    def uptime_seconds(self) -> float:
        return time.time() - self.start_time
```

### **Health Monitor:**

```python
class HealthMonitor:
    ALERT_THRESHOLD_NO_NUMBER = 300  # 5 minutos
    
    def check_health(self):
        if metrics.time_since_last_number() > 300:
            logger.warning("⚠️ Nenhum número detectado há 5 minutos!")
```

**Analogia:** É como o painel do carro mostrando temperatura do motor, velocidade, combustível. Você não precisa olhar sempre, mas se algo der errado, você vê no painel.

---

## <a name="arquitetura"></a> 🏗️ **7. ARQUITETURA DO PROJETO**

### **Separação de Responsabilidades**

```
main.py           → Orquestrador (junta tudo)
scraper/monitor   → Comunicação com site (Playwright)
telegram_bot/bot  → Comunicação com Telegram
strategy/engine   → Lógica de negócio (estratégias)
utils/            → Ferramentas auxiliares (logging, DB, métricas)
```

**Por que separar?**
1. **Manutenibilidade**: Se o Telegram mudar API, você só mexe em `bot.py`
2. **Testabilidade**: Pode testar `monitor.py` sem rodar o Telegram
3. **Reusabilidade**: Pode usar `logger.py` em outros projetos

### **Fluxo de Dados:**

```
Site → Playwright → GameMonitor → main.py → TelegramBot → Telegram
                                     ↓
                                  Database
                                     ↓
                                   Logs
```

### **Padrões Usados:**

**1. Singleton Pattern (Database)**
```python
db = Database()  # ← Uma única instância compartilhada
```

**2. Observer Pattern (Polling)**
```python
while True:
    numero = monitor.watch()  # ← Observa mudanças
```

**3. Retry Pattern (Tratamento de erros)**
```python
for attempt in range(MAX_RETRIES):
    try:
        # ...
```

---

## 🎯 **RESUMO PARA LEVAR**

1. **Playwright** = navega sites como um humano, mas automatizado
2. **Polling** = pergunta "mudou?" repetidamente (simples, mas menos eficiente que WebSocket)
3. **Logging** = diário do bot (essencial em produção)
4. **Retry** = tenta novamente quando falha (torna robusto)
5. **SQLite** = memória persistente (não perde dados)
6. **Métricas** = painel de controle (saúde do sistema)

---

## 📖 **PRÓXIMOS ESTUDOS RECOMENDADOS**

1. **Async/Await** (Playwright assíncrono)
2. **Docker** (rodar em container)
3. **CI/CD** (deploy automatizado)
4. **WebSockets** (comunicação bidirecional)
5. **Redis** (cache distribuído)
6. **Prometheus/Grafana** (monitoramento visual)

---

**Parabéns!** 🎉 Você agora entende os conceitos fundamentais de um bot de produção.
