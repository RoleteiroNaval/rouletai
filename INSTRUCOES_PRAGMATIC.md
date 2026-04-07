# Integração Roleta Pragmatic Play (WebSocket)

Este módulo permite conexão direta via WebSocket para captura ultrarrápida de resultados, substituindo a leitura de tela (OCR/DOM).

## 🚀 Como Configurar

1. **Obtenha o URL do WebSocket**:
   - Abra a roleta no navegador Google Chrome.
   - Pressione `F12` para abrir o DevTools.
   - Vá na aba **Network** -> **WS**.
   - Recarregue a página.
   - Localize a conexão WebSocket principal (geralmente inicia com `wss://gs...` ou similar).
   - Copie o **Request URL** completo.

2. **Configure o Código**:
   - Abra o arquivo `pragmatic_ws.py`.
   - Localize a variável `WS_URL` (linha 16).
   - Cole o URL que você copiou, substituindo o placeholder.

   Exemplo:
   ```python
   WS_URL = "wss://gs5.pragmaticplaylive.net/game?tableId=jsb123..."
   ```

## 📜 Como Rodar

Para iniciar o bot no modo Pragmatic Play (WebSocket), execute:

```bash
python main_pragmatic.py
```

**Nota**: O bot original (`main.py`) continua funcionando normalmente para a Roleta Playtech (modo leitura de tela).

## ⚠️ Detalhes Técnicos

- **Arquivo**: `pragmatic_ws.py` (Módulo de conexão isolado)
- **Runner**: `main_pragmatic.py` (Orquestrador duplicado)
- **JSON Parsing**: O bot busca por mensagens contendo `gameResult` e extrai o campo `score` ou `outcome`. Se a roleta mudar o formato do JSON, ajuste o método `_on_message` em `pragmatic_ws.py`.
