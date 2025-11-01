#!/usr/bin/env python
"""
Script de diagnostic pour le problème de login
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crypto_lab.models import CustomUser
from backend.cryptotoolbox import decrypt_with_algorithm

def diagnose_login_issue():
    print("\n" + "=" * 70)
    print("  🔍 DIAGNOSTIC DU PROBLÈME DE LOGIN")
    print("=" * 70 + "\n")
    
    # Trouver des utilisateurs de test
    users = CustomUser.objects.all()[:5]
    
    if not users:
        print("❌ Aucun utilisateur trouvé dans la base de données")
        return
    
    print(f"📋 Utilisateurs trouvés: {users.count()}\n")
    
    for user in users:
        print(f"\n{'─' * 70}")
        print(f"👤 Utilisateur: {user.username}")
        print(f"   Algorithme: {user.algorithm}")
        print(f"   Clé: {user.key_data}")
        print(f"   Mot de passe chiffré: {user.password_encypted}")
        
        try:
            # Déchiffrer le mot de passe
            algo = user.algorithm.lower()
            if algo == 'cesar':
                algo = 'caesar'
            elif algo == 'plaiyfair':
                algo = 'playfair'
            
            decrypted = decrypt_with_algorithm(algo, user.password_encypted, user.key_data)
            print(f"   Mot de passe déchiffré: {decrypted}")
            
            # Vérifier si c'est un mot de passe numérique converti
            has_letters_abcdefghij = any(c in 'ABCDEFGHIJ' for c in decrypted)
            print(f"   Contient A-J (conversion numérique): {has_letters_abcdefghij}")
            
            # Si c'est une conversion numérique, montrer l'original
            if has_letters_abcdefghij and all(c in 'ABCDEFGHIJ' for c in decrypted):
                numeric_version = ''.join([str(ord(c) - ord('A')) for c in decrypted])
                print(f"   ⚠️  Mot de passe original probable: {numeric_version}")
                print(f"   💡 Pour se connecter, utiliser: {numeric_version}")
            
        except Exception as e:
            print(f"   ❌ Erreur de déchiffrement: {e}")
    
    print("\n" + "=" * 70)
    print("  💡 SOLUTION")
    print("=" * 70)
    print("\nLe problème vient de la conversion des chiffres en lettres.")
    print("Lors du LOGIN, le mot de passe doit AUSSI être converti.")
    print("\nExemple:")
    print("  • Vous entrez: 123")
    print("  • Doit être converti en: BCD")
    print("  • Puis comparé avec le mot de passe déchiffré")
    print("\n")

if __name__ == '__main__':
    diagnose_login_issue()
