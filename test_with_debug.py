"""
Test avec debug complet de run_attack
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Monkey patch pour ajouter du debug
import backend.cryptotoolbox.attack.attack_runner as runner_module

original_run_dictionary_attack = runner_module.run_dictionary_attack

def debug_run_dictionary_attack(algorithm, encrypted, key_data, dictionary, start_time, max_seconds, limit, attempts):
    print(f"\n[DEBUG run_dictionary_attack called]")
    print(f"  algorithm: {algorithm}")
    print(f"  encrypted: {encrypted}")
    print(f"  key_data: {key_data} (type: {type(key_data)})")
    print(f"  dictionary length: {len(dictionary)}")
    print(f"  dictionary first 3: {dictionary[:3] if len(dictionary) >= 3 else dictionary}")
    
    result = original_run_dictionary_attack(algorithm, encrypted, key_data, dictionary, start_time, max_seconds, limit, attempts)
    
    print(f"[DEBUG run_dictionary_attack returned]")
    print(f"  attempts: {result[0]}")
    print(f"  matches: {len(result[1])} matches")
    if result[1]:
        print(f"  first match: {result[1][0]}")
    
    return result

runner_module.run_dictionary_attack = debug_run_dictionary_attack

# Maintenant tester
from backend.cryptotoolbox.attack.attack_runner import run_attack

print("="*80)
print(" TEST AVEC DEBUG")
print("="*80)

dictionary = ['000', '001', '002', '010', '011', '012']

instruction = {
    "target_username": "cas1_012",
    "mode": "dictionary",
    "dictionary": dictionary,
    "limit": 0,
    "max_seconds": 60
}

print(f"\nInstruction:")
print(f"  {instruction}")

result = run_attack(instruction)

print(f"\n[RESULTAT FINAL]")
print(f"  matches_count: {result.get('matches_count')}")
print(f"  matches: {result.get('matches')}")
print(f"  attempts: {result.get('attempts')}")
