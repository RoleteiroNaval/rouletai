import sys
import os
import time

# Adiciona o diretorio atual ao path
sys.path.append(os.getcwd())

from config.settings import Settings
from utils.history_buffer import HistoryBuffer
from utils.rule_engine import engine
from analytics.context_filter import ContextFilter

def verify_integrity():
    print("--- Testando Integridade Windows 10 ---")
    hb = HistoryBuffer(max_size=60)
    
    # 1. Teste de timestamp duplicado
    ts = time.time()
    print(f"Adicionando Numero 10 com TS: {ts}")
    hb.add(10, ts)
    print(f"Adicionando Numero 20 com o MESMO TS: {ts}")
    success = hb.add(20, ts)
    
    if len(hb) == 1 and not success:
        print("OK: Segundo numero ignorado por timestamp duplicado.")
    else:
        print(f"ERRO: Integridade falhou. Tamanho buffer: {len(hb)}")

    # 2. Teste de Delta Invalido (< 15s)
    print(f"Adicionando Numero 30 com TS + 5s (delta 5s)")
    success = hb.add(30, ts + 5.0)
    if len(hb) == 1 and not success:
        print("OK: Numero ignorado por delta curto (< 15s).")
    else:
        print(f"ERRO: Delta invalido nao detectado. Tamanho: {len(hb)}")

    # 3. Teste de Delta Valido (> 15s)
    print(f"Adicionando Numero 30 com TS + 20s (delta 20s)")
    success = hb.add(30, ts + 20.0)
    if len(hb) == 2 and success:
        print("OK: Numero aceito com delta valido.")
    else:
        print(f"ERRO: Delta valido rejeitado.")

def verify_stats_filter():
    print("\n--- Testando Filtro Estatistico (Janela 60) ---")
    cf = ContextFilter()
    
    # 1. Teste de aquecimento (< 60 giros)
    history = [1, 2, 3, 4, 5]
    block, info = cf.should_block_entry(history, 10)
    if block and info['type'] == 'warming_up':
        print(f"OK: Bloqueado por aquecimento ({len(history)}/60)")
    else:
        print("ERRO: Nao bloqueou por aquecimento.")

    # 2. Teste de Turbulencia Extrema (Simulada)
    # Criamos um historico de 60 giros com forte tendencia em Cores, Duzias e Colunas
    # Todos os numeros como '1' (Vermelho, Duzia 1, Coluna 1, Impar, Baixo)
    history_extreme = [1] * 60
    block, info = cf.should_block_entry(history_extreme, 1)
    if block and info['type'] == 'extreme_turbulence':
        print(f"OK: Turbulencia Detectada! Categorias: {info.get('categories')}")
    else:
        print(f"ERRO: Turbulencia nao detectada conforme o esperado. Tipo: {info.get('type')}")

    # 3. Teste de Ruido Aleatorio (Numero base sem desvio > 2 sigma)
    # Vamos criar um historico equilibrado
    history_balanced = list(range(1, 37)) + list(range(1, 25)) # 60 giros
    # O numero 10 apareceu 2 vezes em 60. Mu = 60/37 = 1.62. Sigma ~= 1.25. 
    # Frequencia 2 esta bem abaixo de Mu + 2*Sigma (1.62 + 2.5 = 4.12)
    block, info = cf.should_block_entry(history_balanced, 10)
    if block and info['type'] == 'noise':
        print(f"OK: Numero 10 bloqueado como Ruido Aleatorio (z={info['stats'].get('Num_10', 0):.2f})")
    else:
        print(f"ERRO: Numero equilibrado nao foi tratado como ruido. Bloqueio: {block}, Tipo: {info.get('type')}")

if __name__ == "__main__":
    verify_integrity()
    verify_stats_filter()
