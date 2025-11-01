"""
Créer l'utilisateur avec mot de passe 122 correctement
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crypto_lab.models import CustomUser
from backend.cryptotoolbox import encrypt_with_algorithm
from backend.cryptotoolbox.attack.utils import clean_text
import json

print("="*80)
print(" CRÉATION CORRECTE DE L'UTILISATEUR AVEC MOT DE PASSE 122")
print("="*80)

username = "bellia"
password = "122"
algorithm = "caesar"
shift = 3

print(f"\n1. Configuration:")
print(f"   - Username: {username}")
print(f"   - Password: {password}")
print(f"   - Algorithm: {algorithm}")
print(f"   - Shift: {shift}")

# Supprimer l'ancien utilisateur
CustomUser.objects.filter(username=username).delete()
print(f"\n2. Ancien utilisateur supprimé")

# Convertir le mot de passe
password_converted = clean_text(password)
print(f"\n3. Conversion du mot de passe:")
print(f"   - Original: {password}")
print(f"   - Converti: {password_converted}")

# Chiffrer
encrypted = encrypt_with_algorithm(algorithm, password_converted, {"shift": shift})
print(f"\n4. Chiffrement:")
print(f"   - Plaintext: {password_converted}")
print(f"   - Encrypted: {encrypted}")

# Créer l'utilisateur
user = CustomUser.objects.create(
    username=username,
    password_encypted=encrypted,
    algorithm=algorithm,
    key_data=json.dumps({"shift": shift})
)

print(f"\n5. ✅ Utilisateur créé avec succès!")
print(f"   - ID: {user.id}")
print(f"   - Username: {user.username}")
print(f"   - Password encrypted: {user.password_encypted}")
print(f"   - Algorithm: {user.algorithm}")
print(f"   - Key data: {user.key_data}")

# Vérifier dans la DB
user_check = CustomUser.objects.get(username=username)
print(f"\n6. Vérification en DB:")
print(f"   - Password encrypted: '{user_check.password_encypted}'")
print(f"   - Est vide? {not user_check.password_encypted}")

# Ajouter au dictionnaire si nécessaire
with open('backend/dic.txt', 'r') as f:
    dictionary = [line.strip() for line in f if line.strip()]

if password not in dictionary:
    print(f"\n7. Ajout de '{password}' au dictionnaire...")
    with open('backend/dic.txt', 'a') as f:
        f.write(f'\n{password}')
    print(f"   ✅ Ajouté!")
else:
    print(f"\n7. '{password}' est déjà dans le dictionnaire")

# Ajouter à test_users.txt
with open('test_users.txt', 'r', encoding='utf-8') as f:
    existing = {line.strip() for line in f if line.strip()}

if username not in existing:
    with open('test_users.txt', 'a', encoding='utf-8') as f:
        f.write(f'\n{username}')
    print(f"\n8. '{username}' ajouté à test_users.txt")
else:
    print(f"\n8. '{username}' est déjà dans test_users.txt")

print("\n" + "="*80)
print(" ✅ TERMINÉ - Utilisateur prêt pour l'attaque!")
print("="*80)
print(f"\nPour tester l'attaque, exécutez:")
print(f"  python test_attack_122.py")
