"""
Test direct de run_attack() pour voir l'erreur
"""
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from backend.cryptotoolbox.attack.attack_runner import run_attack

# Test avec dictionnaire par défaut
payload = {
    "target_username": "bellia",
    "mode": "dictionary",
    "dictionary": ["122", "012", "000", "111", "222"],
    "max_seconds": 60,
    "limit": 0
}

print("Test de run_attack()...")
try:
    result = run_attack(payload)
    print(f"✅ Succès!")
    print(f"Result: {result}")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
