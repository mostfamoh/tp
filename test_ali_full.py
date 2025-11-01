"""
Test de l'attaque sur ali avec le bon dictionnaire
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from backend.cryptotoolbox.attack.attack_runner import run_attack

print("="*60)
print("TEST ATTAQUE SUR ALI avec dict_digits6.txt")
print("="*60)

# Charger le dictionnaire digits6
dict_path = os.path.join(os.path.dirname(__file__), 'backend', 'dictionaries', 'dict_digits6.txt')

if os.path.exists(dict_path):
    print(f"\n✅ Dictionnaire trouvé: {dict_path}")
    print(f"⚠️  ATTENTION: Ce dictionnaire contient 1,000,000 d'entrées!")
    print(f"   L'attaque peut prendre 10-60 secondes...")
    
    # Charger tout le dictionnaire
    with open(dict_path, 'r', encoding='utf-8') as f:
        dictionary = [line.strip() for line in f if line.strip()]
    
    print(f"\n📊 Dictionnaire chargé: {len(dictionary):,} entrées")
    
    # Vérifier si 123456 est dans le dictionnaire
    if '123456' in dictionary:
        position = dictionary.index('123456')
        print(f"✅ '123456' est dans le dictionnaire à la position {position:,}")
    else:
        print(f"❌ '123456' n'est PAS dans le dictionnaire!")
    
    print(f"\n🚀 Lancement de l'attaque...")
    
    payload = {
        "target_username": "ali",
        "mode": "dictionary",
        "dictionary": dictionary,
        "max_seconds": 120,  # 2 minutes max
        "limit": 0
    }
    
    import time
    start = time.time()
    result = run_attack(payload)
    elapsed = time.time() - start
    
    print(f"\n" + "="*60)
    print("RÉSULTAT DE L'ATTAQUE")
    print("="*60)
    print(f"⏱️  Temps: {elapsed:.2f} secondes ({elapsed/60:.2f} minutes)")
    print(f"🔢 Tentatives: {result.get('attempts', 0):,}")
    print(f"🎯 Matches: {result.get('matches_count', 0)}")
    
    if result.get('matches'):
        print(f"\n✅ MOT DE PASSE TROUVÉ!")
        for match in result['matches']:
            print(f"   → Password: {match['candidate_key'].get('password_candidate', 'N/A')}")
            print(f"   → Plaintext: {match['candidate_plaintext']}")
            print(f"   → Confidence: {match['confidence']}")
    else:
        print(f"\n❌ Aucun mot de passe trouvé")
        
    print(f"\n" + "="*60)
else:
    print(f"❌ Dictionnaire introuvable: {dict_path}")
    print(f"\n💡 Solution: Exécutez d'abord:")
    print(f"   python generate_dictionaries.py")
