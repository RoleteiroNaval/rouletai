// PWA WebSocket Client V4 - Production Realtime Signal Receiver
class PWAWebSocketClient {
    constructor(wsUrl = 'ws://localhost:8765', token = 'win_secret_2024') {
        this.wsUrl = wsUrl;
        this.token = token;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000;
        this.connected = false;
        this.state = 'DISCONNECTED'; // CONNECTED | RECONNECTING | DISCONNECTED
        this.stats = {
            signalsReceived: 0,
            latencyAvg: 0,
            reconnects: 0
        };
        this.init();
    }

    init() {
        this.connect();
        setInterval(() => this.updateUI(), 1000);
    }

    updateState(newState) {
        this.state = newState;
        document.dispatchEvent(new CustomEvent('wsStateChange', { detail: newState }));
        console.log('📡 State:', newState);
    }

    connect() {
        if (this.ws && this.ws.readyState === WebSocket.CONNECTING) return;
        
        this.updateState('CONNECTING');
        this.ws = new WebSocket(this.wsUrl);

        this.ws.onopen = () => {
            this.reconnectAttempts = 0;
            this.connected = true;
            this.updateState('CONNECTED');
            console.log('✅ Connected, authenticating...');
            this.ws.send(JSON.stringify({ type: 'auth', token: this.token }));
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                const latency = Date.now() - (data.timestamp || 0);
                this.stats.signalsReceived++;
                this.stats.latencyAvg = (this.stats.latencyAvg * 0.9) + (latency * 0.1);
                
                console.log('📨 Signal:', data, `latency:${latency}ms`);
                
                // Dispatch to voice engine
                document.dispatchEvent(new CustomEvent('signal', { detail: data }));
                
                if (data.type === 'auth_ok') {
                    console.log('🔐 Auth success');
                } else if (data.type === 'ping') {
                    this.ws.send(JSON.stringify({ type: 'pong' }));
                }
            } catch (e) {
                console.error('Parse error:', e);
            }
        };

        this.ws.onclose = (event) => {
            this.connected = false;
            this.updateState('RECONNECTING');
            console.log('🔌 Disconnected:', event.code, 'Reconnecting...', this.reconnectAttempts);
            this.stats.reconnects++;
            
            setTimeout(() => {
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    this.connect();
                } else {
                    this.updateState('DISCONNECTED');
                    console.error('❌ Max reconnect attempts reached');
                }
            }, this.reconnectDelay * this.reconnectAttempts);
        };

        this.ws.onerror = (error) => {
            console.error('❌ WS Error:', error);
        };
    }

    getStats() {
        return {
            state: this.state,
            connected: this.connected,
            signalsReceived: this.stats.signalsReceived,
            latencyAvg: Math.round(this.stats.latencyAvg),
            reconnects: this.stats.reconnects
        };
    }

    updateUI() {
        const stats = this.getStats();
        // Update your UI elements here
        if (window.location.pathname.includes('index.html')) {
            document.getElementById('status-dot')?.classList.toggle('connected', stats.connected);
            document.getElementById('status-text') && (document.getElementById('status-text').textContent = stats.connected ? 'conectado' : 'desconectado');
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Global client instance
const wsClient = new PWAWebSocketClient();

// Signal event listener example
document.addEventListener('signal', (e) => {
    const signal = e.detail;
    console.log('🎯 Processing signal:', signal);
    
    // Trigger voice
    if (window.voiceEngine) {
        voiceEngine.processSignal(signal);
    }
    
    // Update UI
    const lastNumberEl = document.getElementById('last-number');
    if (lastNumberEl) lastNumberEl.textContent = signal.number;
});

