# 🧠 GUIA DIDÁTICO: ENGINE DE ESTRATÉGIAS E LÓGICA DE SINAIS

Este guia explica como a "Inteligência" do bot funciona, desde a detecção do número até o envio do sinal e a gestão do ciclo de aposta (Gale).

---

## 🏗️ **A ARQUITETURA DA ENGINE**

A Engine é dividida em 4 partes principais que trabalham juntas:

1.  **O Registro (`Registry`)**: Onde as estratégias são armazenadas.
2.  **O Parser**: O "tradutor" que transforma texto em números.
3.  **O Calculador**: Conhece a roda da roleta e calcula vizinhos/terminais.
4.  **O Gerenciador de Estados (`State Machine`)**: Controla se estamos esperando um sinal ou se já estamos em uma operação (Entrada, Proteção 1, 2, 3).

---

## 1. 🎯 **O GATILHO (TRIGGER)**
Toda estratégia começa com um **número gatilho**. É o número que acaba de sair na roleta.
- No `registry.py`, o número à esquerda (chave) é o gatilho.
- **Exemplo**: `17: { ... }` significa: "Quando sair o 17, analise esta estratégia."

---

## 2. 🗣️ **O TRADUTOR (PARSER)**
Para facilitar a criação de estratégias, usamos linguagem natural que o `parser.py` entende:

| Texto | O que o Parser faz |
| :--- | :--- |
| **"T1"** | Pega todos os números que terminam em 1 (1, 11, 21, 31). |
| **"com 2 vizinhos"** | Pega o alvo e adiciona 2 números para cada lado na roda. |
| **"9 / 19 / 29"** | Aceita múltiplos números separados por barra. |
| **"Tier"** | Pega a região específica da roleta (5, 8, 10, 11, 13, 16, 23, 24, 27, 30, 33, 36). |

**Como criar uma entrada profissional:**
`"T4 e T1 com 1 vizinho"` -> O parser vai pegar os terminais 4 e 1 e seus vizinhos imediatos na roda.

---

## 3. 🎡 **O CÁLCULO DE VIZINHOS**
A roleta não é uma sequência linear (0, 1, 2...). Ela é uma roda. O `calculator.py` contém a ordem exata:
`[0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27... ]`

Quando pedimos "0 com 1 vizinho", o calculador retorna: `[26, 0, 32]`.
- **26** (esquerda)
- **0** (centro)
- **32** (direita)

---

## 4. 🔄 **A MÁQUINA DE ESTADOS (CICLO DE VIDA)**
O `core.py` controla o estado atual da aposta através da classe `StrategyState`.

### **Estados do Ciclo:**
1.  **IDLE (Esperando)**: O bot está apenas "olhando" a roleta sair.
2.  **CONFIRMADO (Entrada)**: Um gatilho bateu! O bot envia o sinal no Telegram.
3.  **AGUARDANDO RESULTADO**: O próximo número sai.
    -   **Bateu no Alvo?** -> 🟢 **WIN** (Reseta para IDLE).
    -   **Não bateu?** -> 🟡 **PROTEÇÃO 1** (Aumenta a tentativa).
4.  **LIMITE ATINGIDO**: Se passar de 3 proteções sem bater -> 🔴 **LOSS**.

---

## 5. 🛠️ **EXEMPLO: CRIANDO SUA PRÓPRIA ESTRATÉGIA**

Se você quiser que o seu novo bot tenha uma estratégia diferente, basta seguir este padrão no `registry.py`:

```python
# Quando sair o número 20...
20: {
    "leitura": "Estratégia Customizada do Usuário",  # O que aparece no log
    "entrada": "T5 e T8 com 2 vizinhos",            # Seus alvos principais
    "cobertura": "T0 / 11 / 22 / 33",               # Seus alvos de proteção
},
```

### **O que o novo bot fará?**
1. Captura o número **20**.
2. Vê que tem uma estratégia para o **20**.
3. Calcula todos os números que fazem parte de `T5` e `T8` + 2 vizinhos.
4. Calcula a cobertura (Terminais 0 e Gêmeos).
5. Envia o sinal formatado pro Telegram.
6. Monitora os próximos giros para confirmar o **WIN** ou **LOSS**.

---

## 💡 **DICA DE OURO PARA O NOVO BOT**
Para que ele capture **EXATAMENTE** igual à nossa engine, ele deve usar o `StrategyRegistry.preload()`. Isso garante que todas as suas strings de texto sejam convertidas em listas de números reais antes da roleta começar a girar, evitando lentidão na hora de processar o sinal.
