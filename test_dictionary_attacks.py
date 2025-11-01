"""
Test rapide des attaques avec les dictionnaires
"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from backend.cryptotoolbox.attack.attack_runner import run_attack

print("="*80)
print(" TEST DES ATTAQUES AVEC DICTIONNAIRES")
print("="*80)

# Charger le dictionnaire
with open('backend/dic.txt', 'r') as f:
    dictionary = [line.strip() for line in f if line.strip()]

print(f"\n📖 Dictionnaire chargé: {len(dictionary)} mots")
print(f"   Premiers mots: {dictionary[:5]}")
print(f"   Derniers mots: {dictionary[-3:]}")

# Test sur cas1_012
print("\n" + "-"*80)
print("TEST 1: Attaque sur cas1_012 (mot de passe: 012)")
print("-"*80)

instruction1 = {
    "target_username": "cas1_012",
    "mode": "dictionary",
    "dictionary": dictionary,
    "limit": 0,
    "max_seconds": 60
}

result1 = run_attack(instruction1)

print(f"\nRésultat complet:")
print(f"  {result1}")

print(f"\nRésultat analysé:")
print(f"  - Status: {'✅ REUSSI' if result1.get('matches_count', 0) > 0 else '❌ ECHOUE'}")
print(f"  - Tentatives: {result1.get('attempts', 0)}")
print(f"  - Temps: {result1.get('time_sec', 0):.6f} secondes")
print(f"  - Matches count: {result1.get('matches_count', 0)}")
if result1.get('matches_count', 0) > 0:
    print(f"  - Correspondances trouvées: {result1.get('matches_count', 0)}")
    if result1.get('matches'):
        print(f"  - Premier match: {result1['matches'][0]}")
else:
    print(f"  - Erreurs: {result1.get('errors', [])}")

# Test sur cas2_123456
print("\n" + "-"*80)
print("TEST 2: Attaque sur cas2_123456 (mot de passe: 123456)")
print("-"*80)

# Charger dictionnaire numérique
with open('backend/dic_numeric.txt', 'r') as f:
    dict_numeric = [line.strip() for line in f if line.strip()]

print(f"📖 Dictionnaire numérique: {len(dict_numeric)} mots")

instruction2 = {
    "target_username": "cas2_123456",
    "mode": "dictionary",
    "dictionary": dict_numeric,
    "limit": 0,
    "max_seconds": 60
}

result2 = run_attack(instruction2)

print(f"\nRésultat:")
print(f"  - Status: {'✅ REUSSI' if result2.get('matches_count', 0) > 0 else '❌ ECHOUE'}")
print(f"  - Tentatives: {result2.get('attempts', 0)}")
print(f"  - Temps: {result2.get('time_sec', 0):.6f} secondes")
if result2.get('matches_count', 0) > 0:
    print(f"  - Correspondances trouvées: {result2.get('matches_count', 0)}")
    if result2.get('matches'):
        print(f"  - Premier match: {result2['matches'][0]}")

print("\n" + "="*80)
print(" TESTS TERMINES")
print("="*80)
