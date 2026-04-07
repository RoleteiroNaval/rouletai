# Integração Roleta Brasileira (Playtech WebSocket)

Este módulo substitui a leitura de tela pelo uso direto do WebSocket da Playtech, que é mais rápido e confiável.

## 🚀 Como Configurar

1. **Obtenha o URL do WebSocket**:
   - Abra a [Roleta Brasileira](https://geralbet.bet.br/games/playtech/roleta-brasileira) no Chrome.
   - Pressione `F12` -> Aba **Network** -> Filtro **WS**.
   - Recarregue a página.
   - Procure por conexões WebSocket (geralmente `ws` ou `socket.io`).
   - Copie o **Request URL**.

2. **Analise o Protocolo (Obrigatório)**:
   - Antes de rodar o bot, precisamos confirmar qual campo tem o número.
   - Edite `playtech_ws_analyzer.py` e cole o URL na variável `WS_URL`.
   - Rode: `python playtech_ws_analyzer.py`
   - Gire a roleta e veja o log. Procure por mensagens com `win`, `result` ou `score`.
   - Anote o nome exato do campo (ex: `outcome`, `value`, `result.win`).

3. **Configure o Bot**:
   - Abra `playtech_ws.py`.
   - Cole o URL em `WS_URL`.
   - Ajuste a lógica dentro de `_on_message` se o campo for diferente do padrão (`value`, `score`, etc).

## 📜 Como Rodar

Para iniciar o bot no modo Playtech WS:

```bash
python main_playtech.py
```

## 🛠️ Arquivos

- `playtech_ws_analyzer.py`: Ferramenta para ver as mensagens cruas.
- `playtech_ws.py`: O módulo de conexão que extrai o número.
- `main_playtech.py`: O bot principal adaptado para usar o módulo acima.
