##############################################################################
# MOTOR PRINCIPAL DE DECISÃO – ESTRATÉGIAS DE NÚMEROS PARA ROLETA
##############################################################################

# INSTRUÇÕES CRÍTICAS (DOCUMENTAÇÃO EMBUTIDA PARA O BOT E PARA OS DEVS):
#
# 1. FINALIDADE:
#    Este arquivo é o MOTOR CENTRAL e o ÚNICO local de verdade das estratégias
#    para geração de sinais do bot de roleta. Só aqui devem ser definidas as
#    regras de decisão associadas a cada número de 0 a 36.
#
# 2. PADRÃO DE USO:
#    - Nenhuma rotina/engine/bot deve MODIFICAR essas estratégias em tempo de execução.
#    - Qualquer alteração de estratégia deve ser feita EXPLICITAMENTE por um DEV,
#      via edição direta e versionamento deste arquivo.
#
# 3. FORMATO ESTRITO:
#    - Cada número de 0 a 36 deve ter SEMPRE um dicionário de estratégia, mesmo
#      que seja temporariamente um placeholder.
#    - Os campos obrigatórios são:
#        leitura   -> string descritiva da lógica ou insight para o número
#        entrada   -> string com ação/recomendação, ou None caso não definida
#        cobertura -> string com cobertura ou None caso não definida
#    - Propriedades extras, como 'comentario', podem ser adicionadas como metadados.
#
# 4. BLACKLIST DE ESTRATÉGIAS:
#    - Números presentes na BLACKLIST (ex: 22,11,8,9,17,0,7,28,29,10,33) NÃO devem
#      gerar sinais, mesmo que possuam estratégia definida neste arquivo.
#    - Isso deve ser implementado no motor de decisão: se o número base pertence à blacklist,
#      a rotina de sinais deve pular o envio, registrar log e aguardar o próximo ciclo.
#
# 5. ATENÇÃO AO AGENTE/BOT:
#    - Sempre procure por ESTRATEGIAS[n] para cada número sorteado.
#    - Caso não encontre a chave, ou ela esteja como "Estratégia não definida", NÃO opere.
#    - NÃO modifique valores durante runtime; esse arquivo é de leitura permanente.
#    - Em caso de chave/estrutura ausente, notifique DEV imediatamente.
#
# 6. VERSÃO E ATUALIZAÇÕES:
#    - Sempre que o preset for modificado, registre a mudança no changelog do projeto
#      (versão, data, motivação); não utilize edits dinâmicos via outros módulos.
#
# 7. EXEMPLO DE USO NO AGENTE:
#    Estrategia = ESTRATEGIAS[numero_base]
#    if numero_base in BLACKLIST or Estrategia["leitura"] == "Estratégia não definida.":
#        # NÃO enviar sinal; apenas registrar ou pular ciclo.
#    else:
#        # Utilizar campos 'leitura', 'entrada', 'cobertura' para gerar mensagem de sinal.
#
# 8. SEGURANÇA DO SISTEMA:
#    - O bot depende 100% deste arquivo padronizado: NÃO utilize dados parciais!
#    - Em caso de dúvida sobre a estratégia de um número, utilize explicitamente o placeholder.
##############################################################################

# BLACKLIST de números que NÃO devem gerar sinais
BLACKLIST = [22, 11, 8, 9, 17, 0, 7, 28, 29, 10, 33]

