"""
Test direct de run_dictionary_attack
"""
import os
import sys
import django
import json
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crypto_lab.models import CustomUser
from backend.cryptotoolbox.attack.dictionaryattack import run_dictionary_attack

# Récupérer l'utilisateur
user = CustomUser.objects.filter(username='cas1_012').first()

if not user:
    print("❌ Utilisateur non trouvé")
    sys.exit(1)

print("="*80)
print(" TEST DIRECT DE run_dictionary_attack")
print("="*80)

encrypted = user.password_encypted
algorithm = user.algorithm.lower().replace('cesar', 'caesar')
key_data = json.loads(user.key_data) if isinstance(user.key_data, str) else user.key_data

print(f"\nParametres:")
print(f"  - Algorithm: {algorithm}")
print(f"  - Encrypted: {encrypted}")
print(f"  - Key data: {key_data}")

# Dictionnaire
dictionary = ['000', '001', '002', '010', '011', '012']
print(f"  - Dictionary: {dictionary}")

# Appeler la fonction
start_time = time.perf_counter()
attempts, matches, limit_reached, timeout_reached, err = run_dictionary_attack(
    algorithm=algorithm,
    encrypted=encrypted,
    key_data=key_data,
    dictionary=dictionary,
    start_time=start_time,
    max_seconds=60,
    limit=0,
    attempts=0
)

print(f"\nResultats:")
print(f"  - Attempts: {attempts}")
print(f"  - Matches found: {len(matches)}")
print(f"  - Limit reached: {limit_reached}")
print(f"  - Timeout reached: {timeout_reached}")
print(f"  - Error: {err}")

if matches:
    print(f"\n✅ SUCCES! Matches trouvés:")
    for i, match in enumerate(matches, 1):
        print(f"\n  Match {i}:")
        print(f"    - Plaintext: {match.get('candidate_plaintext')}")
        print(f"    - Key: {match.get('candidate_key')}")
        print(f"    - Confidence: {match.get('confidence')}")
        print(f"    - Notes: {match.get('notes')}")
else:
    print(f"\n❌ Aucun match trouvé")
    print(f"\n  Debugging...")
    print(f"  Testons manuellement:")
    
    from backend.cryptotoolbox.attack.utils import clean_text
    from string import ascii_uppercase
    
    shift = key_data.get('shift')
    for word in dictionary:
        txt = clean_text(word)
        cipher = ''.join(ascii_uppercase[(ord(ch) - 65 + shift) % 26] for ch in txt)
        match = clean_text(cipher) == clean_text(encrypted)
        print(f"    {word} -> {txt} -> {cipher} vs {encrypted}: {match}")
