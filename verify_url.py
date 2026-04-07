from config.settings import Settings
import logging

# Configura um logger simples para o teste
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_config')

def test_url():
    print("\n" + "="*60)
    print("VALIDAÇÃO DE CONFIGURAÇÃO DE URL")
    print("="*60)
    print(f"URL carregada: {Settings.GAME_URL}")
    
    expected_url = "https://geralbet.bet.br/games/playtech/roleta-brasileira"
    
    if Settings.GAME_URL == expected_url:
        print("✅ SUCESSO: A URL é exatamente a oficial!")
    else:
        print(f"❌ ERRO: A URL está incorreta!")
        print(f"Esperado: {expected_url}")
        print(f"Atual:    {Settings.GAME_URL}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    test_url()
