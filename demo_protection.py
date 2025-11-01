#!/usr/bin/env python
"""
Démonstration Interactive du Système de Protection
Ce script montre visuellement comment fonctionne la protection
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crypto_lab.models import CustomUser
from django.utils import timezone
import time

def print_banner():
    print("\n" + "=" * 70)
    print("  🛡️  DÉMONSTRATION DU SYSTÈME DE PROTECTION DES COMPTES  🛡️")
    print("=" * 70 + "\n")

def print_section(title):
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print('─' * 70)

def print_status(user, step=None):
    """Affiche le statut actuel de l'utilisateur"""
    if step:
        print(f"\n[Étape {step}]")
    
    print(f"\n┌{'─' * 68}┐")
    print(f"│ 👤 Utilisateur: {user.username:<52} │")
    print(f"├{'─' * 68}┤")
    print(f"│ 🛡️  Protection: {'🟢 ACTIVÉE' if user.protection_enabled else '🟡 DÉSACTIVÉE':<55} │")
    print(f"│ 📊 Tentatives échouées: {user.failed_login_attempts}/3{' ' * 42} │")
    print(f"│ 🔒 Statut: {'🔴 VERROUILLÉ' if user.is_account_locked() else '🟢 ACTIF':<59} │")
    
    if user.is_account_locked():
        remaining = user.get_lock_remaining_time()
        print(f"│ ⏱️  Temps restant: {remaining} minute(s){' ' * (47 - len(str(remaining)))} │")
    
    print(f"└{'─' * 68}┘")

def simulate_login_attempt(user, password, correct_password, attempt_num):
    """Simule une tentative de connexion"""
    print(f"\n🔑 Tentative #{attempt_num}: password = '{password}'", end='')
    time.sleep(0.5)
    
    if password == correct_password:
        print(" ✅ SUCCÈS!")
        user.reset_failed_attempts()
        return True
    else:
        print(" ❌ ÉCHEC!")
        before = user.failed_login_attempts
        user.record_failed_attempt()
        after = user.failed_login_attempts
        
        if user.is_account_locked():
            print(f"   🔒 COMPTE VERROUILLÉ ! ({before} → {after} tentatives)")
        else:
            print(f"   ⚠️  Tentatives: {before} → {after}/3")
        
        return False

