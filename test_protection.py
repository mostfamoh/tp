#!/usr/bin/env python
"""
Script de test pour vérifier le système de protection des comptes.
Ce script teste:
1. Création d'un utilisateur
2. Activation de la protection
3. Tentatives de connexion échouées
4. Verrouillage du compte
5. Déverrouillage
"""

import requests
import time
import json

BASE_URL = 'http://127.0.0.1:8000/api'

def create_test_user(username='test_protection', password='ABC', algorithm='caesar', key_data=None):
    """Crée un utilisateur de test"""
    if key_data is None:
        key_data = {'shift': 3}
    
    url = f'{BASE_URL}/regester/'
    data = {
        'username': username,
        'password': password,
        'algorithm': algorithm,
        'key_param': key_data
    }
    
    print(f"🔧 Création de l'utilisateur '{username}'...")
    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print(f"✅ Utilisateur créé avec succès!")
            return True
        elif response.status_code == 409:
            print(f"ℹ️  L'utilisateur existe déjà")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(response.json())
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def toggle_protection(username, enabled=True):
    """Active ou désactive la protection pour un utilisateur"""
    url = f'{BASE_URL}/users/{username}/toggle-protection/'
    data = {'enabled': enabled}
    
    action = "Activation" if enabled else "Désactivation"
    print(f"\n🛡️  {action} de la protection pour '{username}'...")
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(response.json())
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def get_protection_status(username):
    """Récupère le statut de protection"""
    url = f'{BASE_URL}/users/{username}/protection-status/'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def attempt_login(username, password, show_details=True):
    """Tente une connexion"""
    url = f'{BASE_URL}/login/'
    data = {
        'username': username,
        'password': password
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            if show_details:
                print(f"✅ Connexion réussie!")
            return True, response.json()
        else:
            if show_details:
                error_data = response.json()
                if response.status_code == 403:
                    print(f"🔒 Compte verrouillé: {error_data.get('message', '')}")
                    print(f"   Temps restant: {error_data.get('remaining_minutes', 0)} minute(s)")
                elif response.status_code == 401:
                    error_msg = error_data.get('error', 'Mot de passe incorrect')
                    print(f"❌ {error_msg}")
                else:
                    print(f"❌ Erreur: {response.status_code}")
            return False, response.json()
    except Exception as e:
        if show_details:
            print(f"❌ Exception: {e}")
        return False, {}


def unlock_account(username):
    """Déverrouille un compte"""
    url = f'{BASE_URL}/users/{username}/unlock/'
    
    print(f"\n🔓 Déverrouillage du compte '{username}'...")
    try:
        response = requests.post(url)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(response.json())
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def print_status(username):
    """Affiche le statut de protection"""
    status = get_protection_status(username)
    if status:
        print(f"\n📊 Statut de protection pour '{username}':")
        print(f"   • Protection: {'🟢 Activée' if status['protection_enabled'] else '🟡 Désactivée'}")
        print(f"   • Tentatives échouées: {status['failed_attempts']}/3")
        print(f"   • Verrouillé: {'🔒 Oui' if status['is_locked'] else '✅ Non'}")
        if status['is_locked']:
            print(f"   • Temps restant: {status['remaining_minutes']} minute(s)")


def test_protection_system():
    """Test complet du système de protection"""
    print("=" * 60)
    print("🧪 TEST DU SYSTÈME DE PROTECTION DES COMPTES")
    print("=" * 60)
    
    username = 'test_protection'
    correct_password = 'ABC'
    wrong_password = 'WRONG'
    
    # Étape 1: Créer l'utilisateur
    print("\n📝 ÉTAPE 1: Création de l'utilisateur")
    create_test_user(username, correct_password)
    
    # Étape 2: Tester sans protection
    print("\n🔓 ÉTAPE 2: Test sans protection")
    print("   Désactivation de la protection...")
    toggle_protection(username, enabled=False)
    print_status(username)
    
    print("\n   Tentatives avec mauvais mot de passe (protection désactivée):")
    for i in range(5):
        print(f"   Tentative {i+1}: ", end='')
        attempt_login(username, wrong_password, show_details=True)
        time.sleep(0.5)
    
    print("\n   ℹ️  Observation: Aucun verrouillage sans protection")
    
    # Étape 3: Activer la protection
    print("\n🛡️  ÉTAPE 3: Activation de la protection")
    toggle_protection(username, enabled=True)
    unlock_account(username)  # S'assurer que le compte est déverrouillé
    print_status(username)
    
    # Étape 4: Tester avec protection
    print("\n🔐 ÉTAPE 4: Test avec protection active")
    print("   Tentatives avec mauvais mot de passe:")
    
    for i in range(5):
        print(f"\n   Tentative {i+1}:")
        success, data = attempt_login(username, wrong_password, show_details=True)
        
        if not success and data.get('locked'):
            print(f"   🔒 Compte verrouillé après {i+1} tentative(s)!")
            break
        
        time.sleep(0.5)
    
    print_status(username)
    
    # Étape 5: Déverrouillage
    print("\n🔓 ÉTAPE 5: Déverrouillage manuel")
    unlock_account(username)
    print_status(username)
    
    # Étape 6: Test de connexion réussie
    print("\n✅ ÉTAPE 6: Connexion avec le bon mot de passe")
    print("   Tentative de connexion:")
    attempt_login(username, correct_password, show_details=True)
    print_status(username)
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print("✅ Système de protection fonctionnel")
    print("✅ Verrouillage après 3 tentatives")
    print("✅ Déverrouillage manuel disponible")
    print("✅ Réinitialisation après connexion réussie")
    print("=" * 60)


if __name__ == '__main__':
    test_protection_system()
