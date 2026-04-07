"""
Script para visualizar estatísticas do banco de dados
Uso: python view_stats.py
"""

from utils.database import Database
from datetime import datetime

def format_timestamp(ts_str):
    """Formata timestamp para leitura humana"""
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    except:
        return ts_str

def main():
    db = Database()
    
    print("\n" + "="*60)
    print("  📊 ESTATÍSTICAS DO BOT - BANCO DE DADOS")
    print("="*60 + "\n")
    
    stats = db.get_statistics()
    
    print(f"📈 RESUMO GERAL:")
    print(f"   Total de números detectados: {stats['total_numbers']}")
    print(f"   Total de sessões: {stats['total_sessions']}")
    print(f"   Total de erros: {stats['total_errors']}")
    
    print(f"\n🎲 NÚMEROS MAIS FREQUENTES:")
    if stats['most_common']:
        for idx, (number, count) in enumerate(stats['most_common'], 1):
            percentage = (count / stats['total_numbers'] * 100) if stats['total_numbers'] > 0 else 0
            print(f"   {idx}. Número {number:2d} → {count:3d} vezes ({percentage:.1f}%)")
    else:
        print("   (Nenhum número registrado ainda)")
    
    print(f"\n📋 ÚLTIMOS 10 NÚMEROS DETECTADOS:")
    last_numbers = db.get_last_numbers(10)
    if last_numbers:
        for number, detected_at, telegram_sent in last_numbers:
            status = "✅" if telegram_sent else "❌"
            timestamp = format_timestamp(detected_at)
            print(f"   {status} {number:2d} | {timestamp}")
    else:
        print("   (Nenhum número registrado ainda)")
    
    print("\n" + "="*60)
    print("💡 Dica: Para consultas SQL personalizadas, use:")
    print("   sqlite3 data/roulette.db")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