# DICIONÁRIO DE ESTRATÉGIAS
ESTRATEGIAS = {
    0: {
        "leitura": "Zona do zero conexão de vizinhos.",
        "entrada": "8 vizinhos do número 26",
        "cobertura": "33, 5, 10, 14, 13, 8",
    },
    1: {
        "leitura": "Terminal dominante com continuidade.",
        "entrada": "T1 e T3 com 1 vizinho",
        "cobertura": "T4 / T7",
    },
    2: {
        "leitura": "Cluster técnico em terminal baixo.",
        "entrada": "T4 e T6 com 1 vizinho",
        "cobertura": "T5 / T2",
    },
    3: {
        "leitura": "Fluxo claro em terminais médios.",
        "entrada": "T3 e T6 com 1 vizinho",
        "cobertura": "T7 / T4",
    },
    4: {
        "leitura": "Terminal repetindo padrão anterior.",
        "entrada": "T4 e T1 com 1 vizinho",
        "cobertura": "T6 / T8",
    },
    5: {
        "leitura": "Terminal 5 puxando vizinhança.",
        "entrada": "T5 com 2 vizinhos",
        "cobertura": "T4 / T7",
    },
    6: {
        "leitura": "Cluster 6 3 9 ativo.",
        "entrada": "T4 e T3 com 1 vizinho",
        "cobertura": "T2 / T6 / T9",
    },
    7: {
        "leitura": "Estratégia não definida.",
        "entrada": None,
        "cobertura": None,
    },
    8: {
        "leitura": "Região Tier com extensão lateral.",
        "entrada": "Cobrir Tier (7 vizinhos) e 32 (3 vizinhos)",
        "cobertura": "T1",
    },
    9: {
        "leitura": "Estratégia não definida.",
        "entrada": None,
        "cobertura": None,
    },
    10: {
        "leitura": "Zero conectando terminais ativos.",
        "entrada": "T5 e T2 com 1 vizinho",
        "cobertura": "T0 / T7",
    },
    11: {
        "leitura": "Estratégia não definida.",
        "entrada": None,
        "cobertura": None,
    },
    12: {
        "leitura": "Terminal 2.",
        "entrada": "T2 e T4 com 1 vizinho",
        "cobertura": "T1 / T5",
    },
    13: {
        "leitura": "Terminal dominante em repetição.",
        "entrada": "T1 e T3 com 1 vizinho",
        "cobertura": "T2 / T6",
    },
    14: {
        "leitura": "Terminal 4.",
        "entrada": "T4 e T1 com 1 vizinho",
        "cobertura": "T2 / T5",
    },
    15: {
        "leitura": "Terminal 5 conectado ao zero.",
        "entrada": "T5 e T0 com 1 vizinho",
        "cobertura": "T1 / T4",
    },
    16: {
        "leitura": "Terminal 6.",
        "entrada": "T3 e T9 com 1 vizinho",
        "cobertura": "T6 / T8",
    },
    17: {
        "leitura": "Estratégia não definida.",
        "entrada": None,
        "cobertura": None,
    },
    18: {
        "leitura": "Terminal 8.",
        "entrada": "T8 e T5 com 1 vizinho",
        "cobertura": "T4 / T9",
    },
    19: {
        "leitura": "Terminal 9 puxando sequência.",
        "entrada": "T9 e T6 com 1 vizinho",
        "cobertura": "T8 / T3",
    },
    20: {
        "leitura": "Zero conectando terminais altos.",
        "entrada": "T0 e T5 com 1 vizinho",
        "cobertura": "T2 / T4",
    },
    21: {
        "leitura": "Espelhos em continuidade.",
        "entrada": "T2 e T3 com 1 vizinho",
        "cobertura": "12, 21, 13, 31, 23, 32",
    },
    22: {
        "leitura": "Estratégia não definida.",
        "entrada": None,
        "cobertura": None,
    },
    23: {
        "leitura": "Zero conectado ao terminal 5.",
        "entrada": "T0 e T5 com 1 vizinho",
        "cobertura": "12, 21, 13, 31, 23, 32",
    },
    24: {
        "leitura": "CAVALO 47.",
        "entrada": "T4 e T1 com 1 vizinho",
        "cobertura": "T2 / T5",
    },
    25: {
        "leitura": "Terminal 5 isolado com vizinhança.",
        "entrada": "T5 e T0 com 1 vizinho",
        "cobertura": "T1 / T4",
    },
    26: {
        "leitura": "Terminal 6.",
        "entrada": "T6 e T3 com 1 vizinho",
        "cobertura": "T2 / T9",
    },
    27: {
        "leitura": "Estratégia não definida.",
        "entrada": None,
        "cobertura": None,
    },
    28: {
        "leitura": "Sequência técnica ativa.",
        "entrada": "28 e 13 com 5 vizinhos",
        "cobertura": "T1 / T6",
    },
    29: {
        "leitura": "Terminal 9 conexão com o zero.",
        "entrada": "T9 e T0 com 1 vizinho",
        "cobertura": "T6 / T1",
    },
    30: {
        "leitura": "Terminal 0 fluxo lateral.",
        "entrada": "T5 e T7 com 1 vizinho",
        "cobertura": "T4 / T9",
    },
    31: {
        "leitura": "Continuidade de espelhos.",
        "entrada": "T1 e T3 com 1 vizinho",
        "cobertura": "T2 / T4",
    },
    32: {
        "leitura": "Continuidade de espelhos.",
        "entrada": "T1 e T3 com 1 vizinho",
        "cobertura": "T2 / T5",
    },
    33: {
        "leitura": "Gêmeos ativos.",
        "entrada": "11 / 22 / 33 / 0 com 3 vizinhos",
        "cobertura": "17 / 27",
    },
    34: {
        "leitura": "Terminal 4.",
        "entrada": "T4 e T2 com 1 vizinho",
        "cobertura": "T1 / T6",
    },
    35: {
        "leitura": "Terminal 5.",
        "entrada": "T6 e T3 com 1 vizinho",
        "cobertura": "T2 / T9",
    },
    36: {
        "leitura": "Terminal 6.",
        "entrada": "T6 e T8 com 1 vizinho",
        "cobertura": "T5 / T9",
    },
}
