from analytics.market_analysis import analyze_market, check_suspicious_repetition
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('market_analysis')
logger.setLevel(logging.INFO)

def run_verification():
    print("=== STARTING MARKET FILTERS VERIFICATION ===")

    # Scenario 1: Clean Market
    # Alternating colors, low suspicious numbers
    print("\n[Scenario 1] Clean Market (Should PASS)")
    history_clean = [1, 2, 3, 4, 1, 2, 3, 4, 10, 11, 12, 13, 20, 2, 22, 3, 30, 4, 32, 5]
    # Suspicious: 2, 4, 13, 20, 30, 2, 4, 13, 20, 30... wait.
    # Count suspicious in history_clean: 
    # [1, 2, 3, 4, 1, 2, 3, 4, 10, 11, 12, 13, 20, 21, 22, 23, 30, 31, 32, 33]
    # Suspicious list: [2, 4, 8, 13, 15, 20, 30]
    # Matches: 2, 4, 2, 4, 13, 20, 30. Total 7.
    # 7/20 = 0.35 (35%). Should PASS (threshold is > 0.40).
    result = analyze_market(history_clean)
    print(f"Result: {result} (Expected: True)")
    
    # Scenario 2: High Suspicious Count
    print("\n[Scenario 2] High Suspicious Count (Should FAIL)")
    # Add more suspicious numbers
    history_suspicious = history_clean[:]
    # Replace some safe numbers with suspicious ones
    history_suspicious[0] = 8
    history_suspicious[2] = 15
    # Now count = 7 + 2 = 9. 9/20 = 0.45.
    result = analyze_market(history_suspicious)
    print(f"Result: {result} (Expected: False)")
    
    # Scenario 3: Color Streak
    print("\n[Scenario 3] Color Streak (Should FAIL)")
    history_streak = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21] # All Red
    # Suspicious count: 0 (all these are safe except maybe... no 2,4,8,13,15,20,30 here? 
    # 1,3,5,7,9,12,14,16,18,19,21. None are in suspicious list.
    # But streak logic: all Red.
    result = analyze_market(history_streak)
    print(f"Result: {result} (Expected: False)")

    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    run_verification()
