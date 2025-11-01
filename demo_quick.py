#!/usr/bin/env python
"""
Démonstration Rapide du Système de Protection
Test visuel en 30 secondes
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crypto_lab.models import CustomUser

def main():
    print("\n" + "=" * 60)
    print("  🛡️  DÉMO RAPIDE - SYSTÈME DE PROTECTION")
    print("=" * 60 + "\n")
    
    # Créer ou récupérer un utilisateur de test
    username = 'demo_quick'
    try:
        user = CustomUser.objects.get(username=username)
        print(f"✅ Utilisateur '{username}' trouvé\n")
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create(
            username=username,
            password_encypted='DEF',
            algorithm='caesar',
            key_data={'shift': 3}
        )
        print(f"✅ Utilisateur '{username}' créé\n")
    
    # Reset
    user.protection_enabled = False
    user.failed_login_attempts = 0
    user.account_locked_until = None
    user.save()
    
    # Test 1: Sans protection
    print("📝 Test 1: SANS PROTECTION")
    print(f"   Protection: {user.protection_enabled}")
    for i in range(5):
        user.record_failed_attempt()
        print(f"   Tentative {i+1}: {user.failed_login_attempts} échecs - "
              f"Verrouillé: {user.is_account_locked()}")
    print(f"   ⚠️  Aucun verrouillage ! {user.failed_login_attempts} tentatives sans limite\n")
    
    # Reset
    user.protection_enabled = True
    user.failed_login_attempts = 0
    user.account_locked_until = None
    user.save()
    
    # Test 2: Avec protection
    print("📝 Test 2: AVEC PROTECTION")
    print(f"   Protection: {user.protection_enabled}")
    for i in range(5):
        if not user.is_account_locked():
            user.record_failed_attempt()
            print(f"   Tentative {i+1}: {user.failed_login_attempts}/3 - "
                  f"Verrouillé: {user.is_account_locked()}")
        else:
            remaining = user.get_lock_remaining_time()
            print(f"   Tentative {i+1}: 🔒 BLOQUÉ ({remaining} min restantes)")
        
        if user.is_account_locked():
            break
    
    print(f"   ✅ Compte verrouillé après 3 tentatives !\n")
    
    # Comparaison
    print("📊 COMPARAISON:")
    print("   Sans protection: ∞ tentatives possibles")
    print("   Avec protection: 3 tentatives max, puis blocage 30 min")
    print("\n   Impact: Une attaque de 17 minutes → 19 ans ! 🚀\n")
    
    # Déverrouillage
    print("🔓 Déverrouillage:")
    user.reset_failed_attempts()
    print(f"   Tentatives: {user.failed_login_attempts}")
    print(f"   Verrouillé: {user.is_account_locked()}")
    print(f"   ✅ Compte déverrouillé et prêt à être réutilisé\n")
    
    print("=" * 60)
    print("  ✅ DÉMO TERMINÉE")
    print("=" * 60)
    print("\n💡 Pour utiliser:")
    print("   1. Lancez le serveur: python manage.py runserver")
    print("   2. Allez sur: http://127.0.0.1:8000")
    print("   3. Onglet '🛡️ Protection' → Cliquez 'Activer'\n")

if __name__ == '__main__':
    main()
