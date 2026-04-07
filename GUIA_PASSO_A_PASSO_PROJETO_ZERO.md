# 🚀 GUIA: CONSTRUINDO SEU BOT DE ROLETA DO ZERO

Este guia foi criado para orientar o desenvolvimento de um sistema de análise e sinalização de roleta, baseado nas melhores práticas de arquitetura modular, robustez e escalabilidade.

---

## 🏗️ 1. ARQUITETURA DO PROJETO

Antes de digitar a primeira linha de código, entenda como o sistema deve ser dividido. A **Soberania de Responsabilidades** é a chave:

- **Monitor (Captura)**: Responsável apenas por obter o dado (número) do site ou WebSocket.
- **Engine (Inteligência)**: Responsável por analisar o histórico e decidir se há um sinal.
- **State Machine (Gestão)**: Responsável por controlar o ciclo de aposta (Entrada -> Gale 1 -> Gale 2 -> Win/Loss).
- **Bot (Comunicação)**: Responsável por enviar as mensagens para o Telegram.
- **Database (Memória)**: Responsável por guardar o histórico para relatórios.

---

## 📂 2. ESTRUTURA DE PASTAS RECOMENDADA

```text
meu_bot_roleta/
├── core/                # Nucleo do sistema
│   ├── monitor.py       # Captura de dados (Playwright/WS)
│   ├── engine.py        # Logica de análise de sinais
│   └── state.py         # Gestão de ciclos (Win/Loss/Gale)
├── telegram_bot/        # Interface com Telegram
│   ├── bot.py           # Configuração do Bot
│   └── formatter.py     # Formatação das mensagens (Stickers/Texto)
├── utils/               # Ferramentas auxiliares
│   ├── logger.py        # Configuração de logs profissionais
│   └── database.py      # Conexão com SQLite
├── data/                # Onde o banco de dados ficará
├── logs/                # Onde os arquivos de log serão salvos
├── main.py              # O "Cérebro" que orquestra tudo
├── .env                 # Chaves secretas (Token do Bot)
└── requirements.txt     # Dependências (Playwright, python-telegram-bot)
```

---

## 🛠️ 3. PASSO A PASSO DA CONSTRUÇÃO

### **Passo 1: O Monitor (Captura de Dados)**
Você precisa decidir se vai usar **Web Scraping** (Playwright) ou **WebSocket**.
- **Scraping**: Mais fácil, mas gasta mais CPU. Você "olha" o site e pega o texto.
- **WebSocket**: Mais rápido e leve, mas exige interceptar a comunicação do site.

> [!TIP]
> Comece com Playwright para validar a ideia, depois migre para WebSocket se precisar de performance extrema.

### **Passo 2: A Engine de Sinais**
Crie uma classe que recebe uma lista de números e retorna se deve entrar ou não.
```python
def check_signal(history: list[int]):
    # Exemplo: Se os últimos 3 números forem PRETOS
    if all(n in BLACK_NUMBERS for n in history[-3:]):
        return "SINAL_VERMELHO"
    return None
```

### **Passo 3: A Máquina de Estados (Ciclo de Aposta)**
Este é o erro mais comum de iniciantes. Não mande o sinal e esqueça! Você precisa monitorar o que acontece **depois** do sinal.
1. **SINAL EMITIDO**: Aguarda o próximo número.
2. **PRÓXIMO NÚMERO CHEGOU**: 
   - É o que previmos? -> **WIN** -> Volta ao estado de espera.
   - Não é? -> **GALE 1** -> Avisa o usuário para dobrar.
   - Passou do limite de Gales? -> **LOSS** -> Volta ao estado de espera.

### **Passo 4: Telegram e Formatação**
Use `python-telegram-bot`. Crie um arquivo de "templates" para as mensagens. Um bot profissional usa Stickers e formatação HTML/Markdown para ser visualmente atraente.

### **Passo 5: Persistência e Robustez**
1. **Banco de Dados**: Salve cada número e cada sinal. Isso permitirá que você crie relatórios de assertividade depois.
2. **Logs**: Se o bot parar às 4 da manhã, o log dirá se foi a internet que caiu ou se o site mudou o layout.
3. **Auto-Reboot**: Use um `while True` com um `try/except` global no `main.py` para que o bot tente se recuperar sozinho de erros.

---

## 🚀 4. FLUXO DE EXECUÇÃO (DENTRO DO BLOCO PRINCIPAL)

No seu `main.py`, o fluxo deve ser algo como:

```python
while True:
    try:
        numero = monitor.get_new_number()
        if numero:
            # 1. Salva no Banco
            db.save(numero)
            
            # 2. Processa na State Machine (Win/Loss de sinal anterior)
            resultado = state_machine.update(numero)
            if resultado:
                bot.send_result(resultado)
            
            # 3. Analisa novos sinais (Se não estivermos em um ciclo de Gale)
            if not state_machine.is_active:
                novo_sinal = engine.analyze(db.get_history())
                if novo_sinal:
                    state_machine.activate(novo_sinal)
                    bot.send_signal(novo_sinal)
                    
    except Exception as e:
        logger.error(f"Erro crítico: {e}")
        time.sleep(5) # Espera antes de tentar de novo
```

---

## 💡 5. DICAS DE OURO

1. **Proteção do Zero**: Sempre considere o zero como perda ou proteção (dependendo da estratégia).
2. **Delay de Detecção**: Roletas costumam ter um delay entre o número aparecer no visor e ele ser processado no histórico. Configure esperas curtas.
3. **Gestão de Banca**: Não teste estratégias com dinheiro real logo de cara. Crie um "Modo Simulação" no seu bot.
4. **Environment Variables**: Nunca coloque seu Token do Telegram direto no código. Use um arquivo `.env`.

---

**Com essa estrutura, seu projeto fluirá de forma profissional e escalável!** 🚀
