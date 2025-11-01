"""
Test des attaques sur les utilisateurs mostafa et ali
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from crypto_lab.models import CustomUser

print("="*60)
print("VÉRIFICATION DES UTILISATEURS")
print("="*60)

# Vérifier l'utilisateur mostafa
try:
    mostafa = CustomUser.objects.get(username='mostafa')
    print(f"\n✅ Utilisateur: mostafa")
    print(f"   Password encrypted: {mostafa.password_encypted}")
    print(f"   Algorithm: {mostafa.algorithm}")
    print(f"   Key data: {mostafa.key_data}")
except CustomUser.DoesNotExist:
    print(f"\n❌ Utilisateur 'mostafa' n'existe pas!")
    mostafa = None

# Vérifier l'utilisateur ali
try:
    ali = CustomUser.objects.get(username='ali')
    print(f"\n✅ Utilisateur: ali")
    print(f"   Password encrypted: {ali.password_encypted}")
    print(f"   Algorithm: {ali.algorithm}")
    print(f"   Key data: {ali.key_data}")
except CustomUser.DoesNotExist:
    print(f"\n❌ Utilisateur 'ali' n'existe pas!")
    ali = None

print("\n" + "="*60)
print("TEST DES ATTAQUES")
print("="*60)

from backend.cryptotoolbox.attack.attack_runner import run_attack

# Test 1: Attaque sur mostafa avec dictionnaire 012
if mostafa:
    print(f"\n🔍 Test 1: Attaque sur 'mostafa' avec dict_012")
    
    # Charger le dictionnaire
    dict_path = os.path.join(os.path.dirname(__file__), 'backend', 'dictionaries', 'dict_012.txt')
    if os.path.exists(dict_path):
        with open(dict_path, 'r', encoding='utf-8') as f:
            dictionary = [line.strip() for line in f if line.strip()]
        
        print(f"   Dictionnaire: {len(dictionary)} entrées")
        print(f"   Premiers mots: {dictionary[:5]}")
        
        payload = {
            "target_username": "mostafa",
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
            for match in result['matches']:
                print(f"   - ✅ Trouvé: {match['candidate_key'].get('password_candidate', 'N/A')}")
        else:
            print(f"   - ❌ Aucun mot de passe trouvé")
            print(f"   - ⚠️  Le mot de passe chiffré est: {mostafa.password_encypted}")
            print(f"   - Vérifions si un mot du dictionnaire donne ce chiffré...")
            
            from backend.cryptotoolbox.cyphers.caesar import caesar_encrypt
            import json
            
            key_data = mostafa.key_data
            if isinstance(key_data, str):
                key_data = json.loads(key_data)
            if isinstance(key_data, str):
                key_data = json.loads(key_data)
            
            shift = key_data.get('shift', 0)
            print(f"   - Shift utilisé: {shift}")
            
            # Tester les 5 premiers mots du dictionnaire
            print(f"   - Test des premiers mots du dictionnaire:")
            for word in dictionary[:10]:
                # Convertir les chiffres en lettres
                word_as_letters = ''.join([chr(ord('A') + int(c)) for c in word])
                encrypted = caesar_encrypt(word_as_letters, shift)
                match = encrypted == mostafa.password_encypted
                print(f"     {word} → {word_as_letters} → {encrypted} {'✅ MATCH!' if match else ''}")
    else:
        print(f"   ❌ Fichier dictionnaire introuvable: {dict_path}")

# Test 2: Attaque sur ali avec dictionnaire digits6
if ali:
    print(f"\n🔍 Test 2: Attaque sur 'ali' avec dict_digits3")
    
    # Charger le dictionnaire
    dict_path = os.path.join(os.path.dirname(__file__), 'backend', 'dictionaries', 'dict_digits3.txt')
    if os.path.exists(dict_path):
        with open(dict_path, 'r', encoding='utf-8') as f:
            dictionary = [line.strip() for line in f if line.strip()]
        
        print(f"   Dictionnaire: {len(dictionary)} entrées")
        
        # Vérifier le mot de passe chiffré d'ali
        print(f"   Password chiffré d'ali: {ali.password_encypted}")
        
        payload = {
            "target_username": "ali",
            "mode": "dictionary",
            "dictionary": dictionary[:1000],  # Limiter à 1000 pour test rapide
            "max_seconds": 60,
            "limit": 0
        }
        
        result = run_attack(payload)
        print(f"\n   Résultat:")
        print(f"   - Tentatives: {result.get('attempts', 0)}")
        print(f"   - Temps: {result.get('time_sec', 0):.4f}s")
        print(f"   - Matches: {result.get('matches_count', 0)}")
        
        if result.get('matches'):
            for match in result['matches']:
                print(f"   - ✅ Trouvé: {match['candidate_key'].get('password_candidate', 'N/A')}")
        else:
            print(f"   - ❌ Aucun mot de passe trouvé dans les 1000 premières entrées")
            print(f"   - Le mot de passe pourrait être plus loin dans le dictionnaire...")
    else:
        print(f"   ❌ Fichier dictionnaire introuvable: {dict_path}")

print("\n" + "="*60)
