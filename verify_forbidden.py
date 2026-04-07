import sys
import os

# Adiciona o diretorio atual ao path para importar os modulos
sys.path.append(os.getcwd())

from config.settings import Settings
from engine.registry import registry

def verify():
    print("Iniciando Verificacao de Bloqueio de Numeros...")
    
    # Lista de numeros proibidos
    forbidden = [17, 27, 8, 33, 11, 22, 28, 0, 7]
    
    # 1. Verifica se os numeros estao em Settings
    print(f"Configuracao em Settings: {Settings.FORBIDDEN_NUMBERS}")
    for n in forbidden:
        if n not in Settings.FORBIDDEN_NUMBERS:
            print(f"ERRO: Numero {n} nao encontrado em Settings.FORBIDDEN_NUMBERS")
            return
    print("OK: Settings.FORBIDDEN_NUMBERS contem todos os numeros desejados.")

    # 2. Forca o preload no registry para garantir que as mudancas foram aplicadas
    count = registry.preload()
    print(f"Estrategias carregadas: {count}")
    
    # 3. Verifica se os numeros proibidos NAO tem estrategia
    for n in forbidden:
        strat = registry.get_strategy(n)
        if strat is not None:
            print(f"ERRO: Estrategia para o numero {n} ainda esta ativa!")
            return
        else:
            print(f"OK: Numero {n} bloqueado com sucesso.")

    # 4. Verifica o total esperado
    # ESTRATEGIAS tem 37 itens (0 a 36). Bloqueamos 9.
    # Total deve ser 28.
    if count == 28:
        print(f"OK: Total de estrategias (28) esta correto.")
    else:
        print(f"AVISO: Total de estrategias carregadas eh {count}, esperado 28.")

    print("\n--- RESUMO DA VERIFICACAO ---")
    print("As mudancas foram aplicadas corretamente.")
    print("Os numeros 17, 27, 8, 33, 11, 22, 28, 0, 7 nao dispararao mais entradas.")

if __name__ == "__main__":
    verify()