def demo_without_protection():
    """Démo: Attaque sans protection"""
    print_section("PARTIE 1: Attaque SANS Protection")
    
    # Créer ou récupérer utilisateur
    username = 'demo_sans_protection'
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create(
            username=username,
            password_encypted='DEF',  # ABC avec shift 3
            algorithm='caesar',
            key_data={'shift': 3}
        )
    
    # Désactiver la protection
    user.protection_enabled = False
    user.failed_login_attempts = 0
    user.account_locked_until = None
    user.save()
    
    print("\n📝 Configuration:")
    print(f"   • Utilisateur: {username}")
    print(f"   • Mot de passe: ABC (chiffré: DEF)")
    print(f"   • Protection: DÉSACTIVÉE")
    
    print_status(user, "Initiale")
    
    print("\n🎯 Simulation d'une attaque par dictionnaire...")
    print("   L'attaquant teste 10 mots de passe différents:")
    
    passwords = ['AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'FFF', 'GGG', 'HHH', 'III', 'JJJ']
    
    for i, pwd in enumerate(passwords, 1):
        simulate_login_attempt(user, pwd, 'ABC', i)
        time.sleep(0.3)
    
    print_status(user, "Finale")
    
    print("\n💡 OBSERVATION:")
    print("   ⚠️  AUCUNE protection ! L'attaquant peut tenter des milliers de mots")
    print("   ⚠️  de passe sans être bloqué. Les attaques automatisées sont faciles!")
    print(f"   ⚠️  Tentatives échouées: {user.failed_login_attempts} (pas de limite)")

def demo_with_protection():
    """Démo: Attaque avec protection"""
    print_section("PARTIE 2: Attaque AVEC Protection")
    
    # Créer ou récupérer utilisateur
    username = 'demo_avec_protection'
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create(
            username=username,
            password_encypted='DEF',  # ABC avec shift 3
            algorithm='caesar',
            key_data={'shift': 3}
        )
    
    # Activer la protection et réinitialiser
    user.protection_enabled = True
    user.failed_login_attempts = 0
    user.account_locked_until = None
    user.save()
    
    print("\n📝 Configuration:")
    print(f"   • Utilisateur: {username}")
    print(f"   • Mot de passe: ABC (chiffré: DEF)")
    print(f"   • Protection: 🟢 ACTIVÉE (max 3 tentatives)")
    
    print_status(user, "Initiale")
    
    print("\n🎯 Simulation de la même attaque...")
    print("   L'attaquant teste à nouveau des mots de passe:")
    
    passwords = ['AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'FFF', 'GGG', 'HHH', 'III', 'JJJ']
    
    for i, pwd in enumerate(passwords, 1):
        if user.is_account_locked():
            print(f"\n🔒 Tentative #{i}: BLOQUÉE (compte verrouillé)")
            print(f"   ⏱️  Temps restant: {user.get_lock_remaining_time()} minutes")
            time.sleep(0.3)
            if i >= 6:  # Montrer quelques tentatives bloquées
                break
        else:
            simulate_login_attempt(user, pwd, 'ABC', i)
            time.sleep(0.5)
    
    print_status(user, "Finale")
    
    print("\n💡 OBSERVATION:")
    print("   ✅ Protection efficace ! Seulement 3 tentatives autorisées")
    print("   ✅ Compte verrouillé pendant 30 minutes")
    print("   ✅ L'attaquant doit attendre 30 minutes entre chaque série")
    print("   ✅ Une attaque dictionnaire de 1M mots prendrait ~19 ans!")

def demo_successful_login():
    """Démo: Connexion réussie et réinitialisation"""
    print_section("PARTIE 3: Connexion Réussie et Réinitialisation")
    
    # Utiliser l'utilisateur de la démo précédente
    username = 'demo_avec_protection'
    user = CustomUser.objects.get(username=username)
    
    print("\n📝 Situation:")
    print(f"   • Le compte '{username}' est verrouillé")
    print(f"   • L'utilisateur légitime veut se connecter")
    
    print_status(user, "Avant déverrouillage")
    
    print("\n🔓 Déverrouillage manuel (par l'utilisateur ou l'admin)...")
    user.reset_failed_attempts()
    time.sleep(1)
    
    print_status(user, "Après déverrouillage")
    
    print("\n🔑 Tentative de connexion avec le BON mot de passe:")
    success = simulate_login_attempt(user, 'ABC', 'ABC', 1)
    time.sleep(0.5)
    
    print_status(user, "Finale")
    
    print("\n💡 OBSERVATION:")
    print("   ✅ Connexion réussie !")
    print("   ✅ Compteur de tentatives automatiquement réinitialisé à 0")
    print("   ✅ Le compte est à nouveau actif et protégé")
    print("   ✅ L'utilisateur légitime n'est pas pénalisé longtemps")

def demo_comparison():
    """Comparaison des deux systèmes"""
    print_section("PARTIE 4: Comparaison et Impact")
    
    print("\n📊 TEMPS NÉCESSAIRE POUR UNE ATTAQUE PAR DICTIONNAIRE")
    print("\n┌─────────────────────────┬──────────────────┬──────────────────┐")
    print("│ Taille du dictionnaire  │  Sans Protection │  Avec Protection │")
    print("├─────────────────────────┼──────────────────┼──────────────────┤")
    print("│ 1,000 mots              │     ~1 seconde   │     ~5.5 jours   │")
    print("│ 10,000 mots             │    ~10 secondes  │    ~55 jours     │")
    print("│ 100,000 mots            │   ~100 secondes  │    ~1.5 ans      │")
    print("│ 1,000,000 mots          │    ~17 minutes   │    ~19 ans       │")
    print("└─────────────────────────┴──────────────────┴──────────────────┘")
    
    print("\n📊 TENTATIVES PAR UNITÉ DE TEMPS")
    print("\n┌─────────────────────────┬──────────────────┬──────────────────┐")
    print("│ Unité de temps          │  Sans Protection │  Avec Protection │")
    print("├─────────────────────────┼──────────────────┼──────────────────┤")
    print("│ Par seconde             │     ~1,000       │      0.0016      │")
    print("│ Par minute              │    ~60,000       │       0.1        │")
    print("│ Par heure               │ ~3,600,000       │         6        │")
    print("│ Par jour                │~86,400,000       │       144        │")
    print("└─────────────────────────┴──────────────────┴──────────────────┘")
    
    print("\n🎯 RALENTISSEMENT:")
    print("   • Facteur: 625,000x plus lent")
    print("   • De 1000 tentatives/seconde à 0.0016 tentative/seconde")
    print("   • Une attaque de 17 minutes devient une attaque de 19 ans")
    
    print("\n✨ AVANTAGES DE LA PROTECTION:")
    print("   ✅ Ralentit drastiquement les attaques automatisées")
    print("   ✅ Rend les attaques par dictionnaire impraticables")
    print("   ✅ Protège contre la force brute")
    print("   ✅ Alerte sur les tentatives suspectes")
    print("   ✅ Simple à activer/désactiver par l'utilisateur")
    print("   ✅ Déverrouillage manuel disponible")

def main():
    """Fonction principale"""
    print_banner()
    
    print("Cette démonstration va vous montrer:")
    print("  1️⃣  Attaque SANS protection (facile)")
    print("  2️⃣  Attaque AVEC protection (difficile)")
    print("  3️⃣  Connexion réussie et réinitialisation")
    print("  4️⃣  Comparaison et impact sur la sécurité")
    
    input("\n▶️  Appuyez sur Entrée pour commencer...")
    
    # Partie 1: Sans protection
    demo_without_protection()
    input("\n▶️  Appuyez sur Entrée pour continuer...")
    
    # Partie 2: Avec protection
    demo_with_protection()
    input("\n▶️  Appuyez sur Entrée pour continuer...")
    
    # Partie 3: Connexion réussie
    demo_successful_login()
    input("\n▶️  Appuyez sur Entrée pour voir la comparaison...")
    
    # Partie 4: Comparaison
    demo_comparison()
    
    print("\n" + "=" * 70)
    print("  ✅ FIN DE LA DÉMONSTRATION")
    print("=" * 70)
    print("\n💡 Pour utiliser le système:")
    print("   1. Lancez le serveur: python manage.py runserver")
    print("   2. Accédez à l'interface: http://127.0.0.1:8000")
    print("   3. Allez dans l'onglet '🛡️ Protection'")
    print("   4. Activez la protection pour votre compte")
    print("\n📚 Documentation complète: voir GUIDE_PROTECTION.md\n")

if __name__ == '__main__':
    main()
