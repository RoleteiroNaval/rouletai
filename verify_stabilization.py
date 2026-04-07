import os
import sys
import re
from pathlib import Path
from config.settings import Settings

def check_file_content(path, patterns, name):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            for pattern in patterns:
                if not re.search(pattern, content):
                    print(f"❌ {name}: Pattern not found: {pattern}")
                    return False
        print(f"✅ {name}: Verified")
        return True
    except Exception as e:
        print(f"❌ {name}: Error reading file: {e}")
        return False

def check_no_chromium(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "chromium" in content.lower() and "playwright install" not in content.lower(): # Allowed if commented or in install instructions that we just changed? Actually we changed them all.
                 # Actually we changed all install commands to firefox, so chromium shouldn't be there except maybe inside comments or unrelated things.
                 pass
            
            # Let's be strict
            if "playwright.chromium.launch" in content:
                print(f"❌ {path}: Found 'playwright.chromium.launch'")
                return False
    except:
        pass
    return True

def main():
    print("🔎 STARTING FINAL VERIFICATION CHECKLIST\n")
    all_passed = True

    # 1. Check Monitor Configuration
    print("1️⃣ Checking Browser Configuration (Chromium)...")
    monitor_path = "core/monitor.py"
    patterns = [
        r"playwright\.chromium\.launch",
        r"headless=False",
        r"--start-maximized",
        r"context\.new_page\(\)" 
    ]
    if not check_file_content(monitor_path, patterns, "core/monitor.py"):
        all_passed = False

    # 2. Check URL
    print("\n2️⃣ Checking Game URL...")
    expected_url = "https://geralbet.bet.br/games/playtech/roleta-brasileira"
    if Settings.GAME_URL == expected_url:
        print(f"✅ URL Correct: {Settings.GAME_URL}")
    else:
        print(f"❌ URL Incorrect: Found {Settings.GAME_URL}")
        all_passed = False

    # 3. Check Telegram Token
    print("\n3️⃣ Checking Telegram Configuration...")
    if Settings.TELEGRAM_TOKEN and Settings.TELEGRAM_CHAT_ID:
        print("✅ Telegram Credentials Found")
    else:
        print("❌ Telegram Credentials Missing")
        all_passed = False

    # 4. Check Database
    print("\n4️⃣ Checking Database...")
    if os.path.exists(Settings.DB_PATH):
        print(f"✅ Database found at {Settings.DB_PATH}")
    else:
        print(f"⚠️ Database not found (Will be created on start)")

    # 5. Check dependencies in setup scripts
    print("\n5️⃣ Checking Setup Scripts...")
    if not check_file_content("setup_linux.sh", [r"playwright install chromium"], "setup_linux.sh"):
         all_passed = False
    if not check_file_content("bootstrap_linux.sh", [r"playwright install chromium"], "bootstrap_linux.sh"):
         all_passed = False

    # 6. Check for lingering Firefox calls (Optional check)
    print("\n6️⃣ Checking for Firefox leftovers...")
    files_to_check = ["main.py", "core/monitor.py"]
    for f in files_to_check:
        try:
             with open(f, 'r') as file:
                 if "playwright.firefox.launch" in file.read():
                     print(f"❌ {f}: Found Firefox reference")
                     all_passed = False
        except: pass
    
    if all_passed:
        print("\n🎉 ALL CHECKS PASSED! SYSTEM READY FOR LINUX.")
    else:
        print("\n⚠️ SOME CHECKS FAILED. REVIEW OUTPUT.")

if __name__ == "__main__":
    main()
