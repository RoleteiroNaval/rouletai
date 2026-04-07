# 🧪 RELATÓRIO TÉCNICO DE ANÁLISE DE PROTOCOLO (Hipótese Baseada em Padrões)

## 1. Estrutura do WebSocket (Pragmatic Play)

A partir da análise de implementações comuns da Pragmatic (baseado em ws_analyzer), o fluxo de mensagens tende a seguir este padrão:

### A. Heartbeat (Frequência: ~5s)
Mensagens curtas para manter conexão:
```json
{"type": "ping", "serverTime": 1700000000}
```
**Ação**: Ignorar.

### B. MUDANÇA DE ESTADO (Crucial)
A mensagem mais importante costuma vir com `type: "gameResult"` ou dentro de um objeto `game`.

**Payload Típico (Hipótese para Validação):**
```json
{
  "type": "gameResult",
  "tableId": "auto-roulette-1",
  "gameId": "8237492374",   <-- ID ÚNICO DO GIRO
  "result": {
      "score": 14,          <-- O NÚMERO QUE QUEREMOS
      "color": "red",
      "outcome": "win"
  },
  "timestamp": 1700000123
}
```

## 2. Critérios de Validação (FASE 2)

Para garantir integridade e evitar duplicação, o código final implementará as seguintes regras estritas:

### ✅ Regra 1: O Evento "Gatilho"
Só processaremos mensagens que contenham EXPLICITAMENTE:
- `gameResult` (ou chave equivalente descoberta na análise)
- E um campo numérico válido (0-36).

### ✅ Regra 2: Anti-Duplicação por ID
Não basta o número mudar. O `gameId` ou `roundId` DEVE mudar.
- Se `current_round_id == incoming_round_id`: IGNORAR.
- Motivo: O servidor pode enviar o mesmo resultado 2x (ex: ao terminar a animação e ao pagar as apostas).

### ✅ Regra 3: Validação de Tipo
O valor extraído DEVE ser convertido para `int`.
- Se falhar (ex: "None", "Waiting"): IGNORAR.

## 3. Instruções para o Usuário (FASE 3 - Execução)

1. **Rode o Analisador Primeiro**:
   ```bash
   python ws_analyzer.py
   ```
2. **Observe o Log**: Aguarde um giro terminar.
3. **Identifique o JSON**: Copie o JSON que aparecer logo após o número sair na tela.
4. **Valide as Chaves**:
   - É `score`? É `winningNumber`? É `value`?
   - Onde está o ID do round?
5. **Ajuste o Código Final**: Edite `pragmatic_ws.py` com as chaves exatas encontradas.

---
**Nota**: O código do `pragmatic_ws.py` já foi estruturado esperando encontrar `gameResult` e `score`. Se o analisador mostrar algo diferente (ex: `outcomes`), basta alterar a linha de extração na classe `PragmaticMonitor`.
