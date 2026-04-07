import sys
import os
import time

# Adiciona o diretorio atual ao path
sys.path.append(os.getcwd())

from config.settings import Settings
from utils.history_buffer import HistoryBuffer
from analytics.context_filter import ContextFilter

def verify_batch_delivery():
    print("--- Testando Batch Delivery Windows 10 ---")
    hb = HistoryBuffer(max_size=60)
    ts = 1000.0
    
    # Simula 3 números diferentes chegando no MESMO timestamp
    print("Enviando 10, 20, 30 com TS 1000.0")
    hb.add(10, ts)
    hb.add(20, ts)
    hb.add(30, ts)
    
    all_nums = hb.get_all()
    print(f"Números no buffer: {all_nums}")
    
    if len(hb) == 3 and all_nums == [10, 20, 30]:
        print("OK: Batch delivery aceito com delay sintético.")
    else:
        print(f"ERRO: Batch falhou. Tamanho: {len(hb)}")

    # Teste de Repetição Suspeita (Bloqueio)
    print("\nEnviando o número 5 quatro vezes seguidas em batch...")
    hb.clear()
    hb.add(5, ts)
    hb.add(5, ts)
    hb.add(5, ts)
    success = hb.add(5, ts) # 4ª vez!
    
    if len(hb) == 3 and not success:
        print("OK: 4ª repetição idêntica no mesmo batch foi bloqueada.")
    else:
        print(f"ERRO: Bloqueio de repetição falhou. Tamanho: {len(hb)}")

def verify_deescalation():
    print("\n--- Testando Desescalonamento de Turbulência ---")
    cf = ContextFilter()
    
    # Simula 60 giros com desvio moderado (ex: 2.5 sigma)
    # Criamos um cenário onde uma cor está forte, mas não o suficiente para 3.0 sigma em 2 categorias
    history = [1] * 35 + [2] * 25 # Vermelho forte (z ~= 2.5)
    
    block, info = cf.should_block_entry(history, 1)
    
    if not block:
        print("OK: Turbulência de 2.5 sigma NÃO bloqueou a entrada (Continuidade Operacional).")
    else:
        print(f"ERRO: Bloqueio indevido em 2.5 sigma. Tipo: {info.get('type')}")

    # Simula Turbulência EXTREMA (> 3.0 sigma em 2 categorias)
    # Ex: Quase tudo 1 e Vermelho e Dúzia 1 e Coluna 1 e Impar e Baixo
    history_extreme = [1] * 50 + [2] * 10
    block_ext, info_ext = cf.should_block_entry(history_extreme, 1)
    
    if block_ext and info_ext.get('type') == 'extreme_turbulence':
        print(f"OK: Bloqueio apenas em Turbulência Extrema (> 3.0 sigma). Categorias: {info_ext.get('categories')}")
    else:
        print(f"ERRO: Falha ao detectar Turbulência Extrema.")

if __name__ == "__main__":
    verify_batch_delivery()
    verify_deescalation()
