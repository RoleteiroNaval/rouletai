import os
import sys
# Adiciona o diretório atual ao path para importar os módulos locais
sys.path.append(os.getcwd())

from utils.database import Database
from utils.reporting import ReportingSystem
from utils.strategy_analytics import analytics
from datetime import datetime, timedelta

def test_reporting():
    print("🚀 Iniciando testes do Sistema de Relatórios...")
    
    # 1. Setup Database temporário para teste
    db_path = 'data/test_roulette.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path)
    reporting = ReportingSystem(db)
    
    # 2. Simular uma sessão
    session_id = db.start_session()
    analytics.db = db
    analytics.set_session(session_id)
    
    print("📝 Registrando resultados simulados (Hoje)...")
    # Hoje: 5 Greens, 1 Red
    analytics.register(1, 'WIN_ENTRY', 'Estratégia A')
    analytics.register(1, 'WIN_PROTECTION', 'Estratégia A')
    analytics.register(2, 'WIN_ENTRY', 'Estratégia B')
    analytics.register(1, 'LOSS', 'Estratégia A')
    analytics.register(2, 'WIN_ENTRY', 'Estratégia B')
    analytics.register(2, 'WIN_PROTECTION', 'Estratégia B')
    
    # 3. Testar Relatório Diário
    print("\n--- RELATÓRIO DIÁRIO (TESTE) ---")
    daily = reporting.get_daily_report()
    print(daily)
    
    # 4. Inserir dados históricos (Passado)
    print("\n📝 Inserindo dados históricos para teste semanal/mensal...")
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 5 dias atrás
    five_days_ago = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO results (event_type, strategy_name, session_id, date) VALUES (?, ?, ?, ?)",
                   ('WIN_ENTRY', 'Estratégia C', session_id, five_days_ago))
    
    # 15 dias atrás
    fifteen_days_ago = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO results (event_type, strategy_name, session_id, date) VALUES (?, ?, ?, ?)",
                   ('LOSS', 'Estratégia D', session_id, fifteen_days_ago))
    
    conn.commit()
    conn.close()
    
    # 5. Testar Relatório Semanal
    print("\n--- RELATÓRIO SEMANAL (TESTE) ---")
    weekly = reporting.get_weekly_report()
    print(weekly)
    
    # 6. Testar Relatório Mensal
    print("\n--- RELATÓRIO MENSAL (TESTE) ---")
    monthly = reporting.get_monthly_report()
    print(monthly)
    
    print("\n✅ Testes concluídos com sucesso!")
    # os.remove(db_path) # Comente se quiser auditar o DB de teste

if __name__ == "__main__":
    test_reporting()
