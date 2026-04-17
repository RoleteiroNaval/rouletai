# 🎓 GUIA DIDÁTICO: CONCEITOS DE DESENVOLVIMENTO - PROJETO COMPLETO

Este documento explica os conceitos técnicos usados neste projeto completo de monitoramento e análise de roleta, de forma didática.

---

## 📚 **ÍNDICE**

1. [Arquitetura Geral do Sistema](#arquitetura)
2. [Monitoramento de Roleta (DOM vs WebSocket)](#monitoramento)
3. [Engine de Estratégias](#estrategias)
4. [Sistema de Analytics e Performance](#analytics)
5. [Frontend Vision Pro (Next.js)](#frontend)
6. [Backend Server (Express + Socket.IO)](#backend)
7. [Sistema de Agentes (Memory, Strategy, Risk)](#agentes)
8. [Banco de Dados e Persistência](#database)
9. [Progressive Web App (PWA)](#pwa)
10. [Deploy com Docker](#docker)

---

## <a name="arquitetura"></a> 🏗️ **1. ARQUITETURA GERAL DO SISTEMA**

### **Visão Geral**

Este projeto é um **sistema distribuído** para monitoramento em tempo real de roleta online, composto por múltiplas camadas:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MONITOR       │    │   ENGINE        │    │   FRONTEND      │
│   (Python)      │◄──►│   (Python)      │◄──►│   (Next.js)     │
│                 │    │                 │    │                 │
│ • Playwright    │    │ • Estratégias   │    │ • Dashboard     │
│ • WebSocket     │    │ • Analytics     │    │ • Sinais RT     │
│ • Telegram      │    │ • Database      │    │ • Charts        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   BACKEND       │
                    │   (Express)     │
                    │                 │
                    │ • API REST      │
                    │ • WebSocket     │
                    │ • Agentes AI    │
                    │ • PostgreSQL    │
                    └─────────────────┘
```

**Fluxo de Dados:**
1. **Monitor** detecta número na roleta
2. **Engine** analisa histórico e gera estratégia
3. **Backend** processa com agentes de IA
4. **Frontend** exibe sinais em tempo real
5. **Telegram** envia notificações

---

## <a name="monitoramento"></a> 📡 **2. MONITORAMENTO DE ROLETA (DOM vs WebSocket)**

### **Dois Modos de Monitoramento**

| Modo | Tecnologia | Vantagens | Desvantagens |
|------|------------|-----------|--------------|
| **DOM Scraping** | Playwright | Simples, confiável | Latência ~500ms |
| **WebSocket** | Interceptação | Tempo real | Complexo, frágil |

#### **Modo DOM (main.py)**

```python
# Abre navegador e monitora elementos da página
monitor = GameMonitor()
while True:
    numero = monitor.watch()  # Lê DOM a cada 500ms
    if numero:
        processar_numero(numero)
    time.sleep(0.5)
```

**Quando usar:** Desenvolvimento, debugging, sites sem WebSocket público.

#### **Modo WebSocket (main_playtech.py)**

```python
# Intercepta pacotes WebSocket internos do site
monitor = PlaytechMonitor()
monitor.start()  # Conecta ao WebSocket

while True:
    data = monitor.watch()  # Recebe pacotes em tempo real
    numero = data.get("number")
    if numero:
        processar_numero(numero)
```

**Quando usar:** Produção, baixa latência, análise avançada.

---

## <a name="estrategias"></a> 🎯 **3. ENGINE DE ESTRATÉGIAS**

### **Como Funciona uma Estratégia**

Cada estratégia define **alvos de entrada** e **proteção**:

```python
# Exemplo: Estratégia "Vizinhos do Zero"
entry_targets = [26, 0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3]
protection_targets = [0]  # Zero sempre é proteção
```

### **Estado da Estratégia**

```python
class StrategyState:
    def __init__(self):
        self.active = False
        self.entry_targets = set()     # Números para WIN
        self.protection_targets = set() # Números para gale
        self.attempt = 0               # Contador de gales
        self.max_attempts = 3          # Máximo de gales

    def process_number(self, number: int):
        if number in self.entry_targets:
            return "WIN_ENTRY"
        if number in self.protection_targets:
            return "WIN_PROTECTION"
        if self.attempt < self.max_attempts:
            return "PROTECTION"  # Continua apostando
        return "LOSS"            # Para tudo
```

### **Geração Automática**

```python
# Engine analisa histórico e seleciona melhor estratégia
def run_engine(history: list[int], memory_agent, base_number: int):
    # 1. Filtra contexto (últimos 50 números)
    context = context_filter.analyze_window(history[-50:])
    
    # 2. Busca estratégias compatíveis
    candidates = registry.find_matching_strategies(base_number, context)
    
    # 3. Memory Agent lembra padrões passados
    memory_input = memory_agent.recall_similar_patterns(history)
    
    # 4. Seleciona estratégia otimizada
    return get_optimized_strategy(candidates, memory_input)
```

---

## <a name="analytics"></a> 📊 **4. SISTEMA DE ANALYTICS E PERFORMANCE**

### **Métricas Principais**

```python
@dataclass
class Metrics:
    numbers_detected: int = 0
    green_count: int = 0        # Wins
    red_count: int = 0          # Losses
    accuracy: float = 0.0       # Taxa de acerto
    avg_cycles: float = 0.0     # Ciclos médios por win
```

### **Context Filter**

Analisa **janelas de histórico** para detectar padrões:

```python
class ContextFilter:
    def analyze_window(self, history_window: list[int]):
        # Estatísticas da janela
        stats = {
            'hot_numbers': self.get_most_frequent(history_window),
            'cold_numbers': self.get_least_frequent(history_window),
            'zero_ratio': history_window.count(0) / len(history_window),
            'red_black_balance': self.calculate_color_balance(history_window)
        }
        return stats
```

### **Turbulence Monitor**

Detecta **anomalias** no jogo:

```python
class TurbulenceMonitor:
    def check_turbulence(self, recent_numbers: list[int]):
        # Múltiplos zeros seguidos = turbulência
        if recent_numbers.count(0) > 3:
            return "HIGH_TURBULENCE"
        
        # Mesma cor 15x = possível manipulação
        if self.same_color_streak(recent_numbers) > 15:
            return "COLOR_BIAS"
            
        return "NORMAL"
```

---

## <a name="frontend"></a> 🌐 **5. FRONTEND VISION PRO (Next.js)**

### **Tecnologias**

- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS
- **State:** Zustand
- **Real-time:** Socket.IO Client
- **Charts:** Recharts

### **Store de Sinais (Zustand)**

```typescript
interface Signal {
  id: string;
  number: number;
  strategy: string;
  confidence: number;
  entry: string[];      // Alvos de entrada
  protection: string[]; // Alvos de proteção
  status: 'IDLE' | 'ANALYZING' | 'SIGNAL_READY' | 'PROTECTION';
}

const useSignalStore = create<SignalStore>()((set, get) => ({
  signals: [],
  activeSignal: null,
  serverStatus: 'disconnected',
  
  connect: () => {
    const socket = io('http://localhost:4000');
    
    socket.on('signal', (signal) => {
      // Adiciona novo sinal à lista
      set(state => ({
        signals: [signal, ...state.signals.slice(0, 49)],
        activeSignal: signal
      }));
      
      // Vibração se confiança alta
      if (signal.confidence > 0.85 && 'vibrate' in navigator) {
        navigator.vibrate([100, 50, 100]);
      }
    });
  }
}));
```

### **Componentes Principais**

```tsx
// GameCard.tsx - Exibe sinal ativo
function GameCard({ signal }: { signal: Signal }) {
  return (
    <Card className="p-6">
      <div className="text-4xl font-bold text-center mb-4">
        {signal.number}
      </div>
      
      <Badge variant="secondary" className="mb-4">
        {signal.strategy}
      </Badge>
      
      <div className="space-y-2">
        <div>
          <Label>Entrada:</Label>
          <div className="flex flex-wrap gap-1">
            {signal.entry.map(num => (
              <Badge key={num} variant="default">{num}</Badge>
            ))}
          </div>
        </div>
        
        <div>
          <Label>Proteção:</Label>
          <div className="flex flex-wrap gap-1">
            {signal.protection.map(num => (
              <Badge key={num} variant="outline">{num}</Badge>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
```

---

## <a name="backend"></a> ⚙️ **6. BACKEND SERVER (Express + Socket.IO)**

### **Arquitetura**

```typescript
// server/index.ts
const app = express();
const httpServer = createServer(app);

// Middleware
app.use(express.json());
app.use(session({ store: new PgSession({ pool }) }));

// WebSocket
const io = new Server(httpServer, { cors: { origin: "*" } });

// RAG System
const vectorStore = new VectorStore();
const realRag = new RealRAG(vectorStore);

// Agentes
const memoryAgent = new MemoryAgent();
const strategyAgent = new StrategyAgent();
const riskAgent = new RiskAgent();
```

### **Endpoints Principais**

```typescript
// Webhook para sinais do Python
app.post('/api/webhook/signal', (req, res) => {
  const signal = req.body;
  
  // Processa com agentes
  const enrichedSignal = await strategyAgent.enhance(signal);
  
  // Emite via WebSocket para frontend
  io.emit('signal', enrichedSignal);
  
  res.json({ success: true });
});

// API para histórico
app.get('/api/signals/history', async (req, res) => {
  const signals = await db.query.signals.findMany({
    orderBy: desc(signals.timestamp),
    limit: 50
  });
  res.json(signals);
});
```

### **Sistema RAG (Retrieval-Augmented Generation)**

```typescript
class RealRAG {
  async query(question: string): Promise<string> {
    // 1. Converte pergunta em embedding
    const queryEmbedding = await this.embeddings.embedQuery(question);
    
    // 2. Busca documentos similares no vector store
    const relevantDocs = await this.vectorStore.similaritySearch(
      queryEmbedding, 
      5
    );
    
    // 3. Gera resposta baseada no contexto
    const context = relevantDocs.map(doc => doc.pageContent).join('\n');
    
    return await this.llm.generate(`
      Contexto: ${context}
      Pergunta: ${question}
      Responda baseado apenas no contexto fornecido.
    `);
  }
}
```

---

## <a name="agentes"></a> 🤖 **7. SISTEMA DE AGENTES (Memory, Strategy, Risk)**

### **Memory Agent**

Lembra **padrões históricos** para melhorar decisões:

```python
class MemoryAgent:
    def recall_similar_patterns(self, current_history: list[int]):
        # Busca padrões similares no histórico
        similar_patterns = self.db.query_similar_histories(
            current_history[-20:]  # Últimos 20 números
        )
        
        # Calcula sucesso médio desses padrões
        success_rate = self.calculate_pattern_success(similar_patterns)
        
        return {
            'similar_patterns': similar_patterns,
            'avg_success_rate': success_rate,
            'recommended_adjustments': self.generate_adjustments(success_rate)
        }
```

### **Strategy Agent**

Otimiza **seleção de estratégias**:

```typescript
class StrategyAgent {
  async enhance(signal: Signal): Promise<EnhancedSignal> {
    // Análise de risco
    const risk = await this.riskAgent.assess(signal);
    
    // Ajuste baseado em histórico
    const historical_performance = await this.analyzeHistoricalPerformance(
      signal.strategy
    );
    
    // Otimização de alvos
    const optimized_targets = await this.optimizeTargets(
      signal.entry,
      signal.protection,
      historical_performance
    );
    
    return {
      ...signal,
      risk_score: risk.score,
      confidence_adjusted: this.adjustConfidence(signal.confidence, risk),
      optimized_entry: optimized_targets.entry,
      optimized_protection: optimized_targets.protection
    };
  }
}
```

### **Risk Agent**

Avalia **risco em tempo real**:

```typescript
class RiskAgent {
  async assess(signal: Signal): Promise<RiskAssessment> {
    const factors = {
      // Frequência do número base
      base_frequency: await this.getNumberFrequency(signal.number),
      
      // Turbulência atual
      turbulence: this.turbulenceMonitor.getCurrentLevel(),
      
      // Performance recente da estratégia
      strategy_performance: await this.getStrategyRecentPerformance(
        signal.strategy
      ),
      
      // Correlação com sinais anteriores
      correlation: this.calculateSignalCorrelation(signal)
    };
    
    const risk_score = this.calculateOverallRisk(factors);
    
    return {
      score: risk_score,
      factors,
      recommendation: risk_score > 0.7 ? 'HIGH_RISK' : 'ACCEPTABLE'
    };
  }
}
```

---

## <a name="database"></a> 💾 **8. BANCO DE DADOS E PERSISTÊNCIA**

### **Duas Bases de Dados**

| SQLite (Python) | PostgreSQL (Node.js) |
|-----------------|----------------------|
| Histórico números | Sessões usuário |
| Estratégias | Sinais em tempo real |
| Analytics | Configurações |
| Backup local | Dados relacionais |

### **Schema SQLite**

```sql
-- Histórico de números
CREATE TABLE numbers (
    id INTEGER PRIMARY KEY,
    number INTEGER,
    detected_at TIMESTAMP,
    telegram_sent BOOLEAN,
    strategy_applied TEXT
);

-- Sessões de execução
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    total_numbers INTEGER,
    successful_strategies INTEGER
);

-- Analytics de estratégias
CREATE TABLE strategy_analytics (
    id INTEGER PRIMARY KEY,
    strategy_id INTEGER,
    result TEXT,  -- WIN_ENTRY, WIN_PROTECTION, LOSS
    profit_loss REAL,
    cycle_length INTEGER,
    timestamp TIMESTAMP
);
```

### **Backup Automático**

```python
class BackupSystem:
    def __init__(self):
        self.backup_interval = 3600  # 1 hora
        self.max_backups = 10
        
    def start(self):
        while True:
            self.create_backup()
            time.sleep(self.backup_interval)
    
    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"data/backups/database_{timestamp}.db"
        
        # Copia arquivo SQLite
        shutil.copy("data/roulette.db", backup_path)
        
        # Remove backups antigos
        self.cleanup_old_backups()
```

---

## <a name="pwa"></a> 📱 **9. PROGRESSIVE WEB APP (PWA)**

### **Manifest.json**

```json
{
  "name": "Radar do Green",
  "short_name": "RDG",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#000000",
  "theme_color": "#00ff00",
  "icons": [
    {
      "src": "/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

### **Service Worker**

```javascript
// sw.js
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('radar-v1').then((cache) => {
      return cache.addAll([
        '/',
        '/manifest.json',
        '/icon-192x192.png'
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

### **Funcionalidades Offline**

- **Cache de Sinais:** Últimos 50 sinais ficam disponíveis offline
- **Notificações Push:** Alertas mesmo sem app aberto
- **Sincronização:** Quando volta online, sincroniza dados

---

## <a name="docker"></a> 🐳 **10. DEPLOY COM DOCKER**

### **Dockerfile Backend**

```dockerfile
FROM node:18-alpine

# Instala dependências
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Copia código
COPY . .

# Build da aplicação
RUN npm run build

# Porta
EXPOSE 4000

# Comando
CMD ["npm", "start"]
```

### **Dockerfile Frontend**

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Nginx para servir static files
FROM nginx:alpine
COPY --from=builder /app/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

### **Docker Compose**

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "4000:4000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/radar
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build: 
      context: ./vision-pro
      dockerfile: ../docker/Dockerfile.frontend
    ports:
      - "3000:80"

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: radar
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

### **Benefícios do Docker**

- **Isolamento:** Cada serviço em container separado
- **Escalabilidade:** Fácil aumentar réplicas
- **Consistência:** Mesmo ambiente em dev/prod
- **Deploy Simplificado:** Um comando para tudo

---

## 🎯 **RESUMO PARA LEVAR**

1. **Arquitetura Distribuída:** Python (monitor/engine) + Node.js (backend) + Next.js (frontend)
2. **Monitoramento Dual:** DOM scraping ou WebSocket interception
3. **Engine de Estratégias:** Análise histórica + agentes IA para otimização
4. **Analytics Avançado:** Performance tracking, risk assessment, turbulence detection
5. **Real-time:** Socket.IO para comunicação instantânea
6. **PWA:** App offline-capable com notificações push
7. **Docker:** Deploy consistente e escalável

---

## 📖 **PRÓXIMOS ESTUDOS RECOMENDADOS**

1. **Machine Learning:** Modelos preditivos para roleta
2. **Big Data:** Análise de milhões de jogos históricos
3. **Blockchain:** Registros imutáveis de apostas
4. **Edge Computing:** Processamento próximo ao usuário
5. **IoT:** Integração com dispositivos físicos
6. **AI Agents:** Sistemas multi-agente mais sofisticados

---

**Parabéns!** 🎉 Você agora entende a arquitetura completa deste sistema avançado de monitoramento de roleta.</content>
<parameter name="filePath">GUIA_DIDATICO_COMPLETO.md