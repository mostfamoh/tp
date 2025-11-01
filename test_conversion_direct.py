"""
Test direct de la conversion chiffres → lettres lors de l'enregistrement
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from crypto_lab.models import CustomUser
from backend.cryptotoolbox.cyphers.caesar import caesar_encrypt

print("="*60)
print("TEST DE LA CONVERSION CHIFFRES → LETTRES")
print("="*60)

# Supprimer l'ancien utilisateur s'il existe
try:
    CustomUser.objects.filter(username='test_conversion').delete()
    print("✓ Ancien utilisateur supprimé")
except:
    pass

# Test 1: Simuler ce que fait le code modifié
print("\n📝 Test 1: Simulation de l'enregistrement")
password = "012"
print(f"   Password original: {password}")

# Convertir les chiffres en lettres (comme le fait le nouveau code)
password_to_encrypt = password
if any(c.isdigit() for c in password):
    password_to_encrypt = ''.join([
        chr(ord('A') + int(c)) if c.isdigit() else c 
        for c in password
    ])

print(f"   Password converti: {password_to_encrypt}")

# Chiffrer
shift = 3
encrypted = caesar_encrypt(password_to_encrypt, shift)
print(f"   Password chiffré: {encrypted}")
print(f"   Attendu: DEF (A+3=D, B+3=E, C+3=F)")

if encrypted == "DEF":
    print(f"   ✅ CORRECT!")
else:
    print(f"   ❌ ERREUR! Attendu DEF, obtenu {encrypted}")

# Test 2: Créer un vrai utilisateur dans la BDD
print("\n📝 Test 2: Création d'utilisateur dans la BDD")

user = CustomUser.objects.create(
    username='test_conversion',
    password_encypted=encrypted,
    algorithm='cesar',
    key_data={'shift': shift}
)

print(f"   ✅ Utilisateur créé:")
print(f"      Username: {user.username}")
print(f"      Password encrypted: {user.password_encypted}")
print(f"      Algorithm: {user.algorithm}")
print(f"      Key data: {user.key_data}")

# Test 3: Vérifier que l'attaque fonctionne
print("\n📝 Test 3: Test de l'attaque")

from backend.cryptotoolbox.attack.attack_runner import run_attack

dict_path = os.path.join(os.path.dirname(__file__), 'backend', 'dictionaries', 'dict_012.txt')
if os.path.exists(dict_path):
    with open(dict_path, 'r', encoding='utf-8') as f:
        dictionary = [line.strip() for line in f if line.strip()]
    
    print(f"   Dictionnaire: {len(dictionary)} entrées")
    
    payload = {
        "target_username": "test_conversion",
        "mode": "dictionary",
        "dictionary": dictionary,
        "max_seconds": 60,
        "limit": 0
    }
    
    result = run_attack(payload)
    
    print(f"\n   Résultat:")
    print(f"   - Tentatives: {result.get('attempts', 0)}")
    print(f"   - Temps: {result.get('time_sec', 0):.4f}s")
    print(f"   - Matches: {result.get('matches_count', 0)}")
    
    if result.get('matches'):
        found_password = result['matches'][0]['candidate_key'].get('password_candidate', 'N/A')
        print(f"   - ✅ Password trouvé: {found_password}")
        
        if found_password == "012":
            print(f"   - ✅ PARFAIT! Le mot de passe '012' a été trouvé!")
        else:
            print(f"   - ⚠️  Trouvé '{found_password}' au lieu de '012'")
    else:
        print(f"   - ❌ Aucun mot de passe trouvé")
else:
    print(f"   ❌ Dictionnaire introuvable")

print("\n" + "="*60)
print("MAINTENANT, TESTEZ L'ENREGISTREMENT VIA LE FRONTEND!")
print("="*60)
print("""
Le code a été modifié dans views.py pour:
1. Détecter si le mot de passe contient des chiffres
2. Convertir les chiffres en lettres (0→A, 1→B, 2→C, etc.)
3. Chiffrer la version convertie

Exemple:
  Password: "012"
  Converti: "ABC"  
  Chiffré (shift 3): "DEF"
  
Donc maintenant, quand vous créez un utilisateur avec un mot de passe
numérique via le frontend, il sera correctement chiffré et l'attaque
pourra le trouver!
""")
