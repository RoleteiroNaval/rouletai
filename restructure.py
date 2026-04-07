import os
import shutil

base_path = r'c:\Users\visio\Documents\telegram-bot-playwright2'
os.chdir(base_path)

dirs = ['core', 'services', 'storage', 'analytics', 'config']

# Create directories and __init__.py files
for d in dirs:
    if not os.path.exists(d):
        os.makedirs(d)
        print(f"Created directory: {d}")
    init_file = os.path.join(d, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            pass
        print(f"Created {init_file}")

# File moves mapping
moves = [
    ('ws_analyzer.py', 'core/ws_analyzer.py'),
    ('playtech_ws.py', 'core/playtech_ws.py'),
    ('playtech_ws_analyzer.py', 'core/playtech_ws_analyzer.py'),
    ('scraper/monitor.py', 'core/monitor.py'),
    ('strategy/engine.py', 'core/engine.py'),
    ('telegram_bot/bot.py', 'services/bot.py'),
    ('telegram_bot/forwarder.py', 'services/forwarder.py'),
    ('utils/reporting.py', 'services/reporting.py'),
    ('utils/daily_report.py', 'services/daily_report.py'),
    ('utils/database.py', 'storage/database.py'),
    ('utils/backup.py', 'storage/backup.py'),
    ('utils/metrics.py', 'analytics/metrics.py'),
    ('utils/strategy_analytics.py', 'analytics/strategy_analytics.py'),
    ('utils/market_analysis.py', 'analytics/market_analysis.py'),
    ('.env', 'config/.env')
]

for src, dst in moves:
    src_path = os.path.join(base_path, src)
    dst_path = os.path.join(base_path, dst)
    if os.path.exists(src_path):
        try:
            shutil.move(src_path, dst_path)
            print(f"Moved {src} to {dst}")
        except Exception as e:
            print(f"Error moving {src}: {e}")
    else:
        print(f"Source file not found: {src}")

print("Restructuring script completed.")
