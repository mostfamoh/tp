"""
Script pour corriger les utilisateurs mostafa et ali
en chiffrant correctement leurs mots de passe
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
print("CORRECTION DES UTILISATEURS")
print("="*60)

# Demander les informations pour mostafa
print("\n📝 Configuration de l'utilisateur 'mostafa'")
print("Type de mot de passe: Premier type {0,1,2}³")
password_mostafa = input("Entrez le mot de passe de mostafa (ex: 012, 122, 210): ").strip()

if not password_mostafa:
    password_mostafa = "012"  # Par défaut
    print(f"→ Utilisation du mot de passe par défaut: {password_mostafa}")

# Vérifier que c'est bien du type {0,1,2}
if not all(c in '012' for c in password_mostafa):
    print(f"⚠️  Attention: '{password_mostafa}' contient des chiffres hors de {{0,1,2}}")

# Demander les informations pour ali
print("\n📝 Configuration de l'utilisateur 'ali'")
print("Type de mot de passe: Deuxième type {0-9}ⁿ")
password_ali = input("Entrez le mot de passe d'ali (ex: 123456, 999999): ").strip()

if not password_ali:
    password_ali = "123456"  # Par défaut
    print(f"→ Utilisation du mot de passe par défaut: {password_ali}")

# Vérifier que c'est bien des chiffres
if not password_ali.isdigit():
    print(f"⚠️  Attention: '{password_ali}' n'est pas composé uniquement de chiffres")

print("\n" + "="*60)
print("MISE À JOUR DES UTILISATEURS")
print("="*60)

# Fonction pour mettre à jour un utilisateur
def update_user(username, password, shift=3):
    try:
        user = CustomUser.objects.get(username=username)
        
        # Convertir le mot de passe (chiffres → lettres)
        password_as_letters = ''.join([chr(ord('A') + int(c)) for c in password])
        
        # Chiffrer
        encrypted = caesar_encrypt(password_as_letters, shift)
        
        # Mettre à jour
        user.password_encypted = encrypted
        user.algorithm = 'cesar'
        user.key_data = {'shift': shift}
        user.save()
        
        print(f"\n✅ Utilisateur: {username}")
        print(f"   Password: {password}")
        print(f"   Converti: {password} → {password_as_letters}")
        print(f"   Chiffré: {encrypted}")
        print(f"   Shift: {shift}")
        print(f"   → Sauvegardé dans la base de données!")
        
        return True
    except CustomUser.DoesNotExist:
        print(f"\n❌ Utilisateur '{username}' n'existe pas!")
        print(f"   Voulez-vous le créer? (o/N): ", end='')
        response = input().strip().lower()
        
        if response in ['o', 'oui', 'y', 'yes']:
            # Créer l'utilisateur
            password_as_letters = ''.join([chr(ord('A') + int(c)) for c in password])
            encrypted = caesar_encrypt(password_as_letters, shift)
            
            user = CustomUser.objects.create(
                username=username,
                password_encypted=encrypted,
                algorithm='cesar',
                key_data={'shift': shift}
            )
            
            print(f"   ✅ Utilisateur '{username}' créé avec succès!")
            print(f"      Password chiffré: {encrypted}")
            return True
        else:
            print(f"   → Utilisateur '{username}' non créé")
            return False
    except Exception as e:
        print(f"\n❌ Erreur lors de la mise à jour de '{username}': {e}")
        return False

# Mettre à jour mostafa
update_user('mostafa', password_mostafa, shift=3)

# Mettre à jour ali
update_user('ali', password_ali, shift=3)

print("\n" + "="*60)
print("VÉRIFICATION")
print("="*60)

# Vérifier les utilisateurs
for username in ['mostafa', 'ali']:
    try:
        user = CustomUser.objects.get(username=username)
        print(f"\n✅ {username}:")
        print(f"   Password chiffré: {user.password_encypted}")
        print(f"   Algorithm: {user.algorithm}")
        print(f"   Key data: {user.key_data}")
    except CustomUser.DoesNotExist:
        print(f"\n❌ {username}: N'existe pas")

print("\n" + "="*60)
print("Maintenant vous pouvez tester les attaques!")
print("="*60)
