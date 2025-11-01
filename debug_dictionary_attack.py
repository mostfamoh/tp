"""
Debugger l'attaque par dictionnaire
"""
import os
import sys
import django
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crypto_lab.models import CustomUser
from backend.cryptotoolbox.attack.utils import clean_text

# Récupérer l'utilisateur
user = CustomUser.objects.filter(username='cas1_012').first()

if not user:
    print("❌ Utilisateur non trouvé")
    sys.exit(1)

print("="*80)
print(" DEBUG ATTAQUE DICTIONNAIRE")
print("="*80)

print(f"\nUtilisateur: {user.username}")
print(f"Password encrypted from DB: '{user.password_encypted}'")
print(f"Algorithm: {user.algorithm}")
key_data = json.loads(user.key_data) if isinstance(user.key_data, str) else user.key_data
print(f"Key data: {key_data}")

encrypted = user.password_encypted
algorithm = user.algorithm.lower()
shift = key_data.get('shift')

print(f"\n" + "-"*80)
print("Test du dictionnaire:")
print("-"*80)

dictionary = ['000', '001', '002', '010', '011', '012']

for word in dictionary:
    # Étape 1: Nettoyer le mot
    txt = clean_text(word)
    
    # Étape 2: Chiffrer
    from string import ascii_uppercase
    cipher = ''.join(ascii_uppercase[(ord(ch) - 65 + shift) % 26] for ch in txt)
    
    # Étape 3: Nettoyer le résultat chiffré
    cipher_cleaned = clean_text(cipher)
    
    # Étape 4: Nettoyer le mot de passe chiffré de la DB
    encrypted_cleaned = clean_text(encrypted)
    
    # Étape 5: Comparer
    match = cipher_cleaned == encrypted_cleaned
    
    print(f"\n  Mot: '{word}'")
    print(f"    1. Après clean_text: '{txt}'")
    print(f"    2. Après chiffrement: '{cipher}'")
    print(f"    3. Cipher cleaned: '{cipher_cleaned}'")
    print(f"    4. Encrypted cleaned: '{encrypted_cleaned}'")
    print(f"    5. Match: {match} {'✅ TROUVE' if match else '❌'}")
    
    if match:
        print(f"\n>>> MOT DE PASSE TROUVE: {word}")
        break
