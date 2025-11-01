"""
Test de l'enregistrement avec mot de passe numérique
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("TEST D'ENREGISTREMENT AVEC MOT DE PASSE NUMÉRIQUE")
print("="*60)

# Test 1: Créer un utilisateur avec mot de passe numérique simple
print("\n📝 Test 1: Utilisateur avec mot de passe '012'")

# Supprimer l'utilisateur s'il existe déjà
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from crypto_lab.models import CustomUser

try:
    CustomUser.objects.filter(username='test_numeric').delete()
    print("   Ancien utilisateur 'test_numeric' supprimé")
except:
    pass

# Créer le nouvel utilisateur via l'API
payload = {
    "username": "test_numeric",
    "password": "012",
    "algorithm": "cesar",
    "key_param": "3"
}

print(f"\n🚀 Envoi de la requête...")
print(f"   Username: {payload['username']}")
print(f"   Password: {payload['password']}")
print(f"   Algorithm: {payload['algorithm']}")
print(f"   Shift: {payload['key_param']}")

try:
    response = requests.post(f"{BASE_URL}/regester/", json=payload)
    print(f"\n📊 Réponse:")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Message: {data.get('message', 'N/A')}")
        print(f"   🔒 Encrypted: {data.get('encrypted_password', 'N/A')}")
        
        # Vérifier dans la base de données
        user = CustomUser.objects.get(username='test_numeric')
        print(f"\n✅ Vérification dans la base de données:")
        print(f"   Username: {user.username}")
        print(f"   Password encrypted: {user.password_encypted}")
        print(f"   Algorithm: {user.algorithm}")
        print(f"   Key data: {user.key_data}")
        
        # Vérifier que le chiffrement est correct
        expected = "DEF"  # 012 -> ABC -> DEF (shift 3)
        if user.password_encypted == expected:
            print(f"\n   ✅ SUCCÈS! Le mot de passe est correctement chiffré!")
            print(f"      012 → ABC → DEF (shift 3)")
        else:
            print(f"\n   ❌ ERREUR! Chiffrement incorrect")
            print(f"      Attendu: {expected}")
            print(f"      Obtenu: {user.password_encypted}")
    else:
        print(f"   ❌ Erreur: {response.text}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 2: Tester l'attaque
print("\n" + "="*60)
print("TEST D'ATTAQUE SUR L'UTILISATEUR")
print("="*60)

from backend.cryptotoolbox.attack.attack_runner import run_attack

# Charger le dictionnaire
dict_path = os.path.join(os.path.dirname(__file__), 'backend', 'dictionaries', 'dict_012.txt')
if os.path.exists(dict_path):
    with open(dict_path, 'r', encoding='utf-8') as f:
        dictionary = [line.strip() for line in f if line.strip()]
    
    print(f"\n🔍 Attaque avec dict_012.txt ({len(dictionary)} entrées)")
    
    payload = {
        "target_username": "test_numeric",
        "mode": "dictionary",
        "dictionary": dictionary,
        "max_seconds": 60,
        "limit": 0
    }
    
    result = run_attack(payload)
    
    print(f"\n📊 Résultat:")
    print(f"   Tentatives: {result.get('attempts', 0)}")
    print(f"   Temps: {result.get('time_sec', 0):.4f}s")
    print(f"   Matches: {result.get('matches_count', 0)}")
    
    if result.get('matches'):
        print(f"\n   ✅ MOT DE PASSE TROUVÉ!")
        for match in result['matches']:
            found_password = match['candidate_key'].get('password_candidate', 'N/A')
            print(f"      Password: {found_password}")
            if found_password == "012":
                print(f"      ✅ PARFAIT! Le mot de passe '012' a été trouvé!")
            else:
                print(f"      ⚠️  Trouvé '{found_password}' au lieu de '012'")
    else:
        print(f"\n   ❌ Aucun mot de passe trouvé")

print("\n" + "="*60)
print("FIN DES TESTS")
print("="*60)
