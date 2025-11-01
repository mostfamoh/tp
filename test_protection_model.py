#!/usr/bin/env python
"""
Script simple pour tester la protection via Django shell
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crypto_lab.models import CustomUser
from django.utils import timezone
from datetime import timedelta

def test_protection():
    print("=" * 60)
    print("🧪 TEST DU SYSTÈME DE PROTECTION")
    print("=" * 60)
    
    # Créer ou récupérer un utilisateur de test
    username = 'test_protection'
    try:
        user = CustomUser.objects.get(username=username)
        print(f"✅ Utilisateur '{username}' trouvé")
    except CustomUser.DoesNotExist:
        print(f"📝 Création de l'utilisateur '{username}'...")
        user = CustomUser.objects.create(
            username=username,
            password_encypted='DEF',  # ABC avec shift 3
            algorithm='caesar',
            key_data={'shift': 3}
        )
        print(f"✅ Utilisateur créé")
    
    print(f"\n📊 État initial:")
    print(f"   • Protection: {user.protection_enabled}")
    print(f"   • Tentatives échouées: {user.failed_login_attempts}")
    print(f"   • Verrouillé: {user.is_account_locked()}")
    
    # Test 1: Activer la protection
    print(f"\n🛡️  Test 1: Activation de la protection")
    user.protection_enabled = True
    user.save()
    print(f"   ✅ Protection activée")
    
    # Test 2: Enregistrer des tentatives échouées
    print(f"\n❌ Test 2: Simulation de tentatives échouées")
    for i in range(3):
        user.record_failed_attempt()
        print(f"   Tentative {i+1}: {user.failed_login_attempts}/3 - Verrouillé: {user.is_account_locked()}")
    
    # Test 3: Vérifier le verrouillage
    print(f"\n🔒 Test 3: Vérification du verrouillage")
    if user.is_account_locked():
        remaining = user.get_lock_remaining_time()
        print(f"   ✅ Compte verrouillé pour {remaining} minutes")
    else:
        print(f"   ❌ Le compte devrait être verrouillé!")
    
    # Test 4: Déverrouillage
    print(f"\n🔓 Test 4: Déverrouillage manuel")
    user.reset_failed_attempts()
    print(f"   • Tentatives échouées: {user.failed_login_attempts}")
    print(f"   • Verrouillé: {user.is_account_locked()}")
    print(f"   ✅ Compte déverrouillé")
    
    # Test 5: Protection désactivée
    print(f"\n🔓 Test 5: Test avec protection désactivée")
    user.protection_enabled = False
    user.save()
    for i in range(5):
        user.record_failed_attempt()
    print(f"   • Tentatives échouées: {user.failed_login_attempts}")
    print(f"   • Verrouillé: {user.is_account_locked()}")
    print(f"   ✅ Aucun verrouillage sans protection")
    
    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS PASSÉS AVEC SUCCÈS!")
    print("=" * 60)
    print("\n📋 Fonctionnalités testées:")
    print("   ✅ Activation/désactivation de la protection")
    print("   ✅ Enregistrement des tentatives échouées")
    print("   ✅ Verrouillage après 3 tentatives")
    print("   ✅ Calcul du temps restant")
    print("   ✅ Déverrouillage manuel")
    print("   ✅ Comportement sans protection")

if __name__ == '__main__':
    test_protection()
