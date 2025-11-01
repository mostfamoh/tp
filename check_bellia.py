"""
Vérifier l'utilisateur bellia créé via le frontend
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from crypto_lab.models import CustomUser
from backend.cryptotoolbox.attack.attack_runner import run_attack

print("="*60)
print("VÉRIFICATION DE L'UTILISATEUR BELLIA")
print("="*60)

try:
    bellia = CustomUser.objects.get(username='bellia')
    print(f"\n✅ Utilisateur trouvé: bellia")
    print(f"   Password encrypted: '{bellia.password_encypted}'")
    print(f"   Longueur: {len(bellia.password_encypted)}")
    print(f"   Algorithm: {bellia.algorithm}")
    print(f"   Key data: {bellia.key_data}")
    
    # Vérifier si le password est vide
    if not bellia.password_encypted or bellia.password_encypted.strip() == '':
        print(f"\n❌ PROBLÈME: Le password_encypted est VIDE!")
        print(f"   → Le frontend n'a pas utilisé la nouvelle version du code")
        print(f"   → Ou le serveur n'a pas été redémarré après la modification")
    else:
        print(f"\n✅ Le password_encypted n'est pas vide")
        
        # Test avec différents dictionnaires
        print(f"\n" + "="*60)
        print(f"TEST DES ATTAQUES")
        print(f"="*60)
        
        # Test 1: dict_digits3.txt (000-999)
        dict_path = os.path.join(os.path.dirname(__file__), 'backend', 'dictionaries', 'dict_digits3.txt')
        if os.path.exists(dict_path):
            with open(dict_path, 'r', encoding='utf-8') as f:
                dictionary = [line.strip() for line in f if line.strip()]
            
            print(f"\n🔍 Test 1: dict_digits3.txt ({len(dictionary)} entrées)")
            print(f"   Contient '123456'? {'123456' in dictionary}")
            
            if '123456' not in dictionary:
                print(f"   → dict_digits3 va de 000 à 999, pas de 123456!")
        
        # Test 2: dict_digits6.txt (000000-999999)
        dict_path = os.path.join(os.path.dirname(__file__), 'backend', 'dictionaries', 'dict_digits6.txt')
        if os.path.exists(dict_path):
            print(f"\n🔍 Test 2: dict_digits6.txt")
            print(f"   Ce dictionnaire contient 1,000,000 d'entrées (000000 à 999999)")
            print(f"   Il devrait contenir '123456'")
            
            # Charger et tester
            with open(dict_path, 'r', encoding='utf-8') as f:
                dictionary = [line.strip() for line in f if line.strip()]
            
            print(f"   Taille du dictionnaire: {len(dictionary):,} entrées")
            
            if '123456' in dictionary:
                print(f"   ✅ '123456' est dans le dictionnaire à la position {dictionary.index('123456'):,}")
                
                # Lancer l'attaque
                print(f"\n   🚀 Lancement de l'attaque...")
                
                payload = {
                    "target_username": "bellia",
                    "mode": "dictionary",
                    "dictionary": dictionary,
                    "max_seconds": 120,
                    "limit": 0
                }
                
                import time
                start = time.time()
                result = run_attack(payload)
                elapsed = time.time() - start
                
                print(f"\n   📊 Résultat:")
                print(f"   - Temps: {elapsed:.2f} secondes")
                print(f"   - Tentatives: {result.get('attempts', 0):,}")
                print(f"   - Matches: {result.get('matches_count', 0)}")
                
                if result.get('matches'):
                    print(f"\n   ✅ MOT DE PASSE TROUVÉ!")
                    for match in result['matches']:
                        print(f"      → Password: {match['candidate_key'].get('password_candidate', 'N/A')}")
                else:
                    print(f"\n   ❌ Aucun mot de passe trouvé")
                    print(f"\n   🔍 DEBUG: Vérifions le chiffrement manuel...")
                    
                    from backend.cryptotoolbox.cyphers.caesar import caesar_encrypt
                    import json
                    
                    key_data = bellia.key_data
                    if isinstance(key_data, str):
                        key_data = json.loads(key_data)
                    if isinstance(key_data, str):
                        key_data = json.loads(key_data)
                    
                    shift = key_data.get('shift', 0)
                    print(f"      Shift: {shift}")
                    
                    # Test avec 123456
                    password_test = "123456"
                    # Convertir en lettres
                    password_letters = ''.join([chr(ord('A') + int(c)) for c in password_test])
                    print(f"      Test: {password_test} → {password_letters}")
                    
                    encrypted = caesar_encrypt(password_letters, shift)
                    print(f"      Chiffré: {encrypted}")
                    print(f"      Dans DB: {bellia.password_encypted}")
                    print(f"      Match? {encrypted == bellia.password_encypted}")
            else:
                print(f"   ❌ '123456' n'est PAS dans le dictionnaire!")
        else:
            print(f"\n❌ dict_digits6.txt introuvable!")
            print(f"   Exécutez: python generate_dictionaries.py")
        
except CustomUser.DoesNotExist:
    print(f"\n❌ Utilisateur 'bellia' n'existe pas!")
    print(f"\n📝 Utilisateurs existants:")
    for user in CustomUser.objects.all():
        print(f"   - {user.username} ({user.algorithm})")

print(f"\n" + "="*60)
